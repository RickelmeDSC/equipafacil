"""Views de clientes: cadastro, listagem (D14), edição e segurança (P05, P06)."""

import logging
from contextlib import contextmanager
from unittest import mock

from django.contrib import admin
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse

from clientes.models import Cliente
from clientes.validadores import formatar_cpf
from config import mensagens
from config.seguranca import FiltroDeRelatorioDeErros
from config.tests.fabricas import (
    cpf_valido,
    criar_cliente,
    criar_funcionario,
    encerrar,
    registrar,
)

CPF_A = cpf_valido("390533447")
CPF_B = cpf_valido("714602318")
POST_VALIDO = {
    "nome_completo": "Maria Fictícia da Silva",
    "cpf": formatar_cpf(CPF_A),
    "telefone": "",
    "email": "",
}


def _url(nome: str, cliente: Cliente | None = None) -> str:
    return reverse(f"clientes:{nome}", args=[cliente.pk] if cliente else [])


def _cpf_com_digito_errado(cpf: str) -> str:
    return cpf[:-1] + str((int(cpf[-1]) + 1) % 10)


class ComFuncionario(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def _erros(self, resposta) -> dict:
        self.assertEqual(resposta.status_code, 200)
        return resposta.context["form"].errors


class CadastroTests(ComFuncionario):
    def _cadastrar(self, **campos):
        return self.client.post(_url("criar"), {**POST_VALIDO, **campos})

    def test_get_mostra_formulario_vazio(self):
        resposta = self.client.get(_url("criar"))
        self.assertTemplateUsed(resposta, "clientes/formulario.html")
        self.assertFalse(resposta.context["form"].is_bound)

    def test_01_02_nome_e_cpf_validos_sem_telefone_e_sem_email(self):
        resposta = self._cadastrar()
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        cliente = Cliente.objects.get()
        self.assertEqual(
            (cliente.nome_completo, cliente.cpf, cliente.telefone, cliente.email),
            ("Maria Fictícia da Silva", CPF_A, "", ""),
        )

    def test_03_04_cpf_formatado_ou_sem_pontuacao_persiste_onze_digitos(self):
        for entrada in (formatar_cpf(CPF_A), CPF_A):
            with self.subTest(entrada=entrada):
                Cliente.objects.all().delete()
                self._cadastrar(cpf=entrada)
                self.assertEqual(Cliente.objects.get().cpf, CPF_A)

    def test_05_06_cpf_duplicado_com_ou_sem_pontuacao(self):
        criar_cliente(cpf=CPF_A)
        for entrada in (CPF_A, formatar_cpf(CPF_A)):
            with self.subTest(entrada=entrada):
                erros = self._erros(self._cadastrar(cpf=entrada))
                self.assertEqual(erros["cpf"], [mensagens.CPF_DUPLICADO])
        self.assertEqual(Cliente.objects.count(), 1)

    def test_07_08_09_cpf_invalido_nao_e_gravado(self):
        casos = {
            "dígito verificador incorreto": _cpf_com_digito_errado(CPF_A),
            "todos os dígitos iguais": "111.111.111-11",
            "letras": CPF_A[:5] + "A" + CPF_A[6:],
            "vírgulas": "390,533,447-" + CPF_A[-2:],
            "barra": CPF_A[:3] + "/" + CPF_A[3:],
            "espaço": " " + CPF_A,
            "dígitos a menos": CPF_A[:10],
            "dígitos a mais": CPF_A + "0",
            "entrada longa demais": "1" * 30,
        }
        for descricao, entrada in casos.items():
            with self.subTest(caso=descricao):
                erros = self._erros(self._cadastrar(cpf=entrada))
                self.assertEqual(erros["cpf"], [mensagens.CPF_INVALIDO])
        self.assertFalse(Cliente.objects.exists())

    def test_10_nome_e_cpf_obrigatorios(self):
        for campo in ("nome_completo", "cpf"):
            with self.subTest(campo=campo):
                erros = self._erros(self._cadastrar(**{campo: ""}))
                self.assertEqual(erros[campo], [mensagens.CAMPO_OBRIGATORIO])
        erros = self._erros(self._cadastrar(nome_completo="   "))
        self.assertEqual(erros["nome_completo"], [mensagens.CAMPO_OBRIGATORIO])
        self.assertFalse(Cliente.objects.exists())

    def test_11_12_telefone_com_10_ou_11_digitos(self):
        casos = {
            "(81) 3333-4444": "8133334444",
            "8133334444": "8133334444",
            "(81) 99999-8888": "81999998888",
            "81 99999 8888": "81999998888",
        }
        for numero, (entrada, esperado) in enumerate(casos.items()):
            with self.subTest(entrada=entrada):
                cpf = cpf_valido(f"{200000000 + numero:09d}")
                self._cadastrar(cpf=cpf, telefone=entrada)
                cliente = Cliente.objects.get(cpf=cpf)
                self.assertEqual(cliente.telefone, esperado)

    def test_13_telefone_invalido(self):
        for entrada in (
            "3333-4444",
            "(81) 9999-888",
            "+55 81 99999-8888",
            "81.3333.4444",
            "8199999888877",
        ):
            with self.subTest(entrada=entrada):
                erros = self._erros(self._cadastrar(telefone=entrada))
                self.assertEqual(erros["telefone"], [mensagens.TELEFONE_INVALIDO])
        self.assertFalse(Cliente.objects.exists())

    def test_14_email_invalido(self):
        for entrada in ("maria", "maria@", "maria@exemplo"):
            with self.subTest(entrada=entrada):
                erros = self._erros(self._cadastrar(email=entrada))
                self.assertEqual(erros["email"], [mensagens.EMAIL_INVALIDO])
        self.assertFalse(Cliente.objects.exists())

    def test_15_campos_extras_manipulados_sao_ignorados(self):
        outro = criar_cliente(cpf=CPF_B)
        self._cadastrar(
            id=str(outro.pk), pk=str(outro.pk), endereco="Rua X", alugueis="1"
        )
        self.assertEqual(Cliente.objects.count(), 2)
        outro.refresh_from_db()
        self.assertEqual(outro.cpf, CPF_B)
        self.assertFalse(hasattr(Cliente.objects.get(cpf=CPF_A), "endereco"))

    def test_erro_de_integridade_nao_vira_erro_500(self):
        """Corrida simulada: a validação não vê o duplicado; o índice único vê."""
        criar_cliente(cpf=CPF_A)
        with (
            mock.patch.object(Cliente, "_cpf_em_uso", return_value=False),
            mock.patch.object(Cliente, "validate_constraints"),
        ):
            erros = self._erros(self._cadastrar())
        self.assertEqual(erros["cpf"], [mensagens.CPF_DUPLICADO])
        self.assertEqual(Cliente.objects.count(), 1)


class ListagemTests(ComFuncionario):
    def _lista(self, **params):
        resposta = self.client.get(_url("lista"), params)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "clientes/lista.html")
        return resposta

    def test_16_lista_vazia(self):
        resposta = self._lista()
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_17_lista_com_dados_formatados_e_link_de_edicao(self):
        cliente = criar_cliente(
            cpf=CPF_A, telefone="81999998888", email="a@exemplo.test"
        )
        resposta = self._lista()
        self.assertContains(resposta, formatar_cpf(CPF_A))
        self.assertContains(resposta, "(81) 99999-8888")
        self.assertContains(resposta, "a@exemplo.test")
        self.assertContains(resposta, _url("editar", cliente))
        self.assertNotContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_18_ordem_por_nome_e_depois_por_cadastro(self):
        bruno = criar_cliente(nome_completo="Bruno Fictício")
        ana_1 = criar_cliente(nome_completo="Ana Fictícia")
        ana_2 = criar_cliente(nome_completo="Ana Fictícia")
        ordem = [c.pk for c in self._lista().context["object_list"]]
        self.assertEqual(ordem, [ana_1.pk, ana_2.pk, bruno.pk])

    def test_19_sem_pesquisa(self):
        criar_cliente(nome_completo="Ana Fictícia")
        criar_cliente(nome_completo="Bruno Fictício")
        resposta = self._lista(q="Ana")
        self.assertEqual(len(resposta.context["object_list"]), 2)  # parâmetro ignorado
        self.assertNotIn("query", resposta.context)
        self.assertNotContains(resposta, 'name="q"')

    def test_20_sem_pagina_de_detalhe(self):
        cliente = criar_cliente()
        with self.assertRaises(NoReverseMatch):
            reverse("clientes:detalhe", args=[cliente.pk])
        self.assertEqual(self.client.get(f"/clientes/{cliente.pk}/").status_code, 404)
        with self.assertRaises(TemplateDoesNotExist):
            get_template("clientes/detalhe.html")

    def test_lista_sem_consulta_por_linha(self):
        criar_cliente()
        with self.assertNumQueries(3) as poucos:  # sessão, usuário e a lista
            self._lista()
        for _ in range(5):
            encerrar(registrar(cliente=criar_cliente()))
        with self.assertNumQueries(len(poucos.captured_queries)):
            self._lista()


