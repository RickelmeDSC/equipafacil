"""Inicialização e configurações essenciais da fundação Django (DEV-02)."""

from datetime import UTC, date, datetime
from io import StringIO

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

APPS_DE_DOMINIO = ("equipamentos", "clientes", "alugueis")


class InicializacaoTests(SimpleTestCase):
    def test_verificacao_do_sistema_sem_problemas(self):
        saida = StringIO()
        call_command("check", stdout=saida)
        self.assertIn("no issues", saida.getvalue())

    def test_apps_de_dominio_registrados(self):
        for app in APPS_DE_DOMINIO:
            with self.subTest(app=app):
                self.assertTrue(apps.is_installed(app))
        self.assertEqual(apps.get_app_config("alugueis").verbose_name, "Aluguéis")

    def test_sem_app_de_autenticacao_propria_nem_core(self):
        for app in ("core", "autenticacao", "accounts", "usuarios"):
            with self.subTest(app=app):
                self.assertFalse(apps.is_installed(app))

    def test_sem_modelos_de_dominio(self):
        for app in APPS_DE_DOMINIO:
            with self.subTest(app=app):
                self.assertEqual(list(apps.get_app_config(app).get_models()), [])


class MigrationsTests(TestCase):
    """makemigrations consulta o histórico no banco; por isso usa TestCase."""

    def test_sem_migrations_pendentes(self):
        call_command("makemigrations", "--check", "--dry-run", stdout=StringIO())

    def test_sem_migrations_de_dominio(self):
        for app in APPS_DE_DOMINIO:
            with self.subTest(app=app):
                pasta = settings.BASE_DIR / app / "migrations"
                arquivos = sorted(p.name for p in pasta.glob("*.py"))
                self.assertEqual(arquivos, ["__init__.py"])


class IdiomaEFusoTests(SimpleTestCase):
    def test_idioma_e_fuso(self):
        self.assertEqual(settings.LANGUAGE_CODE, "pt-br")
        self.assertEqual(settings.TIME_ZONE, "America/Recife")
        self.assertTrue(settings.USE_I18N)
        self.assertTrue(settings.USE_TZ)
        self.assertEqual(timezone.get_current_timezone_name(), "America/Recife")

    def test_data_atual_usa_o_dia_de_recife_e_nao_o_dia_utc(self):
        # 02:30 UTC de 02/11/2026 ainda é 01/11/2026 em Recife (UTC−3).
        instante = datetime(2026, 11, 2, 2, 30, tzinfo=UTC)
        self.assertEqual(timezone.localdate(instante), date(2026, 11, 1))


class EstruturaTests(SimpleTestCase):
    def test_templates_e_arquivos_estaticos(self):
        self.assertIn(settings.BASE_DIR / "templates", settings.TEMPLATES[0]["DIRS"])
        self.assertTrue(settings.TEMPLATES[0]["APP_DIRS"])
        self.assertEqual(settings.STATIC_URL, "/static/")
        self.assertIn(settings.BASE_DIR / "static", settings.STATICFILES_DIRS)
        self.assertEqual(settings.STATIC_ROOT, settings.BASE_DIR / "staticfiles")

    def test_whitenoise_logo_apos_o_security_middleware(self):
        middleware = settings.MIDDLEWARE
        posicao = middleware.index("django.middleware.security.SecurityMiddleware")
        self.assertEqual(
            middleware[posicao + 1], "whitenoise.middleware.WhiteNoiseMiddleware"
        )

    def test_desenvolvimento_usa_armazenamento_simples_de_estaticos(self):
        # Os testes rodam com DJANGO_DEBUG=True: sem manifesto nem collectstatic.
        self.assertEqual(
            settings.STORAGES["staticfiles"]["BACKEND"],
            "django.contrib.staticfiles.storage.StaticFilesStorage",
        )

    def test_mensagens_habilitadas(self):
        self.assertTrue(apps.is_installed("django.contrib.messages"))
        self.assertIn(
            "django.contrib.messages.context_processors.messages",
            settings.TEMPLATES[0]["OPTIONS"]["context_processors"],
        )

    def test_login_obrigatorio_apos_autenticacao(self):
        middleware = settings.MIDDLEWARE
        autenticacao = middleware.index(
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        )
        login_obrigatorio = middleware.index(
            "django.contrib.auth.middleware.LoginRequiredMiddleware"
        )
        self.assertGreater(login_obrigatorio, autenticacao)
        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", middleware)

    def test_autenticacao_nativa(self):
        self.assertEqual(
            settings.AUTHENTICATION_BACKENDS,
            ["django.contrib.auth.backends.ModelBackend"],
        )
        self.assertEqual(settings.AUTH_USER_MODEL, "auth.User")
        self.assertEqual(settings.LOGIN_URL, "login")
        self.assertEqual(settings.LOGOUT_REDIRECT_URL, "login")
        self.assertEqual(len(settings.AUTH_PASSWORD_VALIDATORS), 4)
