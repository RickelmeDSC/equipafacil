"""Registro de erros e mascaramento de dados sensíveis nos relatórios de erro."""

import io
import logging
import sys

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.views.debug import (
    get_default_exception_reporter_filter,
    technical_500_response,
)

# A página de erro mostra o código-fonte em volta do erro; por isso os testes
# usam SENHA, e não o valor literal, perto do raise.
SENHA = "senha-ficticia-123"
URL_COM_SENHA = f"postgresql://app:{SENHA}@db.exemplo.test/banco"


class RegistroDeErrosTests(SimpleTestCase):
    def test_erros_do_django_vao_para_o_console_mesmo_sem_debug(self):
        # Sem isso, com DEBUG desativado o Django só envia erros por e-mail a
        # ADMINS, que não existe, e as falhas 500 não apareceriam no Render.
        manipuladores = logging.getLogger("django").handlers
        console = [h for h in manipuladores if isinstance(h, logging.StreamHandler)]
        self.assertEqual(len(console), 1)
        self.assertEqual(console[0].filters, [])
        saida = io.StringIO()
        fluxo_original = console[0].setStream(saida)
        try:
            with override_settings(DEBUG=False):
                logging.getLogger("django.request").error("falha de teste 500")
        finally:
            console[0].setStream(fluxo_original)
        self.assertIn("falha de teste 500", saida.getvalue())


class FiltroDeRelatorioTests(SimpleTestCase):
    def test_database_url_e_mascarada_em_request_meta(self):
        requisicao = RequestFactory().get(
            "/", DATABASE_URL=URL_COM_SENHA, DJANGO_SECRET_KEY="chave-ficticia"
        )
        meta = get_default_exception_reporter_filter().get_safe_request_meta(requisicao)
        self.assertNotIn(SENHA, meta["DATABASE_URL"])
        self.assertNotIn("chave-ficticia", meta["DJANGO_SECRET_KEY"])

    @override_settings(DEBUG=True)
    def test_pagina_de_erro_de_desenvolvimento_nao_mostra_a_url(self):
        # O runserver copia o ambiente do processo para request.META.
        requisicao = RequestFactory().get("/", DATABASE_URL=URL_COM_SENHA)
        try:
            raise RuntimeError("erro de teste")
        except RuntimeError:
            resposta = technical_500_response(requisicao, *sys.exc_info())
        self.assertEqual(resposta.status_code, 500)
        self.assertNotIn(SENHA.encode(), resposta.content)