class EdicaoTests(ComFuncionario):
    def _editar(self, cliente, **campos):
        dados = {
            "nome_completo": cliente.nome_completo,
            "cpf": cliente.cpf,
            "telefone": cliente.telefone,
            "email": cliente.email,
        }
        return self.client.post(_url("editar", cliente), {**dados, **campos})

    def test_get_mostra_cpf_e_telefone_formatados(self):
        cliente = criar_cliente(cpf=CPF_A, telefone="81999998888")
        resposta = self.client.get(_url("editar", cliente))
        self.assertTrue(resposta.context["cpf_editavel"])
        self.assertEqual(resposta.context["object"], cliente)
        self.assertContains(resposta, formatar_cpf(CPF_A))
        self.assertContains(resposta, "(81) 99999-8888")

    def test_22_23_24_nome_telefone_e_email_editaveis_mesmo_com_historico(self):
        cliente = criar_cliente(cpf=CPF_A)
        encerrar(registrar(cliente=cliente))
        resposta = self._editar(
            cliente,
            nome_completo="Nome Corrigido",
            telefone="(81) 3333-4444",
            email="novo@exemplo.test",
        )
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        cliente.refresh_from_db()
        self.assertEqual(
            (cliente.nome_completo, cliente.telefone, cliente.email, cliente.cpf),
            ("Nome Corrigido", "8133334444", "novo@exemplo.test", CPF_A),
        )

    def test_25_cpf_editavel_sem_historico(self):
        cliente = criar_cliente(cpf=CPF_A)
        resposta = self._editar(cliente, cpf=formatar_cpf(CPF_B))
        self.assertRedirects(resposta, _url("lista"), fetch_redirect_response=False)
        cliente.refresh_from_db()
        self.assertEqual(cliente.cpf, CPF_B)

    def test_26_27_cpf_somente_leitura_com_aluguel_aberto_ou_encerrado(self):
        aberto = criar_cliente(cpf=CPF_A)
        registrar(cliente=aberto)
        encerrado = criar_cliente(cpf=CPF_B)
        encerrar(registrar(cliente=encerrado))
        for cliente in (aberto, encerrado):
            with self.subTest(cpf=cliente.cpf):
                resposta = self.client.get(_url("editar", cliente))
                self.assertFalse(resposta.context["cpf_editavel"])
                self.assertTrue(resposta.context["form"].fields["cpf"].disabled)
                self.assertContains(resposta, mensagens.CPF_BLOQUEADO)
                original = cliente.cpf
                # POST manipulado: o valor enviado é ignorado; o resto é gravado.
                resposta = self._editar(
                    cliente, cpf=cpf_valido("123456780"), nome_completo="Nome Novo"
                )
                self.assertRedirects(
                    resposta, _url("lista"), fetch_redirect_response=False
                )
                cliente.refresh_from_db()
                self.assertEqual(
                    (cliente.cpf, cliente.nome_completo), (original, "Nome Novo")
                )

    def test_28_mesmo_cpf_reenviado_com_ou_sem_pontuacao(self):
        """Reenviar o CPF gravado, com ou sem pontuação, não é alteração."""
        sem_historico = criar_cliente(cpf=CPF_A)
        com_historico = criar_cliente(cpf=CPF_B)
        encerrar(registrar(cliente=com_historico))
        for cliente in (sem_historico, com_historico):
            original = cliente.cpf
            for cpf in (original, formatar_cpf(original)):
                with self.subTest(cpf=cpf):
                    email = f"{cpf.replace('.', '').replace('-', '')}@exemplo.test"
                    resposta = self._editar(cliente, cpf=cpf, email=email)
                    self.assertRedirects(
                        resposta, _url("lista"), fetch_redirect_response=False
                    )
                    cliente.refresh_from_db()
                    self.assertEqual((cliente.cpf, cliente.email), (original, email))

    def test_29_cpf_de_outro_cliente(self):
        criar_cliente(cpf=CPF_A)
        cliente = criar_cliente(cpf=CPF_B)
        erros = self._erros(self._editar(cliente, cpf=formatar_cpf(CPF_A)))
        self.assertEqual(erros["cpf"], [mensagens.CPF_DUPLICADO])
        cliente.refresh_from_db()
        self.assertEqual(cliente.cpf, CPF_B)

    def test_dados_invalidos_nao_sao_gravados(self):
        cliente = criar_cliente(cpf=CPF_A, telefone="81999998888")
        erros = self._erros(
            self._editar(cliente, nome_completo="", telefone="123", email="invalido")
        )
        self.assertEqual(set(erros), {"nome_completo", "telefone", "email"})
        cliente.refresh_from_db()
        self.assertEqual(cliente.telefone, "81999998888")

    def test_30_campos_protegidos_e_id_manipulados(self):
        cliente = criar_cliente(cpf=CPF_A)
        outro = criar_cliente(cpf=CPF_B, nome_completo="Outro Cliente")
        self._editar(
            cliente, id=str(outro.pk), pk=str(outro.pk), nome_completo="Alterado"
        )
        cliente.refresh_from_db()
        outro.refresh_from_db()
        self.assertEqual(cliente.nome_completo, "Alterado")
        self.assertEqual(outro.nome_completo, "Outro Cliente")
        self.assertEqual(Cliente.objects.count(), 2)

    def test_cliente_inexistente_retorna_404(self):
        self.assertEqual(
            self.client.get(reverse("clientes:editar", args=[999])).status_code, 404
        )
        resposta = self.client.post(reverse("clientes:editar", args=[999]), POST_VALIDO)
        self.assertEqual(resposta.status_code, 404)
        self.assertFalse(Cliente.objects.exists())


