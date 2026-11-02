"""Registro de erros e mascaramento de dados sensíveis nos relatórios de erro."""

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
