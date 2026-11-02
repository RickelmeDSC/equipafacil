"""Cabeçalhos de segurança, cookies e saída dos templates provisórios."""

import secrets

from django.contrib.auth import get_user_model
from django.test import TestCase
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
