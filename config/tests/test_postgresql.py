"""Verificações que só rodam quando o banco configurado é PostgreSQL.

Com SQLite (desenvolvimento temporário), estes testes são pulados e aparecem
como "skipped" no resultado. Não substituem os testes de restrições e
concorrência, que dependem dos modelos de DEV-03.
"""

from unittest import skipUnless

from django.conf import settings
from django.db import connection
from django.test import TestCase

POSTGRESQL = connection.vendor == "postgresql"


@skipUnless(POSTGRESQL, "banco configurado não é PostgreSQL")
class PostgreSQLTests(TestCase):
    def test_versao_suportada_pelo_django_5_2(self):
        # Django 5.2 exige PostgreSQL 14 ou superior.
        self.assertGreaterEqual(connection.pg_version, 140000)

    def test_conexao_em_utc_com_use_tz(self):
        self.assertTrue(settings.USE_TZ)
        with connection.cursor() as cursor:
            cursor.execute("SHOW TimeZone")
            self.assertEqual(cursor.fetchone()[0], "UTC")

    def test_codificacao_utf8(self):
        # Instalações no Windows podem criar bancos em WIN1252; o projeto usa UTF8.
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_encoding")
            self.assertEqual(cursor.fetchone()[0], "UTF8")
