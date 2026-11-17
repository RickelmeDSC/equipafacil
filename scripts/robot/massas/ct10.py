"""Massa do CT10 — Impedir cadastro com CPF duplicado."""

from config.tests.fabricas import criar_cliente


def preparar() -> None:
    criar_cliente(
        nome_completo="João Silva",
        cpf="52998224725",
    )
