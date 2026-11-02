"""Views de aluguéis: registro com prévia (P07, D13), histórico (P08), devolução (P09)."""

import json
import re
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest import mock

from django.contrib import admin
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse

from alugueis import services
from alugueis.models import Aluguel, Situacao
from alugueis.tests.test_devolucao_e_previa import registrar_no_passado
from clientes.validadores import formatar_cpf
from config import mensagens
from config.tests.fabricas import (
    cpf_valido,
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    dias,
    encerrar,
    hoje,
    registrar,
)
from equipamentos.models import Equipamento

URL_CRIAR = "/alugueis/novo/"
URL_HISTORICO = "/alugueis/"


def _url_devolver(aluguel) -> str:
    return reverse("alugueis:devolver", args=[aluguel.pk])


def _iso(data: date) -> str:
    return data.isoformat()


class ComFuncionario(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def _erros(self, resposta) -> dict:
        self.assertEqual(resposta.status_code, 200)
        return resposta.context["form"].errors


class RegistroTests(ComFuncionario):
    def setUp(self):
        super().setUp()
        self.cliente = criar_cliente(
            nome_completo="Maria Fictícia", cpf=cpf_valido("390533447")
        )
        self.equipamento = criar_equipamento(
            codigo="FUR-01", nome="Furadeira", valor_diaria=Decimal("50.00")
        )

    def _post(self, **campos):
        dados = {
            "cliente": self.cliente.pk,
            "equipamento": self.equipamento.pk,
            "data_retirada": _iso(hoje()),
            "data_devolucao_prevista": _iso(dias(2)),
            "acao": "registrar",  # confirmação explícita (sem ela, nada é gravado)
        }
        dados.update(campos)
        return self.client.post(URL_CRIAR, dados)

    def test_get_contexto_do_contrato(self):
        inativo = criar_equipamento(codigo="INA-01", ativo=False)
        alugado = criar_equipamento(codigo="ALU-01")
        registrar(equipamento=alugado)
        resposta = self.client.get(URL_CRIAR)
        self.assertTemplateUsed(resposta, "alugueis/formulario.html")
        contexto = resposta.context
        self.assertEqual(
            (contexto["data_atual"], contexto["data_minima"]), (hoje(), hoje())
        )
        self.assertFalse(contexto["sem_clientes"])
        self.assertFalse(contexto["sem_equipamentos_disponiveis"])
        self.assertIsNone(contexto["resumo"])
        opcoes = list(contexto["form"].fields["equipamento"].queryset)
        self.assertEqual(opcoes, [self.equipamento])
        self.assertNotIn(inativo, opcoes)
        self.assertEqual(
            contexto["diarias_equipamentos"], {str(self.equipamento.pk): "50.00"}
        )
        script = re.search(
            r'<script id="diarias-equipamentos" type="application/json">(.*?)</script>',
            resposta.content.decode(),
        )
        dados_json = json.loads(script.group(1))
        self.assertEqual(dados_json, {str(self.equipamento.pk): "50.00"})
        self.assertContains(resposta, "não pode ser cancelado")

    def test_selecao_mostra_nome_cpf_mascarado_e_diaria(self):
        resposta = self.client.get(URL_CRIAR)
        self.assertContains(resposta, "Maria Fictícia — CPF ***.533.447-**")
        self.assertNotContains(resposta, formatar_cpf(self.cliente.cpf))
        self.assertNotContains(resposta, self.cliente.cpf)
        self.assertContains(resposta, "FUR-01 — Furadeira (R$ 50,00/dia)")

    def test_sem_clientes_ou_sem_equipamentos(self):
        Equipamento.objects.filter(pk=self.equipamento.pk).update(ativo=False)
        contexto = self.client.get(URL_CRIAR).context
        self.assertTrue(contexto["sem_equipamentos_disponiveis"])
        self.assertFalse(contexto["sem_clientes"])
        self.cliente.delete()
        self.assertTrue(self.client.get(URL_CRIAR).context["sem_clientes"])

    def test_previa_calcula_no_servidor_e_nao_grava(self):
        resposta = self._post(acao="previa")
        resumo = resposta.context["resumo"]
        self.assertEqual(
            (resumo.quantidade_diarias, resumo.valor_diaria, resumo.valor_previsto),
            (3, Decimal("50.00"), Decimal("150.00")),
        )
        self.assertContains(resposta, "Total previsto: R$ 150,00")
        self.assertFalse(Aluguel.objects.exists())
        self.assertTrue(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)

    def test_registro_redireciona_ao_historico_com_valores_do_backend(self):
        resposta = self._post(acao="registrar")
        self.assertRedirects(resposta, URL_HISTORICO, fetch_redirect_response=False)
        aluguel = Aluguel.objects.get()
        self.assertEqual(
            (
                aluguel.quantidade_diarias,
                aluguel.valor_diaria_contratada,
                aluguel.valor_contratado,
            ),
            (3, Decimal("50.00"), Decimal("150.00")),
        )
        self.assertTrue(aluguel.aberto)

    def test_retirada_hoje_futura_e_mesmo_dia(self):
        casos = [(hoje(), hoje(), 1), (dias(5), dias(5), 1), (dias(5), dias(9), 5)]
        for retirada, prevista, diarias in casos:
            with self.subTest(retirada=retirada, prevista=prevista):
                Aluguel.objects.all().delete()
                self._post(
                    data_retirada=_iso(retirada), data_devolucao_prevista=_iso(prevista)
                )
                aluguel = Aluguel.objects.get()
                self.assertEqual(aluguel.quantidade_diarias, diarias)
                self.assertEqual(aluguel.valor_contratado, Decimal("50.00") * diarias)
                # Indisponível já no registro, mesmo com retirada futura (I1).
                self.assertFalse(
                    Equipamento.objects.get(pk=self.equipamento.pk).disponivel
                )

    def test_datas_invalidas(self):
        erros = self._erros(self._post(data_retirada=_iso(dias(-1))))
        self.assertEqual(erros["data_retirada"], [mensagens.RETIRADA_NO_PASSADO])
        erros = self._erros(self._post(data_devolucao_prevista=_iso(dias(-1))))
        self.assertEqual(
            erros["data_devolucao_prevista"], [mensagens.PREVISTA_ANTES_DA_RETIRADA]
        )
        erros = self._erros(
            self._post(data_retirada="", data_devolucao_prevista="31/02/2026")
        )
        self.assertEqual(erros["data_retirada"], [mensagens.CAMPO_OBRIGATORIO])
        self.assertIn("data_devolucao_prevista", erros)
        self.assertFalse(Aluguel.objects.exists())

    def test_equipamento_indisponivel_inativo_ou_inexistente(self):
        alugado = criar_equipamento()
        registrar(equipamento=alugado)
        reservado = criar_equipamento()
        registrar(equipamento=reservado, retirada=dias(10), prevista=dias(11))
        inativo = criar_equipamento(ativo=False)
        for pk in (alugado.pk, reservado.pk, inativo.pk, 999):
            with self.subTest(pk=pk):
                erros = self._erros(self._post(equipamento=pk))
                self.assertEqual(
                    erros["equipamento"], [mensagens.EQUIPAMENTO_INDISPONIVEL]
                )
        self.assertEqual(Aluguel.objects.count(), 2)

    def test_cliente_inexistente_e_campos_obrigatorios(self):
        erros = self._erros(self._post(cliente=999))
        self.assertEqual(erros["cliente"], [mensagens.CLIENTE_INEXISTENTE])
        erros = self._erros(self._post(cliente="", equipamento=""))
        self.assertEqual(erros["cliente"], [mensagens.CAMPO_OBRIGATORIO])
        self.assertEqual(erros["equipamento"], [mensagens.CAMPO_OBRIGATORIO])
        self.assertFalse(Aluguel.objects.exists())

    def test_valores_financeiros_manipulados_sao_ignorados(self):
        self._post(
            valor_diaria_contratada="1.00",
            valor_contratado="0.01",
            quantidade_diarias="99",
            data_devolucao_real=_iso(hoje()),
            id="999",
        )
        aluguel = Aluguel.objects.get()
        self.assertEqual(
            (
                aluguel.valor_diaria_contratada,
                aluguel.quantidade_diarias,
                aluguel.valor_contratado,
            ),
            (Decimal("50.00"), 3, Decimal("150.00")),
        )
        self.assertIsNone(aluguel.data_devolucao_real)
        self.assertNotEqual(aluguel.pk, 999)

    def test_corrida_entre_validacao_e_registro_vira_erro_de_campo(self):
        """O formulário viu o equipamento disponível; o serviço, já não."""
        original = services.registrar_aluguel

        def outro_funcionario_alugou_antes(**dados):
            registrar(equipamento=self.equipamento)
            return original(**dados)

        with mock.patch.object(
            services, "registrar_aluguel", outro_funcionario_alugou_antes
        ):
            erros = self._erros(self._post())
        self.assertEqual(erros["equipamento"], [mensagens.EQUIPAMENTO_INDISPONIVEL])
        self.assertEqual(Aluguel.objects.count(), 1)

    def test_data_atual_em_america_recife(self):
        """01h30 UTC de 03/11 ainda é 02/11 em Recife (UTC−3)."""
        instante = datetime(2026, 11, 3, 1, 30, tzinfo=UTC)
        with mock.patch("django.utils.timezone.now", return_value=instante):
            contexto = self.client.get(URL_CRIAR).context
            self.assertEqual(contexto["data_atual"], date(2026, 11, 2))
            resposta = self._post(
                data_retirada="2026-11-02", data_devolucao_prevista="2026-11-02"
            )
        self.assertRedirects(resposta, URL_HISTORICO, fetch_redirect_response=False)
        self.assertEqual(Aluguel.objects.get().data_retirada, date(2026, 11, 2))


class HistoricoTests(ComFuncionario):
    def _historico(self):
        resposta = self.client.get(URL_HISTORICO)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "alugueis/historico.html")
        return resposta

    def test_vazio(self):
        resposta = self._historico()
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_quatro_situacoes_e_devolucao_so_quando_permitida(self):
        ativo = registrar(
            equipamento=criar_equipamento(codigo="ATV-01"), prevista=dias(2)
        )
        atrasado = registrar_no_passado(criar_equipamento(codigo="ATR-01"), 5, 2)
        encerrado = encerrar(
            registrar_no_passado(criar_equipamento(codigo="ENC-01"), 6, 3), dias(-4)
        )
        com_atraso = encerrar(
            registrar_no_passado(criar_equipamento(codigo="ECA-01"), 7, 5), dias(-1)
        )
        futuro = registrar(
            equipamento=criar_equipamento(codigo="FUT-01"),
            retirada=dias(3),
            prevista=dias(4),
        )
        resposta = self._historico()
        linhas = {a.pk: a for a in resposta.context["object_list"]}
        esperado = {
            ativo.pk: (Situacao.ATIVO, True),
            atrasado.pk: (Situacao.ATRASADO, True),
            encerrado.pk: (Situacao.ENCERRADO, False),
            com_atraso.pk: (Situacao.ENCERRADO_COM_ATRASO, False),
            futuro.pk: (Situacao.ATIVO, False),
        }
        for pk, (situacao, pode_devolver) in esperado.items():
            with self.subTest(pk=pk):
                self.assertEqual(linhas[pk].situacao_codigo(), situacao)
                self.assertEqual(linhas[pk].pode_devolver(), pode_devolver)
        for texto in ("Ativo", "Atrasado", "Encerrado", "Encerrado com atraso"):
            self.assertContains(resposta, f">{texto}</td>")
        self.assertContains(resposta, reverse("alugueis:devolver", args=[ativo.pk]))
        self.assertContains(resposta, reverse("alugueis:devolver", args=[atrasado.pk]))
        self.assertNotContains(
            resposta, reverse("alugueis:devolver", args=[encerrado.pk])
        )
        self.assertNotContains(resposta, reverse("alugueis:devolver", args=[futuro.pk]))

    def test_campos_valores_congelados_e_equipamento_inativo(self):
        equipamento = criar_equipamento(
            codigo="FUR-01", nome="Furadeira", valor_diaria=Decimal("1500.00")
        )
        cliente = criar_cliente(nome_completo="Cliente do Histórico")
        aluguel = encerrar(
            registrar(equipamento=equipamento, cliente=cliente, prevista=dias(1)),
            hoje(),
        )
        Equipamento.objects.filter(pk=equipamento.pk).update(
            ativo=False, valor_diaria=Decimal("9.99")
        )
        resposta = self._historico()
        self.assertEqual(list(resposta.context["object_list"]), [aluguel])
        for texto in (
            "Cliente do Histórico",
            "FUR-01 — Furadeira (inativo)",
            hoje().strftime("%d/%m/%Y"),
            dias(1).strftime("%d/%m/%Y"),
            "R$ 1.500,00",
            "R$ 3.000,00",
        ):
            self.assertContains(resposta, texto)
        self.assertNotContains(resposta, "9,99")

    def test_ordem_do_mais_recente_e_sem_consulta_por_linha(self):
        antigo = registrar_no_passado(criar_equipamento(), 9, 8)
        recente = registrar(
            equipamento=criar_equipamento(), retirada=dias(2), prevista=dias(3)
        )
        meio = registrar(equipamento=criar_equipamento())
        with self.assertNumQueries(3) as poucos:  # sessão, usuário e a lista
            resposta = self._historico()
        self.assertEqual(
            [a.pk for a in resposta.context["object_list"]],
            [recente.pk, meio.pk, antigo.pk],
        )
        for _ in range(5):
            encerrar(registrar(equipamento=criar_equipamento()))
        with self.assertNumQueries(len(poucos.captured_queries)):
            self._historico()


