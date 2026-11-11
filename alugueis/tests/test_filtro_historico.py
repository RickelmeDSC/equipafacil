"""Filtro do histórico de aluguéis por situação (RF010, RN004).

Complementa CT19 e CT20 (``test_cenarios_ct.py``): o filtro no banco segue a
mesma regra de ``Aluguel.situacao_codigo`` nos limites de data, valor
desconhecido vale "Todas", a ordem do RF008 é mantida, os estados vazios, a
data atual em America/Recife, leitura sem gravação, consultas e autenticação.
"""

from datetime import UTC, date, datetime
from unittest import mock

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from alugueis import services
from alugueis.models import Aluguel, Situacao
from alugueis.tests.test_devolucao_e_previa import registrar_no_passado
from config import mensagens
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    dias,
    encerrar,
    hoje,
    registrar,
)

ROTULOS = ("Todas", "Ativo", "Atrasado", "Encerrado", "Encerrado com atraso")


def _url_historico() -> str:
    return reverse("alugueis:historico")


def _um_de_cada() -> dict[str, list[Aluguel]]:
    """Aluguéis nos limites de cada situação, relativos à data atual em Recife."""
    eq = criar_equipamento
    return {
        Situacao.ATIVO: [
            registrar(equipamento=eq(codigo="ATV-HOJE"), prevista=hoje()),
            registrar(
                equipamento=eq(codigo="ATV-FUT"), retirada=dias(3), prevista=dias(4)
            ),
        ],
        Situacao.ATRASADO: [registrar_no_passado(eq(codigo="ATR-ONTEM"), 3, 1)],
        Situacao.ENCERRADO: [
            encerrar(registrar_no_passado(eq(codigo="ENC-PRAZO"), 4, 0), hoje()),
            encerrar(registrar_no_passado(eq(codigo="ENC-ANTES"), 6, 1), dias(-3)),
        ],
        Situacao.ENCERRADO_COM_ATRASO: [
            encerrar(registrar_no_passado(eq(codigo="ECA-UM-DIA"), 5, 2), dias(-1)),
        ],
    }


class NaSituacaoQuerySetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.por_situacao = _um_de_cada()
        cls.todos = [a for lista in cls.por_situacao.values() for a in lista]

    def test_cada_situacao_traz_exatamente_os_seus_alugueis(self):
        for codigo, esperados in self.por_situacao.items():
            with self.subTest(situacao=codigo):
                self.assertEqual(
                    set(Aluguel.objects.na_situacao(codigo, hoje())), set(esperados)
                )

    def test_mesma_regra_de_situacao_codigo_em_outras_datas(self):
        for data in (dias(-5), dias(-1), hoje(), dias(1), dias(10)):
            for codigo in Situacao.values:
                with self.subTest(data=data, situacao=codigo):
                    esperado = {
                        a.pk for a in self.todos if a.situacao_codigo(data) == codigo
                    }
                    obtido = set(
                        Aluguel.objects.na_situacao(codigo, data).values_list(
                            "pk", flat=True
                        )
                    )
                    self.assertEqual(obtido, esperado)

    def test_situacoes_sao_disjuntas_e_cobrem_o_historico(self):
        vistos = []
        for codigo in Situacao.values:
            vistos += list(
                Aluguel.objects.na_situacao(codigo, hoje()).values_list("pk", flat=True)
            )
        self.assertCountEqual(vistos, [a.pk for a in self.todos])

    def test_situacao_desconhecida_e_recusada_no_queryset(self):
        for codigo in ("", "todas", "ATIVO", "cancelado"):
            with self.subTest(codigo=codigo), self.assertRaises(ValueError):
                Aluguel.objects.na_situacao(codigo, hoje())


class FiltroNoHistoricoTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def _historico(self, **params):
        resposta = self.client.get(_url_historico(), params)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "alugueis/historico.html")
        return resposta

    def _pks(self, resposta) -> list[int]:
        return [a.pk for a in resposta.context["object_list"]]

    def test_cada_situacao_na_tela_com_a_opcao_selecionada(self):
        por_situacao = _um_de_cada()
        for situacao, esperados in por_situacao.items():
            codigo = str(situacao)
            with self.subTest(situacao=codigo):
                resposta = self._historico(situacao=codigo)
                self.assertCountEqual(self._pks(resposta), [a.pk for a in esperados])
                self.assertEqual(resposta.context["situacao_selecionada"], codigo)
                rotulo = situacao.label
                self.assertContains(
                    resposta, f'<option value="{codigo}" selected>{rotulo}</option>'
                )
                self.assertContains(resposta, f">{rotulo}</td>")
                for outro in Situacao:
                    if outro != codigo:
                        self.assertNotContains(resposta, f">{outro.label}</td>")
                self.assertContains(resposta, f'href="{_url_historico()}">Limpar</a>')

    def test_filtro_mantem_a_ordem_do_historico(self):
        antigo = registrar_no_passado(criar_equipamento(), 9, 0)
        futuro = registrar(
            equipamento=criar_equipamento(), retirada=dias(2), prevista=dias(3)
        )
        de_hoje = registrar(equipamento=criar_equipamento())
        encerrar(registrar(equipamento=criar_equipamento()))
        resposta = self._historico(situacao=Situacao.ATIVO)
        self.assertEqual(self._pks(resposta), [futuro.pk, de_hoje.pk, antigo.pk])

    def test_todas_vazio_ou_desconhecido_equivalem_ao_historico_sem_filtro(self):
        _um_de_cada()
        sem_filtro = self._pks(self._historico())
        self.assertEqual(len(sem_filtro), 6)
        for valor in ("", "todas", "Todas", "ATIVO", "cancelado", "ativo;--", " "):
            with self.subTest(valor=valor):
                resposta = self._historico(situacao=valor)
                self.assertEqual(self._pks(resposta), sem_filtro)
                self.assertEqual(resposta.context["situacao_selecionada"], "")
                self.assertContains(
                    resposta, '<option value="" selected>Todas</option>'
                )
                self.assertNotContains(resposta, "Limpar")

    def test_opcoes_do_filtro(self):
        resposta = self._historico()
        self.assertEqual(
            [rotulo for _, rotulo in resposta.context["opcoes_situacao"]], list(ROTULOS)
        )
        self.assertContains(resposta, 'name="situacao"')
        for valor, rotulo in resposta.context["opcoes_situacao"]:
            self.assertContains(resposta, f'value="{valor}"')
            self.assertContains(resposta, f">{rotulo}</option>")

    def test_filtro_mantem_registrar_devolucao_nos_abertos(self):
        atrasado = registrar_no_passado(criar_equipamento(), 4, 2)
        resposta = self._historico(situacao=Situacao.ATRASADO)
        self.assertEqual(self._pks(resposta), [atrasado.pk])
        self.assertContains(resposta, reverse("alugueis:devolver", args=[atrasado.pk]))

    def test_historico_vazio_sem_filtro_mantem_a_orientacao(self):
        resposta = self._historico()
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
        self.assertContains(resposta, "Registre o primeiro aluguel")
        self.assertNotContains(resposta, "Limpar filtro")

    def test_historico_vazio_com_filtro_oferece_limpar(self):
        for codigo in Situacao.values:
            with self.subTest(situacao=codigo):
                resposta = self._historico(situacao=codigo)
                self.assertEqual(self._pks(resposta), [])
                self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
                self.assertContains(resposta, "Limpar filtro")
                self.assertNotContains(resposta, "Registre o primeiro aluguel")
                self.assertNotContains(resposta, "<tbody>")
                self.assertNotContains(resposta, "R$")

    def test_situacao_pela_data_atual_em_america_recife(self):
        """01h30 UTC de 03/11 ainda é 02/11 em Recife: prevista 02/11 está ativo."""
        aluguel = services.registrar_aluguel(
            cliente_id=criar_cliente().pk,
            equipamento_id=criar_equipamento().pk,
            data_retirada=date(2026, 11, 1),
            data_devolucao_prevista=date(2026, 11, 2),
            hoje=date(2026, 11, 1),
        )
        instante = datetime(2026, 11, 3, 1, 30, tzinfo=UTC)
        with mock.patch("django.utils.timezone.now", return_value=instante):
            ativos = self._historico(situacao=Situacao.ATIVO)
            atrasados = self._historico(situacao=Situacao.ATRASADO)
        self.assertEqual(self._pks(ativos), [aluguel.pk])
        self.assertEqual(self._pks(atrasados), [])

    def test_filtro_so_le_o_banco_e_nao_altera_alugueis(self):
        _um_de_cada()
        antes = list(Aluguel.objects.order_by("pk").values())
        with CaptureQueriesContext(connection) as consultas:
            for valor in ("", *Situacao.values, "desconhecida"):
                self._historico(situacao=valor)
        self.assertTrue(consultas.captured_queries)
        for consulta in consultas.captured_queries:
            with self.subTest(sql=consulta["sql"]):
                self.assertTrue(consulta["sql"].lstrip().upper().startswith("SELECT"))
        self.assertEqual(list(Aluguel.objects.order_by("pk").values()), antes)

    def test_filtro_sem_consulta_por_linha(self):
        registrar(equipamento=criar_equipamento())
        with self.assertNumQueries(3):  # sessão, usuário e a lista
            self._historico(situacao=Situacao.ATIVO)
        for _ in range(5):
            registrar(equipamento=criar_equipamento())
        with self.assertNumQueries(3):
            self._historico(situacao=Situacao.ATIVO)


class FiltroComAutenticacaoTests(TestCase):
    def test_anonimo_e_redirecionado_sem_ver_alugueis(self):
        registrar(equipamento=criar_equipamento(nome="Betoneira Secreta"))
        for valor in ("", Situacao.ATIVO, "desconhecida"):
            with self.subTest(valor=valor):
                resposta = self.client.get(_url_historico(), {"situacao": valor})
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
                self.assertNotIn(b"Betoneira", resposta.content)

    def test_filtro_nao_aceita_post(self):
        funcionario = criar_funcionario()
        self.client.force_login(funcionario)
        resposta = self.client.post(_url_historico(), {"situacao": Situacao.ATIVO})
        self.assertEqual(resposta.status_code, 405)
