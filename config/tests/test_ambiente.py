"""Separação da configuração sensível: variáveis de ambiente, .env e banco."""

import os
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.env import (
    carregar_arquivo_env,
    configurar_banco,
    exigir_banco_local_para_testes,
    obter_booleano,
    obter_inteiro,
    obter_lista,
    obter_obrigatorio,
    validar_chave_secreta,
)

BASE_DIR = Path(settings.BASE_DIR)
BOM = chr(0xFEFF)


class LeituraDeVariaveisTests(SimpleTestCase):
    def test_obrigatoria_ausente_falha_sem_expor_valor(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DJANGO_SECRET_KEY"):
            obter_obrigatorio("DJANGO_SECRET_KEY", {})
        with self.assertRaises(ImproperlyConfigured):
            obter_obrigatorio("DJANGO_SECRET_KEY", {"DJANGO_SECRET_KEY": "   "})

    def test_booleanos(self):
        for valor, esperado in (
            ("True", True),
            ("1", True),
            ("false", False),
            ("0", False),
        ):
            with self.subTest(valor=valor):
                self.assertIs(obter_booleano("X", False, {"X": valor}), esperado)
        self.assertIs(obter_booleano("X", True, {}), True)
        with self.assertRaises(ImproperlyConfigured):
            obter_booleano("X", False, {"X": "talvez"})

    def test_inteiros_e_listas(self):
        self.assertEqual(obter_inteiro("X", 0, {"X": "3600"}), 3600)
        self.assertEqual(obter_inteiro("X", 7, {}), 7)
        with self.assertRaises(ImproperlyConfigured):
            obter_inteiro("X", 0, {"X": "-1"})
        self.assertEqual(
            obter_lista("X", {"X": " a.test, ,b.test "}), ["a.test", "b.test"]
        )
        self.assertEqual(obter_lista("X", {}), [])


class ChaveSecretaTests(SimpleTestCase):
    def test_desenvolvimento_aceita_chave_curta(self):
        validar_chave_secreta("troque-por-uma-chave-gerada-localmente", debug=True)

    def test_producao_recusa_chave_fraca_sem_expor_o_valor(self):
        fracas = (
            "troque-por-uma-chave-gerada-localmente",
            "a" * 60,
            "django-insecure-" + secrets.token_urlsafe(50),
        )
        for chave in fracas:
            with self.subTest(tamanho=len(chave)):
                with self.assertRaises(ImproperlyConfigured) as erro:
                    validar_chave_secreta(chave, debug=False)
                self.assertIn("DJANGO_SECRET_KEY", str(erro.exception))
                self.assertNotIn(chave, str(erro.exception))

    def test_producao_aceita_chave_gerada(self):
        validar_chave_secreta(secrets.token_urlsafe(50), debug=False)


class ArquivoEnvTests(SimpleTestCase):
    def _arquivo(self, conteudo: str) -> Path:
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        caminho = Path(pasta.name) / ".env"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def test_le_valores_sem_sobrescrever_o_ambiente(self):
        caminho = self._arquivo(
            "# comentário\n\nA=1\nexport B='dois'\nC=\"três\"\nD=do-arquivo\n"
        )
        ambiente = {"D": "do-ambiente"}
        carregar_arquivo_env(caminho, ambiente)
        self.assertEqual(
            ambiente, {"A": "1", "B": "dois", "C": "três", "D": "do-ambiente"}
        )

    def test_linha_invalida_falha_sem_expor_conteudo(self):
        caminho = self._arquivo("VALOR_SECRETO_SEM_CHAVE\n")
        with self.assertRaises(ImproperlyConfigured) as erro:
            carregar_arquivo_env(caminho, {})
        self.assertIn("Linha 1", str(erro.exception))
        self.assertNotIn("VALOR_SECRETO_SEM_CHAVE", str(erro.exception))

    def test_arquivo_com_bom_utf8_e_lido(self):
        # Set-Content/Out-File do PowerShell 5.1 gravam UTF-8 com BOM.
        caminho = self._arquivo(BOM + "# comentário\nA=1\n")
        ambiente: dict[str, str] = {}
        carregar_arquivo_env(caminho, ambiente)
        self.assertEqual(ambiente, {"A": "1"})
        caminho = self._arquivo(BOM + "B=2\n")
        carregar_arquivo_env(caminho, ambiente)
        self.assertEqual(ambiente, {"A": "1", "B": "2"})

    def test_arquivo_ausente_e_ignorado(self):
        ambiente: dict[str, str] = {}
        carregar_arquivo_env(BASE_DIR / "arquivo-inexistente.env", ambiente)
        self.assertEqual(ambiente, {})


class BancoDeDadosTests(SimpleTestCase):
    def test_postgresql_e_o_padrao_e_exige_nome_e_usuario(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DB_NAME"):
            configurar_banco({}, BASE_DIR, debug=True)
        banco = configurar_banco(
            {"DB_NAME": "equipafacil", "DB_USER": "equipafacil"}, BASE_DIR, debug=True
        )["default"]
        self.assertEqual(banco["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(banco["HOST"], "localhost")
        self.assertEqual(banco["PORT"], "5432")
        self.assertEqual(banco["OPTIONS"], {"sslmode": "prefer"})
        self.assertEqual(banco["TEST"], {"CHARSET": "UTF8", "TEMPLATE": "template0"})

    def test_postgresql_respeita_sslmode(self):
        banco = configurar_banco(
            {"DB_NAME": "n", "DB_USER": "u", "DB_SSLMODE": "require"},
            BASE_DIR,
            debug=False,
        )["default"]
        self.assertEqual(banco["OPTIONS"]["sslmode"], "require")

    def test_sqlite_so_no_desenvolvimento(self):
        banco = configurar_banco({"DB_ENGINE": "sqlite"}, BASE_DIR, debug=True)
        self.assertEqual(banco["default"]["ENGINE"], "django.db.backends.sqlite3")
        with self.assertRaisesMessage(ImproperlyConfigured, "DJANGO_DEBUG=True"):
            configurar_banco({"DB_ENGINE": "sqlite"}, BASE_DIR, debug=False)

    def test_motor_desconhecido_falha(self):
        with self.assertRaises(ImproperlyConfigured):
            configurar_banco({"DB_ENGINE": "mysql"}, BASE_DIR, debug=True)


URL_NEON_FICTICIA = (
    "postgresql://usuario_app:s%40nha%3Aficticia@ep-exemplo-123456.sa-east-1"
    ".aws.neon.tech/equipafacil?sslmode=require&channel_binding=require"
)


class DatabaseUrlTests(SimpleTestCase):
    def test_url_completa_com_senha_codificada_e_opcoes(self):
        banco = configurar_banco({"DATABASE_URL": URL_NEON_FICTICIA}, BASE_DIR, False)
        banco = banco["default"]
        self.assertEqual(banco["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(banco["NAME"], "equipafacil")
        self.assertEqual(banco["USER"], "usuario_app")
        self.assertEqual(banco["PASSWORD"], "s@nha:ficticia")
        self.assertEqual(banco["HOST"], "ep-exemplo-123456.sa-east-1.aws.neon.tech")
        self.assertEqual(banco["PORT"], "5432")
        self.assertEqual(
            banco["OPTIONS"], {"sslmode": "require", "channel_binding": "require"}
        )
        self.assertEqual(banco["TEST"], {"CHARSET": "UTF8", "TEMPLATE": "template0"})

    def test_url_sem_sslmode_usa_require(self):
        banco = configurar_banco(
            {"DATABASE_URL": "postgres://app@db.exemplo.test:6543/equipafacil"},
            BASE_DIR,
            debug=False,
        )["default"]
        self.assertEqual(banco["OPTIONS"], {"sslmode": "require"})
        self.assertEqual(banco["PORT"], "6543")
        self.assertEqual(banco["PASSWORD"], "")

    def test_url_tem_precedencia_sobre_as_variaveis_db(self):
        ambiente = {
            "DATABASE_URL": URL_NEON_FICTICIA,
            "DB_NAME": "equipafacil_dev",
            "DB_USER": "equipafacil_dev",
            "DB_HOST": "127.0.0.1",
        }
        banco = configurar_banco(ambiente, BASE_DIR, debug=False)["default"]
        self.assertEqual(banco["NAME"], "equipafacil")
        self.assertEqual(banco["HOST"], "ep-exemplo-123456.sa-east-1.aws.neon.tech")

    def test_url_junto_com_sqlite_explicito_falha(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DATABASE_URL"):
            configurar_banco(
                {"DATABASE_URL": URL_NEON_FICTICIA, "DB_ENGINE": "sqlite"},
                BASE_DIR,
                debug=True,
            )

    def test_url_invalida_falha_sem_expor_a_senha(self):
        invalidas = (
            "mysql://usuario:segredo-nao-exibir@db.exemplo.test/equipafacil",
            "postgresql://usuario:segredo-nao-exibir@db.exemplo.test:porta/banco",
            "postgresql://usuario:segredo-nao-exibir@db.exemplo.test/",
            "postgresql://:segredo-nao-exibir@db.exemplo.test/equipafacil",
            "postgresql://usuario:segredo-nao-exibir@/equipafacil",
        )
        for url in invalidas:
            with self.subTest(url=url.split("@")[-1]):
                with self.assertRaises(ImproperlyConfigured) as erro:
                    configurar_banco({"DATABASE_URL": url}, BASE_DIR, debug=True)
                self.assertIsNone(erro.exception.__cause__)
                self.assertNotIn("segredo-nao-exibir", str(erro.exception))
                self.assertIn("DATABASE_URL", str(erro.exception))


class TlsEConexoesTests(SimpleTestCase):
    def test_fora_do_desenvolvimento_exige_tls(self):
        inseguras = (
            {"DB_NAME": "n", "DB_USER": "u"},
            {"DB_NAME": "n", "DB_USER": "u", "DB_SSLMODE": "disable"},
            {"DATABASE_URL": "postgresql://u@db.exemplo.test/n?sslmode=prefer"},
        )
        for ambiente in inseguras:
            with self.subTest(ambiente=sorted(ambiente)):
                with self.assertRaisesMessage(ImproperlyConfigured, "sslmode"):
                    configurar_banco(ambiente, BASE_DIR, debug=False)
        for modo in ("require", "verify-ca", "verify-full"):
            with self.subTest(modo=modo):
                configurar_banco(
                    {"DB_NAME": "n", "DB_USER": "u", "DB_SSLMODE": modo},
                    BASE_DIR,
                    debug=False,
                )

    def test_desenvolvimento_aceita_banco_local_sem_tls(self):
        banco = configurar_banco({"DB_NAME": "n", "DB_USER": "u"}, BASE_DIR, True)
        self.assertEqual(banco["default"]["OPTIONS"]["sslmode"], "prefer")

    def test_tempo_de_vida_das_conexoes(self):
        padrao = configurar_banco({"DB_NAME": "n", "DB_USER": "u"}, BASE_DIR, True)
        self.assertEqual(padrao["default"]["CONN_MAX_AGE"], 0)
        self.assertTrue(padrao["default"]["CONN_HEALTH_CHECKS"])
        reuso = configurar_banco(
            {"DB_NAME": "n", "DB_USER": "u", "DB_CONN_MAX_AGE": "60"}, BASE_DIR, True
        )
        self.assertEqual(reuso["default"]["CONN_MAX_AGE"], 60)


class BancoDosTestesTests(SimpleTestCase):
    def test_testes_aceitam_somente_banco_local(self):
        for host in ("127.0.0.1", "localhost", "::1", ""):
            with self.subTest(host=host):
                exigir_banco_local_para_testes(
                    {"ENGINE": "django.db.backends.postgresql", "HOST": host}
                )
        exigir_banco_local_para_testes(
            {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}
        )
        with self.assertRaisesMessage(ImproperlyConfigured, "local"):
            exigir_banco_local_para_testes(
                {
                    "ENGINE": "django.db.backends.postgresql",
                    "HOST": "ep-exemplo-123456.sa-east-1.aws.neon.tech",
                }
            )

    def test_suite_atual_roda_em_banco_local(self):
        exigir_banco_local_para_testes(settings.DATABASES["default"])


class SettingsEmProcessoSeparadoTests(SimpleTestCase):
    """Carrega config.settings em outro processo, com ambiente controlado."""

    _CODIGO_PADRAO = (
        "from django.conf import settings as s; "
        "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, "
        "s.SECURE_SSL_REDIRECT, s.DATABASES['default']['ENGINE'])"
    )

    def _executar(
        self,
        variaveis: dict[str, str],
        codigo: str = _CODIGO_PADRAO,
        argumentos: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        ambiente = {
            chave: valor
            for chave, valor in os.environ.items()
            if not chave.startswith(("DJANGO_", "DB_", "DATABASE_URL", "RENDER"))
        }
        ambiente.update(
            {
                "DJANGO_ENV_FILE": "",
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "PYTHONIOENCODING": "utf-8",
            }
        )
        ambiente.update(variaveis)
        return subprocess.run(
            [sys.executable, *(argumentos or ["-c", codigo])],
            cwd=BASE_DIR,
            env=ambiente,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )

    def test_sem_secret_key_nao_inicializa(self):
        resultado = self._executar({"DJANGO_DEBUG": "True", "DB_ENGINE": "sqlite"})
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", resultado.stderr)

    def test_producao_simulada_usa_cookies_seguros_e_https(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DB_ENGINE": "postgresql",
                "DB_NAME": "equipafacil",
                "DB_USER": "equipafacil",
                "DB_SSLMODE": "require",
            }
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(
            resultado.stdout.split(),
            ["False", "True", "True", "True", "django.db.backends.postgresql"],
        )

    def test_producao_simulada_recusa_sqlite(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DB_ENGINE": "sqlite",
            }
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("DB_ENGINE=sqlite", resultado.stderr)

    def test_producao_simulada_recusa_a_chave_do_env_example(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": "troque-por-uma-chave-gerada-localmente",
                "DJANGO_DEBUG": "False",
                "DB_NAME": "equipafacil",
                "DB_USER": "equipafacil",
            }
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", resultado.stderr)
        self.assertNotIn("troque-por-uma-chave-gerada-localmente", resultado.stderr)

    def test_debug_desativado_por_padrao(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DB_NAME": "equipafacil",
                "DB_USER": "equipafacil",
                "DB_SSLMODE": "require",
            }
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout.split()[0], "False")

    def test_producao_simulada_com_database_url(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DATABASE_URL": URL_NEON_FICTICIA,
            },
            codigo=(
                "from django.conf import settings as s; d = s.DATABASES['default']; "
                "print(d['ENGINE'], d['HOST'], d['OPTIONS']['sslmode'])"
            ),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(
            resultado.stdout.split(),
            [
                "django.db.backends.postgresql",
                "ep-exemplo-123456.sa-east-1.aws.neon.tech",
                "require",
            ],
        )
        self.assertNotIn("ficticia", resultado.stdout + resultado.stderr)

    def test_producao_simulada_recusa_conexao_sem_tls(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DB_NAME": "equipafacil",
                "DB_USER": "equipafacil",
            }
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("sslmode", resultado.stderr)

    def test_manage_py_test_recusa_banco_remoto(self):
        # Só lê a configuração: --help não conecta a nenhum banco.
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "True",
                "DATABASE_URL": URL_NEON_FICTICIA,
            },
            argumentos=["manage.py", "test", "--help"],
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("PostgreSQL local", resultado.stderr)
        self.assertNotIn("ficticia", resultado.stderr)

    def test_producao_simulada_usa_manifesto_comprimido_do_whitenoise(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DB_NAME": "equipafacil",
                "DB_USER": "equipafacil",
                "DB_SSLMODE": "require",
            },
            codigo=(
                "from django.conf import settings as s; "
                "print(s.STORAGES['staticfiles']['BACKEND'])"
            ),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(
            resultado.stdout.strip(),
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )

    def test_producao_simulada_no_render(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DATABASE_URL": URL_NEON_FICTICIA,
                "RENDER_EXTERNAL_HOSTNAME": "equipafacil.onrender.com",
                "DJANGO_SECURE_PROXY_SSL_HEADER": "True",
            },
            codigo=(
                "from django.conf import settings as s; "
                "print(s.ALLOWED_HOSTS, s.SECURE_PROXY_SSL_HEADER, "
                "s.SECURE_SSL_REDIRECT, s.SECURE_HSTS_SECONDS)"
            ),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(
            resultado.stdout.strip(),
            "['equipafacil.onrender.com'] ('HTTP_X_FORWARDED_PROTO', 'https') True 0",
        )

    def test_proxy_desligado_e_hsts_configuravel(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DJANGO_DEBUG": "False",
                "DATABASE_URL": URL_NEON_FICTICIA,
                "DJANGO_ALLOWED_HOSTS": "equipafacil.exemplo.test",
                "DJANGO_SECURE_HSTS_SECONDS": "3600",
            },
            codigo=(
                "from django.conf import settings as s; "
                "print(s.ALLOWED_HOSTS, s.SECURE_PROXY_SSL_HEADER, "
                "s.SECURE_HSTS_SECONDS)"
            ),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(
            resultado.stdout.strip(), "['equipafacil.exemplo.test'] None 3600"
        )


class SegredosNaoVersionadosTests(SimpleTestCase):
    def test_settings_sem_segredo_literal(self):
        fonte = (BASE_DIR / "config" / "settings.py").read_text(encoding="utf-8")
        self.assertNotIn("django-insecure", fonte)
        self.assertIsNone(re.search(r"SECRET_KEY\s*=\s*[\"']", fonte))

    def test_env_example_sem_chave_real(self):
        exemplo = (BASE_DIR / ".env.example").read_text(encoding="utf-8")
        self.assertIn(
            "DJANGO_SECRET_KEY=troque-por-uma-chave-gerada-localmente", exemplo
        )
        self.assertNotIn("django-insecure", exemplo)
        self.assertNotRegex(exemplo, r"postgres(ql)?://\S+:\S+@")
