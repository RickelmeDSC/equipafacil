"""Health check /healthz/: público, sem banco e sem expor configuração."""

import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

CAMINHO = "/healthz/"


class HealthCheckTests(TestCase):
    def test_visitante_recebe_ok_sem_consultar_o_banco(self):
        with self.assertNumQueries(0):
            resposta = self.client.get(CAMINHO)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.content, b"ok\n")
        self.assertEqual(resposta["Content-Type"], "text/plain; charset=utf-8")

    def test_cookie_de_sessao_nao_leva_a_consulta_ao_banco(self):
        usuario = get_user_model().objects.create_user(
            username="funcionario.teste", password=secrets.token_urlsafe(16)
        )
        self.client.force_login(usuario)
        with self.assertNumQueries(0):
            resposta = self.client.get(CAMINHO)
        self.assertEqual(resposta.status_code, 200)
        # Contraprova: com o mesmo cookie, uma página comum lê sessão e usuário.
        with CaptureQueriesContext(connection) as consultas:
            self.assertEqual(self.client.get("/").status_code, 200)
        self.assertGreater(len(consultas), 0)

    def test_head_e_aceito_e_outros_metodos_nao(self):
        self.assertEqual(self.client.head(CAMINHO).status_code, 200)
        resposta = self.client.post(CAMINHO)
        self.assertEqual(resposta.status_code, 405)
        self.assertEqual(resposta["Allow"], "GET, HEAD")

    def test_resposta_nao_e_armazenada_em_cache(self):
        resposta = self.client.get(CAMINHO)
        self.assertIn("no-store", resposta["Cache-Control"])

    def test_mantem_os_cabecalhos_de_seguranca(self):
        resposta = self.client.get(CAMINHO)
        self.assertEqual(resposta["X-Content-Type-Options"], "nosniff")
        self.assertEqual(resposta["Referrer-Policy"], "same-origin")

    def test_nao_expoe_configuracao(self):
        conteudo = self.client.get(CAMINHO).content.decode()
        for termo in ("DEBUG", "SECRET", "postgres", "sqlite", settings.SECRET_KEY):
            with self.subTest(termo=termo[:6]):
                self.assertNotIn(termo, conteudo)

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_responde_por_http_sem_redirecionar_para_https(self):
        self.assertEqual(self.client.get(CAMINHO).status_code, 200)
        # As demais páginas continuam redirecionadas para HTTPS.
        resposta = self.client.get("/login/")
        self.assertEqual(resposta.status_code, 301)
        self.assertTrue(resposta["Location"].startswith("https://"))

    def test_host_fora_de_allowed_hosts_e_recusado_sem_consultar_o_banco(self):
        with self.assertLogs("django.security.DisallowedHost", "ERROR"):
            with self.assertNumQueries(0):
                resposta = self.client.get(CAMINHO, HTTP_HOST="site-externo.example")
        self.assertEqual(resposta.status_code, 400)
        self.assertNotIn(b"ok", resposta.content)

    @override_settings(
        ALLOWED_HOSTS=["equipafacil.onrender.com"], SECURE_SSL_REDIRECT=True
    )
    def test_host_do_render_responde_por_http_sem_redirecionar(self):
        # O health check do Render usa o subdomínio onrender.com como Host.
        resposta = self.client.get(CAMINHO, HTTP_HOST="equipafacil.onrender.com")
        self.assertEqual(resposta.status_code, 200)
        resposta = self.client.get(CAMINHO, HTTP_HOST="site-externo.example")
        self.assertEqual(resposta.status_code, 400)

    def test_outras_rotas_continuam_protegidas(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta["Location"].startswith("/login/"))

    def test_posicao_antes_da_sessao(self):
        middleware = settings.MIDDLEWARE
        self.assertLess(
            middleware.index("config.middleware.HealthCheckMiddleware"),
            middleware.index("django.contrib.sessions.middleware.SessionMiddleware"),
        )