@contextmanager
def _capturar_logs():
    """Captura tudo o que os loggers do projeto registrariam."""
    registros: list[logging.LogRecord] = []

    class Coletor(logging.Handler):
        def emit(self, record):
            registros.append(record)

    coletor = Coletor(level=logging.DEBUG)
    loggers = [logging.getLogger(), logging.getLogger("django")]
    for logger in loggers:
        logger.addHandler(coletor)
    try:
        yield registros
    finally:
        for logger in loggers:
            logger.removeHandler(coletor)


class SegurancaTests(TestCase):
    def setUp(self):
        self.cliente = criar_cliente(cpf=CPF_B, nome_completo="Cliente Seguro")
        self.rotas_get = [_url("lista"), _url("criar"), _url("editar", self.cliente)]
        self.rotas_post = [_url("criar"), _url("editar", self.cliente)]

    def _estado(self):
        return list(Cliente.objects.order_by("pk").values_list("nome_completo", "cpf"))

    def test_21_login_obrigatorio(self):
        antes = self._estado()
        for url in self.rotas_get:
            with self.subTest(url=url, metodo="GET"):
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
        for url in self.rotas_post:
            with self.subTest(url=url, metodo="POST"):
                resposta = self.client.post(
                    url, {**POST_VALIDO, "nome_completo": "Invasor"}
                )
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(reverse("login")))
        self.assertEqual(self._estado(), antes)

    def test_autenticado_acessa_as_paginas(self):
        self.client.force_login(criar_funcionario())
        for url in self.rotas_get:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_csrf_obrigatorio(self):
        cliente_http = Client(enforce_csrf_checks=True)
        cliente_http.force_login(criar_funcionario())
        antes = self._estado()
        for url in self.rotas_post:
            with self.subTest(url=url):
                resposta = cliente_http.post(
                    url, {**POST_VALIDO, "nome_completo": "Sem CSRF"}
                )
                self.assertEqual(resposta.status_code, 403)
        self.assertEqual(self._estado(), antes)

    def test_metodos_nao_permitidos(self):
        self.client.force_login(criar_funcionario())
        casos = [
            ("post", _url("lista")),
            ("put", _url("criar")),
            ("delete", _url("editar", self.cliente)),
            ("patch", _url("editar", self.cliente)),
        ]
        for metodo, url in casos:
            with self.subTest(metodo=metodo, url=url):
                self.assertEqual(getattr(self.client, metodo)(url).status_code, 405)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_sem_exclusao_de_cliente(self):
        with self.assertRaises(NoReverseMatch):
            reverse("clientes:excluir", args=[self.cliente.pk])

    def test_cpf_nao_aparece_nos_logs(self):
        self.client.force_login(criar_funcionario())
        with _capturar_logs() as registros:
            self.client.post(_url("criar"), POST_VALIDO)
            self.client.post(_url("criar"), POST_VALIDO)  # duplicado
            self.client.post(_url("criar"), {**POST_VALIDO, "cpf": "111.111.111-11"})
            self.client.post(reverse("clientes:editar", args=[999]), POST_VALIDO)  # 404
            self.client.get(_url("lista"), {"cpf": CPF_A})
            self.client.delete(_url("editar", self.cliente))  # 405
        self.assertTrue(registros, "esperava ao menos os avisos de 404 e 405")
        texto = "\n".join(registro.getMessage() for registro in registros)
        for valor in (CPF_A, formatar_cpf(CPF_A), CPF_B, formatar_cpf(CPF_B)):
            self.assertNotIn(valor, texto)

    def test_relatorio_de_erro_mascara_cpf_e_contatos(self):
        self.client.force_login(criar_funcionario())
        resposta = self.client.post(
            _url("criar"),
            {**POST_VALIDO, "telefone": "81999998888", "email": "m@exemplo.test"},
        )
        parametros = FiltroDeRelatorioDeErros().get_post_parameters(
            resposta.wsgi_request
        )
        for campo in ("cpf", "telefone", "email"):
            with self.subTest(campo=campo):
                self.assertNotIn(
                    parametros[campo],
                    (CPF_A, formatar_cpf(CPF_A), "81999998888", "m@exemplo.test"),
                )
                self.assertTrue(set(parametros[campo]) == {"*"})
        self.assertEqual(parametros["nome_completo"], POST_VALIDO["nome_completo"])

    def test_cliente_fora_do_django_admin(self):
        self.assertFalse(admin.site.is_registered(Cliente))
        modelo_usuario = criar_funcionario().__class__
        administrador = modelo_usuario.objects.create_superuser(
            username="admin.clientes", password=None
        )
        self.client.force_login(administrador)
        self.assertEqual(self.client.get("/admin/clientes/cliente/").status_code, 404)
        self.client.force_login(criar_funcionario("funcionario.sem.admin"))
        resposta = self.client.get("/admin/")
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta["Location"].startswith("/admin/login/"))