class DevolucaoTests(ComFuncionario):
    def setUp(self):
        super().setUp()
        self.equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))

    def test_get_contexto_do_contrato(self):
        aluguel = registrar_no_passado(self.equipamento, 3, 1)
        resposta = self.client.get(_url_devolver(aluguel))
        self.assertTemplateUsed(resposta, "alugueis/devolver.html")
        contexto = resposta.context
        self.assertEqual(contexto["object"], aluguel)
        self.assertTrue(contexto["pode_devolver"])
        self.assertEqual(
            (contexto["data_atual"], contexto["data_minima"], contexto["data_maxima"]),
            (hoje(), dias(-3), hoje()),
        )
        self.assertEqual(contexto["form"]["data_devolucao_real"].value(), hoje())
        self.assertContains(resposta, f'min="{_iso(dias(-3))}"')
        self.assertContains(resposta, f'max="{_iso(hoje())}"')

    def test_devolucao_hoje_libera_equipamento(self):
        aluguel = registrar(equipamento=self.equipamento, prevista=dias(2))
        resposta = self.client.post(
            _url_devolver(aluguel), {"data_devolucao_real": _iso(hoje())}
        )
        self.assertRedirects(resposta, URL_HISTORICO, fetch_redirect_response=False)
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, hoje())
        self.assertEqual(aluguel.valor_contratado, Decimal("150.00"))
        self.assertTrue(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)

    def test_datas_invalidas_nao_gravam(self):
        aluguel = registrar_no_passado(self.equipamento, 2, 1)
        casos = {
            _iso(dias(-3)): mensagens.DEVOLUCAO_ANTES_DA_RETIRADA,
            _iso(dias(1)): mensagens.DEVOLUCAO_FUTURA,
            "": mensagens.CAMPO_OBRIGATORIO,
        }
        for valor, mensagem in casos.items():
            with self.subTest(valor=valor):
                resposta = self.client.post(
                    _url_devolver(aluguel), {"data_devolucao_real": valor}
                )
                self.assertEqual(
                    self._erros(resposta)["data_devolucao_real"], [mensagem]
                )
        aluguel.refresh_from_db()
        self.assertTrue(aluguel.aberto)

    def test_segunda_devolucao_recusada(self):
        aluguel = encerrar(registrar_no_passado(self.equipamento, 3, 1), dias(-1))
        resposta = self.client.get(_url_devolver(aluguel))
        self.assertFalse(resposta.context["pode_devolver"])
        self.assertContains(resposta, mensagens.ALUGUEL_ENCERRADO)
        resposta = self.client.post(
            _url_devolver(aluguel), {"data_devolucao_real": _iso(hoje())}
        )
        self.assertEqual(
            self._erros(resposta)["__all__"], [mensagens.ALUGUEL_ENCERRADO]
        )
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, dias(-1))

    def test_retirada_futura(self):
        aluguel = registrar(
            equipamento=self.equipamento, retirada=dias(2), prevista=dias(3)
        )
        resposta = self.client.get(_url_devolver(aluguel))
        self.assertFalse(resposta.context["pode_devolver"])
        resposta = self.client.post(
            _url_devolver(aluguel), {"data_devolucao_real": _iso(hoje())}
        )
        self.assertEqual(
            self._erros(resposta)["data_devolucao_real"],
            [mensagens.DEVOLUCAO_ANTES_DA_RETIRADA],
        )
        aluguel.refresh_from_db()
        self.assertTrue(aluguel.aberto)

    def test_inexistente_retorna_404(self):
        url = reverse("alugueis:devolver", args=[999])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.post(url, {"data_devolucao_real": _iso(hoje())}).status_code,
            404,
        )


