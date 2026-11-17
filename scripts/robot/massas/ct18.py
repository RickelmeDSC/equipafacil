
"""Massa do CT18 — Pesquisar cliente inexistente."""

from config.tests.fabricas import criar_cliente


def preparar() -> None:
    criar_cliente(nome_completo="João Silva")
