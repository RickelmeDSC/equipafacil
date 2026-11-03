"""Cabeçalhos de segurança, cookies e saída dos templates provisórios."""

import secrets

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse


class CabecalhosDeSegurancaTests(TestCase):
    def test_paginas_publicas_e_protegidas_enviam_cabecalhos(self):
        usuario = get_user_model().objects.create_user(
            username="funcionario.teste", password=secrets.token_urlsafe(16)
        )
        respostas = {"login": self.client.get(reverse("login"))}
        self.client.force_login(usuario)
        respostas["inicio"] = self.client.get(reverse("inicio"))
        esperados = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "same-origin",
            "Cross-Origin-Opener-Policy": "same-origin",
        }
        for pagina, resposta in respostas.items():
            for cabecalho, valor in esperados.items():
                with self.subTest(pagina=pagina, cabecalho=cabecalho):
                    self.assertEqual(resposta.headers.get(cabecalho), valor)

    def test_cookie_de_sessao_inacessivel_ao_javascript(self):
        usuario = get_user_model().objects.create_user(
            username="funcionario.teste", password=(senha := secrets.token_urlsafe(16))
        )
        resposta = self.client.post(
            reverse("login"), {"username": usuario.username, "password": senha}
        )
        self.assertTrue(resposta.cookies["sessionid"]["httponly"])
        self.assertEqual(resposta.cookies["sessionid"]["samesite"], "Lax")


class TemplatesProvisoriosTests(TestCase):
    def test_login_escapa_o_parametro_next(self):
        ataque = '"><script>alert(1)</script>'
        resposta = self.client.get(reverse("login"), {"next": ataque})
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "<script>alert(1)</script>")
        self.assertContains(resposta, "&lt;script&gt;")

    def test_login_tem_csrf_e_sem_credenciais_de_exemplo(self):
        resposta = self.client.get(reverse("login"))
        self.assertContains(resposta, 'name="csrfmiddlewaretoken"')
        self.assertContains(resposta, 'method="post"')
        conteudo = resposta.content.decode().lower()
        for termo in ("admin123", "senha123", 'value="admin'):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, conteudo)

    def test_inicio_escapa_o_nome_do_usuario_e_sai_por_post(self):
        usuario = get_user_model().objects.create_user(
            username="<b>teste</b>", password=secrets.token_urlsafe(16)
        )
        self.client.force_login(usuario)
        resposta = self.client.get(reverse("inicio"))
        self.assertNotContains(resposta, "<b>teste</b>")
        self.assertContains(resposta, "&lt;b&gt;teste&lt;/b&gt;")
        self.assertContains(resposta, f'action="{reverse("logout")}"')
        self.assertContains(resposta, 'name="csrfmiddlewaretoken"')


PROXY_HTTPS = ("HTTP_X_FORWARDED_PROTO", "https")


@override_settings(
    SECURE_SSL_REDIRECT=True,
    SECURE_PROXY_SSL_HEADER=PROXY_HTTPS,
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
)
class ProducaoAtrasDoProxyTests(TestCase):
    """Comportamento com as configurações de produção atrás do proxy do Render."""

    def setUp(self):
        self.senha = secrets.token_urlsafe(16)
        get_user_model().objects.create_user(
            username="funcionario.teste", password=self.senha
        )
        self.cliente = Client(enforce_csrf_checks=True)

    def _https(self, **extras):
        # Como o proxy do Render: marca HTTPS e envia o Host. Sem Host, o cliente
        # de testes informaria a porta 80 e a origem viraria https://testserver:80.
        return {"HTTP_X_FORWARDED_PROTO": "https", "HTTP_HOST": "testserver", **extras}

    def test_http_direto_e_redirecionado_para_https(self):
        resposta = self.cliente.get(reverse("login"))
        self.assertEqual(resposta.status_code, 301)
        self.assertEqual(resposta["Location"], "https://testserver/login/")

    def test_requisicao_https_vinda_do_proxy_nao_e_redirecionada(self):
        self.assertEqual(
            self.cliente.get(reverse("login"), **self._https()).status_code, 200
        )

    @override_settings(SECURE_PROXY_SSL_HEADER=None)
    def test_sem_proxy_configurado_o_cabecalho_e_ignorado(self):
        resposta = self.cliente.get(reverse("login"), **self._https())
        self.assertEqual(resposta.status_code, 301)

    def test_login_por_https_usa_cookies_secure_e_exige_origem(self):
        resposta = self.cliente.get(reverse("login"), **self._https())
        self.assertTrue(resposta.cookies["csrftoken"]["secure"])
        dados = {
            "username": "funcionario.teste",
            "password": self.senha,
            "csrfmiddlewaretoken": self.cliente.cookies["csrftoken"].value,
        }
        # Origem de outro site ou ausente: recusado pela proteção CSRF.
        externa = self.cliente.post(
            reverse("login"),
            dados,
            **self._https(HTTP_ORIGIN="https://site-externo.example"),
        )
        self.assertEqual(externa.status_code, 403)
        sem_origem = self.cliente.post(reverse("login"), dados, **self._https())
        self.assertEqual(sem_origem.status_code, 403)
        # Mesma origem: autentica e a sessão sai com cookie Secure.
        resposta = self.cliente.post(
            reverse("login"),
            dados,
            **self._https(HTTP_ORIGIN="https://testserver"),
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.cookies["sessionid"]["secure"])

    def test_hsts_desligado_por_padrao(self):
        resposta = self.cliente.get(reverse("login"), **self._https())
        self.assertNotIn("Strict-Transport-Security", resposta)

    @override_settings(SECURE_HSTS_SECONDS=3600)
    def test_hsts_configuravel(self):
        resposta = self.cliente.get(reverse("login"), **self._https())
        self.assertEqual(resposta["Strict-Transport-Security"], "max-age=3600")

    @override_settings(ALLOWED_HOSTS=["equipafacil.onrender.com"])
    def test_host_fora_de_allowed_hosts_e_recusado(self):
        aceito = self.cliente.get(
            reverse("login"), **self._https(HTTP_HOST="equipafacil.onrender.com")
        )
        self.assertEqual(aceito.status_code, 200)
        recusado = self.cliente.get(
            reverse("login"), **self._https(HTTP_HOST="site-externo.example")
        )
        self.assertEqual(recusado.status_code, 400)
