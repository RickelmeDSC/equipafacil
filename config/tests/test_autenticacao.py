"""Autenticação e autorização da fundação (D1, D15; cobertura complementar FC12).

Usuários e senhas são temporários, gerados só durante os testes.
"""

import secrets

from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse


def _senha_temporaria() -> str:
    return secrets.token_urlsafe(16)


class AcessoAnonimoTests(TestCase):
    def test_pagina_de_login_e_publica(self):
        resposta = self.client.get(reverse("login"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "registration/login.html")

    def test_rota_protegida_redireciona_para_login(self):
        resposta = self.client.get(reverse("inicio"))
        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={reverse('inicio')}",
            fetch_redirect_response=False,
        )

    def test_admin_anonimo_redireciona_para_login(self):
        resposta = self.client.get("/admin/")
        self.assertRedirects(
            resposta, "/admin/login/?next=/admin/", fetch_redirect_response=False
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_login_do_admin_e_publico(self):
        resposta = self.client.get("/admin/login/")
        self.assertEqual(resposta.status_code, 200)

    def test_sem_cadastro_publico_nem_recuperacao_de_senha(self):
        for nome in ("password_reset", "password_reset_confirm", "signup", "register"):
            with self.subTest(rota=nome), self.assertRaises(NoReverseMatch):
                reverse(nome)
        for caminho in ("/cadastro/", "/accounts/signup/", "/password_reset/"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.get(caminho).status_code, 404)


class LoginTests(TestCase):
    def setUp(self):
        self.senha = _senha_temporaria()
        self.funcionario = get_user_model().objects.create_user(
            username="funcionario.teste", password=self.senha
        )

    def test_login_com_credenciais_validas(self):
        resposta = self.client.post(
            reverse("login"),
            {"username": "funcionario.teste", "password": self.senha},
        )
        self.assertRedirects(resposta, reverse("inicio"), fetch_redirect_response=False)
        self.assertEqual(self.client.session[SESSION_KEY], str(self.funcionario.pk))

    def test_login_com_senha_errada_nao_autentica(self):
        resposta = self.client.post(
            reverse("login"),
            {"username": "funcionario.teste", "password": _senha_temporaria()},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].errors)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_login_de_usuario_inativo_e_recusado(self):
        self.funcionario.is_active = False
        self.funcionario.save()
        resposta = self.client.post(
            reverse("login"),
            {"username": "funcionario.teste", "password": self.senha},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_usuario_autenticado_acessa_pagina_operacional(self):
        self.client.force_login(self.funcionario)
        resposta = self.client.get(reverse("inicio"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "inicio.html")
        self.assertContains(resposta, "funcionario.teste")

    def test_pagina_operacional_so_aceita_get(self):
        self.client.force_login(self.funcionario)
        self.assertEqual(self.client.post(reverse("inicio")).status_code, 405)

    def test_login_troca_a_chave_da_sessao(self):
        # Evita fixação de sessão: a chave anterior ao login não continua válida.
        sessao = self.client.session
        sessao["marcador"] = "anonimo"
        sessao.save()
        chave_anterior = sessao.session_key
        self.client.post(
            reverse("login"),
            {"username": "funcionario.teste", "password": self.senha},
        )
        self.assertIn(SESSION_KEY, self.client.session)
        self.assertNotEqual(self.client.session.session_key, chave_anterior)

    def test_login_ignora_redirecionamento_para_outro_site(self):
        resposta = self.client.post(
            reverse("login"),
            {
                "username": "funcionario.teste",
                "password": self.senha,
                "next": "https://site-externo.example/",
            },
        )
        self.assertRedirects(resposta, reverse("inicio"), fetch_redirect_response=False)

    def test_login_respeita_next_interno(self):
        resposta = self.client.post(
            reverse("login"),
            {"username": "funcionario.teste", "password": self.senha, "next": "/"},
        )
        self.assertRedirects(resposta, "/", fetch_redirect_response=False)

    def test_login_sem_token_csrf_e_recusado(self):
        cliente = Client(enforce_csrf_checks=True)
        resposta = cliente.post(
            reverse("login"),
            {"username": "funcionario.teste", "password": self.senha},
        )
        self.assertEqual(resposta.status_code, 403)
        self.assertNotIn(SESSION_KEY, cliente.session)

    def test_login_com_token_csrf_autentica(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.get(reverse("login"))
        resposta = cliente.post(
            reverse("login"),
            {
                "username": "funcionario.teste",
                "password": self.senha,
                "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
            },
        )
        self.assertRedirects(resposta, reverse("inicio"), fetch_redirect_response=False)


class LogoutTests(TestCase):
    def setUp(self):
        self.funcionario = get_user_model().objects.create_user(
            username="funcionario.teste", password=_senha_temporaria()
        )
        # Cliente que aplica a verificação de CSRF como em produção.
        self.cliente = Client(enforce_csrf_checks=True)
        self.cliente.force_login(self.funcionario)

    def _token_csrf(self) -> str:
        resposta = self.cliente.get(reverse("inicio"))
        self.assertEqual(resposta.status_code, 200)
        return self.cliente.cookies["csrftoken"].value

    def test_logout_por_get_nao_e_aceito(self):
        resposta = self.cliente.get(reverse("logout"))
        self.assertEqual(resposta.status_code, 405)
        self.assertIn(SESSION_KEY, self.cliente.session)

    def test_logout_por_post_sem_csrf_e_recusado(self):
        resposta = self.cliente.post(reverse("logout"))
        self.assertEqual(resposta.status_code, 403)
        self.assertIn(SESSION_KEY, self.cliente.session)

    def test_logout_por_post_com_csrf_encerra_a_sessao(self):
        token = self._token_csrf()
        resposta = self.cliente.post(reverse("logout"), {"csrfmiddlewaretoken": token})
        self.assertRedirects(resposta, reverse("login"), fetch_redirect_response=False)
        self.assertNotIn(SESSION_KEY, self.cliente.session)
        resposta = self.cliente.get(reverse("inicio"))
        self.assertEqual(resposta.status_code, 302)


class AdminTests(TestCase):
    def setUp(self):
        modelo = get_user_model()
        self.funcionario = modelo.objects.create_user(
            username="funcionario.teste", password=_senha_temporaria()
        )
        self.administrador = modelo.objects.create_superuser(
            username="admin.teste", password=_senha_temporaria()
        )

    def test_usuario_comum_nao_recebe_permissoes_administrativas(self):
        senha = _senha_temporaria()
        self.funcionario.set_password(senha)
        self.funcionario.save()
        resposta = self.client.post(
            reverse("login"), {"username": "funcionario.teste", "password": senha}
        )
        self.assertRedirects(resposta, reverse("inicio"), fetch_redirect_response=False)
        self.funcionario.refresh_from_db()
        self.assertFalse(self.funcionario.is_staff)
        self.assertFalse(self.funcionario.is_superuser)
        self.assertEqual(self.funcionario.get_all_permissions(), set())
        self.assertFalse(self.funcionario.groups.exists())

    def test_equipe_sem_permissao_nao_gerencia_contas(self):
        # Acesso ao Admin não basta: gerir contas exige permissão explícita (D15).
        equipe = get_user_model().objects.create_user(
            username="equipe.teste", password=_senha_temporaria(), is_staff=True
        )
        self.client.force_login(equipe)
        self.assertEqual(self.client.get("/admin/").status_code, 200)
        self.assertEqual(self.client.get("/admin/auth/user/").status_code, 403)
        self.assertEqual(self.client.get("/admin/auth/user/add/").status_code, 403)

    def test_funcionario_sem_permissao_nao_acessa_o_admin(self):
        self.client.force_login(self.funcionario)
        resposta = self.client.get("/admin/")
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.url.startswith("/admin/login/"))

    def test_funcionario_sem_permissao_nao_entra_pelo_login_do_admin(self):
        senha = _senha_temporaria()
        self.funcionario.set_password(senha)
        self.funcionario.save()
        resposta = self.client.post(
            "/admin/login/", {"username": "funcionario.teste", "password": senha}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_administrador_autorizado_acessa_o_admin(self):
        self.client.force_login(self.administrador)
        self.assertEqual(self.client.get("/admin/").status_code, 200)
        resposta = self.client.get("/admin/auth/user/add/")
        self.assertEqual(resposta.status_code, 200)
