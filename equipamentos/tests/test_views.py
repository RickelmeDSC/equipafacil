"""Views de equipamentos: cadastro, consulta, edição, ações e segurança (P02–P04)."""

from decimal import Decimal
from unittest import mock

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from alugueis.models import Aluguel
from config import mensagens
from config.tests.fabricas import (
    criar_equipamento,
    criar_funcionario,
    dias,
    encerrar,
    registrar,
)
from equipamentos.models import Categoria, Equipamento

POST_VALIDO = {
    "codigo": "FUR-01",
    "nome": "Furadeira",
    "categoria": Categoria.FERRAMENTAS,
    "descricao": "",
    "valor_diaria": "35,50",
}


def _url(nome: str, equipamento: Equipamento | None = None) -> str:
    args = [equipamento.pk] if equipamento else []
    return reverse(f"equipamentos:{nome}", args=args)


class ComFuncionario(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def _erros(self, resposta) -> dict:
        return resposta.context["form"].errors

    def _mensagens(self, resposta) -> list[str]:
        return [str(m) for m in get_messages(resposta.wsgi_request)]


class CadastroTests(ComFuncionario):
    def test_get_mostra_formulario_vazio(self):
        resposta = self.client.get(_url("criar"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "equipamentos/formulario.html")
        self.assertFalse(resposta.context["form"].is_bound)

    def test_cadastro_valido_com_virgula_decimal(self):
        resposta = self.client.post(
            _url("criar"), {**POST_VALIDO, "codigo": "  FUR-01  "}
        )
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        equipamento = Equipamento.objects.get()
        self.assertEqual(equipamento.codigo, "FUR-01")
        self.assertEqual(equipamento.valor_diaria, Decimal("35.50"))
        self.assertTrue(equipamento.ativo)

    def test_campos_obrigatorios(self):
        for campo in ("codigo", "nome", "categoria", "valor_diaria"):
            with self.subTest(campo=campo):
                resposta = self.client.post(_url("criar"), {**POST_VALIDO, campo: ""})
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(
                    self._erros(resposta)[campo], [mensagens.CAMPO_OBRIGATORIO]
                )
        self.assertFalse(Equipamento.objects.exists())

    def test_codigo_duplicado_inclusive_sem_diferenciar_maiusculas(self):
        criar_equipamento(codigo="FUR-01")
        for codigo in ("FUR-01", "fur-01", " Fur-01 "):
            with self.subTest(codigo=codigo):
                resposta = self.client.post(
                    _url("criar"), {**POST_VALIDO, "codigo": codigo}
                )
                self.assertEqual(
                    self._erros(resposta)["codigo"], [mensagens.CODIGO_DUPLICADO]
                )
        self.assertEqual(Equipamento.objects.count(), 1)

    def test_categoria_invalida(self):
        resposta = self.client.post(
            _url("criar"), {**POST_VALIDO, "categoria": "jardinagem"}
        )
        self.assertEqual(
            self._erros(resposta)["categoria"], [mensagens.CATEGORIA_INVALIDA]
        )

    def test_diaria_invalida(self):
        for valor in ("0", "0,00", "-10,00", "10,005", "abc"):
            with self.subTest(valor=valor):
                resposta = self.client.post(
                    _url("criar"), {**POST_VALIDO, "valor_diaria": valor}
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(
                    self._erros(resposta)["valor_diaria"], [mensagens.DIARIA_INVALIDA]
                )
        self.assertFalse(Equipamento.objects.exists())

    def test_campos_inesperados_sao_ignorados(self):
        self.client.post(
            _url("criar"),
            {**POST_VALIDO, "ativo": "False", "id": "999", "disponivel": "0"},
        )
        equipamento = Equipamento.objects.get()
        self.assertTrue(equipamento.ativo)
        self.assertNotEqual(equipamento.pk, 999)

    def test_erro_de_integridade_nao_vira_erro_500(self):
        """Corrida simulada: a validação não vê o duplicado, o índice do banco vê."""
        criar_equipamento(codigo="FUR-01")
        with (
            mock.patch.object(Equipamento, "_codigo_em_uso", return_value=False),
            mock.patch.object(Equipamento, "validate_constraints"),
        ):
            resposta = self.client.post(
                _url("criar"), {**POST_VALIDO, "codigo": "fur-01"}
            )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self._erros(resposta)["codigo"], [mensagens.CODIGO_DUPLICADO])
        self.assertEqual(Equipamento.objects.count(), 1)


class ConsultaTests(ComFuncionario):
    def _lista(self, **params):
        resposta = self.client.get(_url("lista"), params)
        self.assertEqual(resposta.status_code, 200)
        return resposta

    def test_lista_vazia(self):
        resposta = self._lista()
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_lista_ativos_e_inativos_com_situacao(self):
        criar_equipamento(codigo="ATV-01", nome="Betoneira")
        criar_equipamento(codigo="INA-01", nome="Andaime", ativo=False)
        resposta = self._lista()
        codigos = [e.codigo for e in resposta.context["object_list"]]
        self.assertEqual(codigos, ["INA-01", "ATV-01"])  # ordem por nome
        self.assertContains(resposta, "Ativo")
        self.assertContains(resposta, "Inativo")

    def test_pesquisa_por_nome_e_por_codigo(self):
        criar_equipamento(codigo="FUR-01", nome="Furadeira")
        criar_equipamento(codigo="PRJ-01", nome="Projetor")
        for termo, esperado in (
            ("furad", ["FUR-01"]),
            ("prj-", ["PRJ-01"]),
            ("  PROJ ", ["PRJ-01"]),
        ):
            with self.subTest(termo=termo):
                resposta = self._lista(q=termo)
                self.assertEqual(
                    [e.codigo for e in resposta.context["object_list"]], esperado
                )
                self.assertEqual(resposta.context["query"], termo.strip())

    def test_pesquisa_nao_usa_descricao(self):
        criar_equipamento(
            codigo="FUR-01", nome="Furadeira", descricao="acompanha maleta"
        )
        self.assertEqual(list(self._lista(q="maleta").context["object_list"]), [])

    def test_pesquisa_sem_resultado(self):
        criar_equipamento()
        resposta = self._lista(q="inexistente")
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_disponibilidade_calculada(self):
        livre = criar_equipamento(codigo="LIV-01")
        alugado = criar_equipamento(codigo="ALU-01")
        inativo = criar_equipamento(codigo="INA-01", ativo=False)
        reservado = criar_equipamento(codigo="RES-01")
        registrar(equipamento=alugado)
        registrar(equipamento=reservado, retirada=dias(10), prevista=dias(12))
        disponibilidade = {
            e.codigo: e.disponivel for e in self._lista().context["object_list"]
        }
        self.assertEqual(
            disponibilidade,
            {
                livre.codigo: True,
                alugado.codigo: False,
                inativo.codigo: False,
                reservado.codigo: False,
            },
        )

    def test_acoes_por_linha_sem_revalidar_cadastro(self):
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        linha = self._lista().context["object_list"][0]
        self.assertFalse(linha.acoes.pode_excluir)
        self.assertTrue(linha.acoes.pode_inativar)

    def test_sem_consultas_por_linha(self):
        for numero in range(2):
            equipamento = criar_equipamento(codigo=f"EQ-{numero}")
            encerrar(registrar(equipamento=equipamento))
        # sessão, usuário e uma única consulta da lista
        with self.assertNumQueries(3) as poucos:
            self._lista()
        for numero in range(2, 8):
            equipamento = criar_equipamento(codigo=f"EQ-{numero}")
            registrar(equipamento=equipamento)
        with self.assertNumQueries(len(poucos.captured_queries)):
            self._lista()


class EdicaoTests(ComFuncionario):
    def test_edicao_valida_sem_historico_inclusive_codigo(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        resposta = self.client.get(_url("editar", equipamento))
        self.assertTrue(resposta.context["codigo_editavel"])
        resposta = self.client.post(
            _url("editar", equipamento),
            {**POST_VALIDO, "codigo": "FUR-02", "nome": "Nova"},
        )
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        equipamento.refresh_from_db()
        self.assertEqual((equipamento.codigo, equipamento.nome), ("FUR-02", "Nova"))

    def test_codigo_somente_leitura_com_historico(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        encerrar(registrar(equipamento=equipamento))
        resposta = self.client.get(_url("editar", equipamento))
        self.assertFalse(resposta.context["codigo_editavel"])
        self.assertTrue(resposta.context["form"].fields["codigo"].disabled)
        for codigo in ("FUR-99", "fur-01"):
            with self.subTest(codigo=codigo):
                self.client.post(
                    _url("editar", equipamento),
                    {**POST_VALIDO, "codigo": codigo, "nome": codigo},
                )
                equipamento.refresh_from_db()
                self.assertEqual(equipamento.codigo, "FUR-01")
                self.assertEqual(
                    equipamento.nome, codigo
                )  # demais campos seguem editáveis

    def test_ct05_nova_diaria_nao_altera_contrato(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        aluguel = registrar(equipamento=equipamento, prevista=dias(2))
        self.client.post(
            _url("editar", equipamento),
            {**POST_VALIDO, "codigo": equipamento.codigo, "valor_diaria": "80,00"},
        )
        equipamento.refresh_from_db()
        aluguel.refresh_from_db()
        self.assertEqual(equipamento.valor_diaria, Decimal("80.00"))
        self.assertEqual(aluguel.valor_diaria_contratada, Decimal("50.00"))
        self.assertEqual(aluguel.valor_contratado, Decimal("150.00"))

    def test_edicao_nao_altera_situacao(self):
        equipamento = criar_equipamento()
        self.client.post(_url("editar", equipamento), {**POST_VALIDO, "ativo": "False"})
        equipamento.refresh_from_db()
        self.assertTrue(equipamento.ativo)

    def test_inexistente_retorna_404(self):
        self.assertEqual(
            self.client.get(reverse("equipamentos:editar", args=[999])).status_code, 404
        )


class AcoesTests(ComFuncionario):
    def _contexto(self, equipamento):
        resposta = self.client.get(_url("acoes", equipamento))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "equipamentos/acoes.html")
        return resposta.context

    def test_indicadores_por_situacao(self):
        sem_historico = criar_equipamento()
        com_historico = criar_equipamento()
        encerrar(registrar(equipamento=com_historico))
        com_aberto = criar_equipamento()
        registrar(equipamento=com_aberto)
        inativo = criar_equipamento(ativo=False)
        casos = {
            "sem histórico": (sem_historico, (True, True, False)),
            "com histórico": (com_historico, (False, True, False)),
            "com aluguel aberto": (com_aberto, (False, False, False)),
            "inativo": (inativo, (True, False, True)),
        }
        for descricao, (equipamento, esperado) in casos.items():
            with self.subTest(caso=descricao):
                contexto = self._contexto(equipamento)
                self.assertEqual(
                    (
                        contexto["pode_excluir"],
                        contexto["pode_inativar"],
                        contexto["pode_reativar"],
                    ),
                    esperado,
                )
        contexto = self._contexto(com_aberto)
        self.assertTrue(contexto["tem_aluguel_ativo"])
        self.assertContains(
            self.client.get(_url("acoes", com_aberto)), mensagens.ALUGUEL_ATIVO_IMPEDE
        )


class ExclusaoTests(ComFuncionario):
    def test_exclui_com_confirmacao(self):
        equipamento = criar_equipamento()
        resposta = self.client.post(
            _url("excluir", equipamento), {"confirmacao": "sim"}
        )
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        self.assertFalse(Equipamento.objects.exists())

    def test_sem_confirmacao_nao_exclui(self):
        equipamento = criar_equipamento()
        for dados in ({}, {"confirmacao": "nao"}, {"confirmacao": ""}):
            with self.subTest(dados=dados):
                resposta = self.client.post(_url("excluir", equipamento), dados)
                self.assertRedirects(
                    resposta, _url("acoes", equipamento), fetch_redirect_response=False
                )
                self.assertIn(
                    mensagens.CONFIRMACAO_DE_EXCLUSAO_AUSENTE, self._mensagens(resposta)
                )
        self.assertTrue(Equipamento.objects.filter(pk=equipamento.pk).exists())

    def test_recusa_com_historico_e_volta_para_acoes(self):
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        resposta = self.client.post(
            _url("excluir", equipamento), {"confirmacao": "sim"}
        )
        self.assertRedirects(
            resposta, _url("acoes", equipamento), fetch_redirect_response=False
        )
        self.assertIn(mensagens.EXCLUSAO_COM_HISTORICO, self._mensagens(resposta))
        self.assertEqual(Aluguel.objects.filter(equipamento=equipamento).count(), 1)

    def test_recusa_com_aluguel_aberto(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento)
        resposta = self.client.post(
            _url("excluir", equipamento), {"confirmacao": "sim"}
        )
        self.assertIn(mensagens.ALUGUEL_ATIVO_IMPEDE, self._mensagens(resposta))
        self.assertTrue(Equipamento.objects.filter(pk=equipamento.pk).exists())

    def test_get_nao_exclui(self):
        equipamento = criar_equipamento()
        self.assertEqual(self.client.get(_url("excluir", equipamento)).status_code, 405)
        self.assertTrue(Equipamento.objects.filter(pk=equipamento.pk).exists())


class InativacaoEReativacaoTests(ComFuncionario):
    def test_inativa_sem_e_com_historico(self):
        sem_historico = criar_equipamento()
        com_historico = criar_equipamento()
        encerrar(registrar(equipamento=com_historico))
        for equipamento in (sem_historico, com_historico):
            with self.subTest(equipamento=equipamento.codigo):
                resposta = self.client.post(_url("inativar", equipamento))
                self.assertRedirects(
                    resposta, _url("lista"), fetch_redirect_response=False
                )
                equipamento.refresh_from_db()
                self.assertFalse(equipamento.ativo)

    def test_recusa_inativar_com_aluguel_aberto(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento)
        resposta = self.client.post(_url("inativar", equipamento))
        self.assertRedirects(
            resposta, _url("acoes", equipamento), fetch_redirect_response=False
        )
        self.assertIn(mensagens.ALUGUEL_ATIVO_IMPEDE, self._mensagens(resposta))
        equipamento.refresh_from_db()
        self.assertTrue(equipamento.ativo)

    def test_reativa_valido_e_recusa_inconsistente(self):
        valido = criar_equipamento(ativo=False)
        resposta = self.client.post(_url("reativar", valido))
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        valido.refresh_from_db()
        self.assertTrue(valido.ativo)

        inconsistente = criar_equipamento(ativo=False)
        Equipamento.objects.filter(pk=inconsistente.pk).update(nome="   ")
        resposta = self.client.post(_url("reativar", inconsistente))
        self.assertIn(mensagens.REATIVACAO_BLOQUEADA, self._mensagens(resposta))
        inconsistente.refresh_from_db()
        self.assertFalse(inconsistente.ativo)

    def test_operacoes_repetidas_sao_previsiveis(self):
        equipamento = criar_equipamento(ativo=False)
        self.client.post(_url("inativar", equipamento))
        equipamento.refresh_from_db()
        self.assertFalse(equipamento.ativo)
        self.client.post(_url("reativar", equipamento))
        self.client.post(_url("reativar", equipamento))
        equipamento.refresh_from_db()
        self.assertTrue(equipamento.ativo)


class SegurancaTests(TestCase):
    def setUp(self):
        self.equipamento = criar_equipamento(codigo="SEG-01")
        self.rotas_get = [
            _url("lista"),
            _url("criar"),
            _url("editar", self.equipamento),
            _url("acoes", self.equipamento),
        ]
        self.rotas_post = [
            _url("criar"),
            _url("editar", self.equipamento),
            _url("excluir", self.equipamento),
            _url("inativar", self.equipamento),
            _url("reativar", self.equipamento),
        ]

    def _estado(self):
        return list(Equipamento.objects.values_list("codigo", "nome", "ativo"))

    def test_login_obrigatorio(self):
        antes = self._estado()
        for url in self.rotas_get:
            with self.subTest(url=url, metodo="GET"):
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
        for url in self.rotas_post:
            with self.subTest(url=url, metodo="POST"):
                resposta = self.client.post(url, {**POST_VALIDO, "confirmacao": "sim"})
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
        self.assertEqual(self._estado(), antes)

    def test_csrf_obrigatorio(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(criar_funcionario())
        antes = self._estado()
        for url in self.rotas_post:
            with self.subTest(url=url):
                resposta = cliente.post(
                    url, {**POST_VALIDO, "codigo": "NOVO", "confirmacao": "sim"}
                )
                self.assertEqual(resposta.status_code, 403)
        self.assertEqual(self._estado(), antes)

    def test_metodos_nao_permitidos(self):
        self.client.force_login(criar_funcionario())
        casos = [
            ("get", _url("excluir", self.equipamento)),
            ("get", _url("inativar", self.equipamento)),
            ("get", _url("reativar", self.equipamento)),
            ("post", _url("lista")),
            ("post", _url("acoes", self.equipamento)),
            ("put", _url("criar")),
            ("delete", _url("editar", self.equipamento)),
        ]
        for metodo, url in casos:
            with self.subTest(metodo=metodo, url=url):
                self.assertEqual(getattr(self.client, metodo)(url).status_code, 405)
        self.assertTrue(Equipamento.objects.filter(pk=self.equipamento.pk).exists())

    def test_inexistente_retorna_404(self):
        self.client.force_login(criar_funcionario())
        for nome in ("editar", "acoes"):
            with self.subTest(nome=nome):
                self.assertEqual(
                    self.client.get(
                        reverse(f"equipamentos:{nome}", args=[999])
                    ).status_code,
                    404,
                )
        for nome in ("excluir", "inativar", "reativar"):
            with self.subTest(nome=nome):
                resposta = self.client.post(
                    reverse(f"equipamentos:{nome}", args=[999]), {"confirmacao": "sim"}
                )
                self.assertEqual(resposta.status_code, 404)

    def test_post_manipulado_nao_contorna_as_regras(self):
        """Mesmo sem os botões da tela, o backend revalida cada operação."""
        self.client.force_login(criar_funcionario())
        encerrar(registrar(equipamento=self.equipamento))
        aberto = criar_equipamento()
        registrar(equipamento=aberto)
        self.client.post(_url("excluir", self.equipamento), {"confirmacao": "sim"})
        self.client.post(_url("inativar", aberto))
        self.client.post(_url("reativar", self.equipamento))  # já ativo: nada muda
        self.assertTrue(Equipamento.objects.filter(pk=self.equipamento.pk).exists())
        aberto.refresh_from_db()
        self.assertTrue(aberto.ativo)
        self.assertEqual(Aluguel.objects.count(), 2)
