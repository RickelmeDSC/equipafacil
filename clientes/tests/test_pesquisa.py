"""Pesquisa de clientes por nome ou CPF (RF009, RN002, D16).

Complementa CT17 e CT18 (``test_cenarios_ct.py``): regras do termo, CPF
parcial ou completo com ou sem máscara, estados da lista, leitura sem
gravação, consultas e autenticação. CPFs fictícios com dígitos válidos.
"""

from unittest import skipUnless

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from clientes.models import Cliente
from clientes.validadores import formatar_cpf
from config import mensagens
from config.tests.fabricas import (
    cpf_valido,
    criar_cliente,
    criar_funcionario,
    encerrar,
    registrar,
)

POSTGRESQL = connection.vendor == "postgresql"
CPF_MARIA = cpf_valido("529982247")  # 529.982.247-25
CPF_JOAO = cpf_valido("390533447")  # 390.533.447-05


def _url_lista() -> str:
    return reverse("clientes:lista")


class PesquisarQuerySetTests(TestCase):
    """``Cliente.objects.pesquisar``: só leitura, sem ordenar (a view ordena)."""

    @classmethod
    def setUpTestData(cls):
        cls.maria = criar_cliente(nome_completo="Maria Fictícia Souza", cpf=CPF_MARIA)
        cls.joao = criar_cliente(nome_completo="João Fictício Lima", cpf=CPF_JOAO)

    def _pks(self, termo) -> set[int]:
        return set(Cliente.objects.pesquisar(termo).values_list("pk", flat=True))

    def test_termo_ausente_vazio_ou_so_espacos_devolve_todos(self):
        for termo in (None, "", "   ", "\t \n"):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), {self.maria.pk, self.joao.pk})

    def test_nome_parcial_sem_diferenciar_maiusculas(self):
        for termo in ("maria", "MARIA", "aRiA", "fictícia sou", "  souza  "):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), {self.maria.pk})

    def test_cpf_completo_com_ou_sem_mascara(self):
        for termo in (CPF_MARIA, formatar_cpf(CPF_MARIA), f"  {CPF_MARIA}  "):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), {self.maria.pk})

    def test_cpf_parcial_com_ou_sem_mascara(self):
        for termo in ("98224", "529.982", "982.247-2", "247-25", "390.533"):
            esperado = {self.joao.pk} if termo == "390.533" else {self.maria.pk}
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), esperado)

    def test_so_pontuacao_nao_devolve_todos(self):
        # Sem pontos e hífen não sobra dígito: o termo não vira "contém vazio".
        for termo in (".", "-", ".-.", "..."):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), set())

    def test_termo_misto_pesquisa_so_pelo_nome(self):
        for termo in ("Maria 529", "529982abc", "Maria 529.982.247-25"):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), set())

    def test_cpf_so_desconsidera_pontos_e_hifen(self):
        # RN002 b: espaços, barras e vírgulas não são removidos do CPF.
        for termo in ("529 982 247 25", "529/982", "529,982"):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), set())

    def test_digitos_de_outros_alfabetos_nao_contam_como_cpf(self):
        for termo in ("５２９９８", "٥٢٩٩٨"):
            with self.subTest(termo=termo):
                self.assertEqual(self._pks(termo), set())

    def test_curingas_do_like_sao_texto_literal(self):
        com_sublinhado = criar_cliente(nome_completo="Ana_Teste Fictícia")
        criar_cliente(nome_completo="AnaXTeste Fictícia")
        self.assertEqual(self._pks("ana_teste"), {com_sublinhado.pk})
        self.assertEqual(self._pks("%"), set())

    @skipUnless(POSTGRESQL, "SQLite só ignora maiúsculas em letras sem acento")
    def test_maiusculas_acentuadas_no_postgresql(self):
        erica = criar_cliente(nome_completo="Érica Conceição")
        self.assertEqual(self._pks("ÉRICA CONCEIÇÃO"), {erica.pk})

    def test_acentos_nao_sao_ignorados(self):
        # Q3 (EQF-5, comentário 10078): sem pesquisa insensível a acentos.
        self.assertEqual(self._pks("joao"), set())
        self.assertEqual(self._pks("João"), {self.joao.pk})


class PesquisaNaListaTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def _lista(self, **params):
        resposta = self.client.get(_url_lista(), params)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "clientes/lista.html")
        return resposta

    def test_resultado_em_ordem_alfabetica_com_dados_formatados(self):
        zeta = criar_cliente(
            nome_completo="Maria Zeta",
            cpf=CPF_MARIA,
            telefone="81999998888",
            email="mz@exemplo.test",
        )
        criar_cliente(nome_completo="Bruno Fictício")
        alfa = criar_cliente(nome_completo="Maria Alfa")
        resposta = self._lista(q="maria")
        self.assertEqual(
            [c.pk for c in resposta.context["object_list"]], [alfa.pk, zeta.pk]
        )
        for texto in (formatar_cpf(CPF_MARIA), "(81) 99999-8888", "mz@exemplo.test"):
            self.assertContains(resposta, texto)
        self.assertNotContains(resposta, "Bruno Fictício")

    def test_pesquisa_por_cpf_na_tela_mantem_o_termo(self):
        maria = criar_cliente(nome_completo="Maria Fictícia", cpf=CPF_MARIA)
        criar_cliente(nome_completo="João Fictício", cpf=CPF_JOAO)
        for termo in (CPF_MARIA, formatar_cpf(CPF_MARIA), "982.247"):
            with self.subTest(termo=termo):
                resposta = self._lista(q=termo)
                self.assertEqual(list(resposta.context["object_list"]), [maria])
                self.assertEqual(resposta.context["query"], termo)
                self.assertContains(resposta, f'name="q" value="{termo}"')
                self.assertNotContains(resposta, "João Fictício")

    def test_termo_preservado_sem_espacos_nas_pontas_e_com_opcao_de_limpar(self):
        criar_cliente(nome_completo="Maria Fictícia")
        resposta = self._lista(q="  maria  ")
        self.assertEqual(resposta.context["query"], "maria")
        self.assertContains(resposta, 'name="q" value="maria"')
        self.assertContains(resposta, f'href="{_url_lista()}">Limpar</a>')

    def test_termo_vazio_lista_todos_sem_opcao_de_limpar(self):
        criar_cliente(nome_completo="Ana Fictícia")
        criar_cliente(nome_completo="Bruno Fictício")
        for params in ({}, {"q": ""}, {"q": "   "}):
            with self.subTest(params=params):
                resposta = self._lista(**params)
                self.assertEqual(len(resposta.context["object_list"]), 2)
                self.assertEqual(resposta.context["query"], "")
                self.assertContains(resposta, 'name="q" value=""')
                self.assertNotContains(resposta, "Limpar")

    def test_sem_correspondencia_mostra_mensagem_e_opcao_de_limpar(self):
        criar_cliente(nome_completo="Maria Fictícia")
        resposta = self._lista(q="inexistente")
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
        self.assertContains(resposta, "Limpar pesquisa")
        self.assertNotContains(resposta, "Cadastre o primeiro cliente")
        self.assertNotContains(resposta, "<tbody>")

    def test_sem_clientes_e_sem_termo_mantem_orientacao_de_cadastro(self):
        resposta = self._lista()
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
        self.assertContains(resposta, "Cadastre o primeiro cliente")
        self.assertNotContains(resposta, "Limpar pesquisa")

    def test_termo_e_escapado_na_pagina(self):
        resposta = self._lista(q='"><script>alert(1)</script>')
        self.assertNotContains(resposta, "<script>alert(1)</script>")
        self.assertContains(resposta, "&quot;&gt;&lt;script&gt;alert(1)")

    def test_pesquisa_so_le_o_banco_e_nao_altera_clientes(self):
        criar_cliente(nome_completo="Maria Fictícia", cpf=CPF_MARIA)
        criar_cliente(nome_completo="João Fictício", cpf=CPF_JOAO)
        antes = list(Cliente.objects.order_by("pk").values())
        with CaptureQueriesContext(connection) as consultas:
            for termo in ("maria", CPF_MARIA, "982.247", "inexistente", ""):
                self._lista(q=termo)
        self.assertTrue(consultas.captured_queries)
        for consulta in consultas.captured_queries:
            with self.subTest(sql=consulta["sql"]):
                self.assertTrue(consulta["sql"].lstrip().upper().startswith("SELECT"))
        self.assertEqual(list(Cliente.objects.order_by("pk").values()), antes)

    def test_pesquisa_sem_consulta_por_linha(self):
        criar_cliente(nome_completo="Maria Fictícia")
        with self.assertNumQueries(3):  # sessão, usuário e a lista
            self._lista(q="maria")
        for _ in range(5):
            encerrar(registrar(cliente=criar_cliente(nome_completo="Maria Outra")))
        with self.assertNumQueries(3):
            self._lista(q="maria")


class PesquisaComAutenticacaoTests(TestCase):
    def test_anonimo_e_redirecionado_sem_ver_clientes(self):
        criar_cliente(nome_completo="Maria Fictícia", cpf=CPF_MARIA)
        for termo in ("maria", CPF_MARIA, formatar_cpf(CPF_MARIA)):
            with self.subTest(termo=termo):
                resposta = self.client.get(_url_lista(), {"q": termo})
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
                self.assertNotIn(b"Maria", resposta.content)
