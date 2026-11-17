
"""Massa do CT17 — Pesquisar cliente pelo nome."""

from config.tests.fabricas import criar_cliente


def preparar() -> None:
    criar_cliente(nome_completo="Maria QA Pesquisa")
    criar_cliente(nome_completo="João Silva")