class SegurancaTests(TestCase):
    def setUp(self):
        self.equipamento = criar_equipamento()
        self.cliente = criar_cliente()
        self.aluguel = registrar(equipamento=criar_equipamento(), prevista=dias(1))
        self.dados = {
            "cliente": self.cliente.pk,
            "equipamento": self.equipamento.pk,
            "data_retirada": _iso(hoje()),
            "data_devolucao_prevista": _iso(hoje()),
            "data_devolucao_real": _iso(hoje()),
            "acao": "registrar",
        }

    def _estado(self):
        return list(
            Aluguel.objects.order_by("pk").values_list("pk", "data_devolucao_real")
        )

    def test_login_obrigatorio(self):
        antes = self._estado()
        for url in (URL_HISTORICO, URL_CRIAR, _url_devolver(self.aluguel)):
            with self.subTest(url=url, metodo="GET"):
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
        for url in (URL_CRIAR, _url_devolver(self.aluguel)):
            with self.subTest(url=url, metodo="POST"):
                resposta = self.client.post(url, self.dados)
                self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self._estado(), antes)

    def test_csrf_obrigatorio(self):
        cliente_http = Client(enforce_csrf_checks=True)
        cliente_http.force_login(criar_funcionario())
        antes = self._estado()
        for url in (URL_CRIAR, _url_devolver(self.aluguel)):
            with self.subTest(url=url):
                self.assertEqual(cliente_http.post(url, self.dados).status_code, 403)
        self.assertEqual(self._estado(), antes)

    def test_metodos_nao_permitidos(self):
        self.client.force_login(criar_funcionario())
        casos = [
            ("post", URL_HISTORICO),
            ("put", URL_CRIAR),
            ("delete", _url_devolver(self.aluguel)),
            ("patch", _url_devolver(self.aluguel)),
        ]
        for metodo, url in casos:
            with self.subTest(metodo=metodo, url=url):
                self.assertEqual(getattr(self.client, metodo)(url).status_code, 405)
        self.assertEqual(Aluguel.objects.count(), 1)

    def test_sem_cancelamento_nem_edicao_de_aluguel(self):
        for nome in ("editar", "cancelar", "excluir", "detalhe"):
            with self.subTest(nome=nome):
                with self.assertRaises(NoReverseMatch):
                    reverse(f"alugueis:{nome}", args=[self.aluguel.pk])
        self.assertFalse(admin.site.is_registered(Aluguel))

    def test_devolucao_nao_aceita_outro_aluguel_pelo_post(self):
        self.client.force_login(criar_funcionario())
        outro = registrar(equipamento=self.equipamento, prevista=dias(1))
        self.client.post(
            _url_devolver(self.aluguel),
            {"data_devolucao_real": _iso(hoje()), "aluguel": outro.pk, "id": outro.pk},
        )
        outro.refresh_from_db()
        self.aluguel.refresh_from_db()
        self.assertTrue(outro.aberto)
        self.assertFalse(self.aluguel.aberto)
