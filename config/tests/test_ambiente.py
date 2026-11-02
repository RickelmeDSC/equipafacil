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
    obter_booleano,
    obter_inteiro,
    obter_lista,
    obter_obrigatorio,
)

BASE_DIR = Path(settings.BASE_DIR)


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

    def test_arquivo_ausente_e_ignorado(self):
        ambiente: dict[str, str] = {}
        carregar_arquivo_env(BASE_DIR / "arquivo-inexistente.env", ambiente)
        self.assertEqual(ambiente, {})


class BancoDeDadosTests(SimpleTestCase):
    def test_postgresql_e_o_padrao_e_exige_nome_e_usuario(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DB_NAME"):
            configurar_banco({}, BASE_DIR, debug=True)
        banco = configurar_banco(
            {"DB_NAME": "equipafacil", "DB_USER": "equipafacil"}, BASE_DIR, debug=False
        )["default"]
        self.assertEqual(banco["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(banco["HOST"], "localhost")
        self.assertEqual(banco["PORT"], "5432")
        self.assertEqual(banco["OPTIONS"], {"sslmode": "prefer"})

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


class SettingsEmProcessoSeparadoTests(SimpleTestCase):
    """Carrega config.settings em outro processo, com ambiente controlado."""

    def _executar(self, variaveis: dict[str, str]) -> subprocess.CompletedProcess:
        ambiente = {
            chave: valor
            for chave, valor in os.environ.items()
            if not chave.startswith(("DJANGO_", "DB_"))
        }
        ambiente.update(
            {
                "DJANGO_ENV_FILE": "",
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "PYTHONIOENCODING": "utf-8",
            }
        )
        ambiente.update(variaveis)
        codigo = (
            "from django.conf import settings as s; "
            "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, "
            "s.SECURE_SSL_REDIRECT, s.DATABASES['default']['ENGINE'])"
        )
        return subprocess.run(
            [sys.executable, "-c", codigo],
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

    def test_debug_desativado_por_padrao(self):
        resultado = self._executar(
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
                "DB_NAME": "equipafacil",
                "DB_USER": "equipafacil",
            }
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout.split()[0], "False")


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
