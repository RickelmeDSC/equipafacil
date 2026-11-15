"""Massa do CT11 — Registrar aluguel e calcular corretamente o valor.

Pré-condição: cliente e equipamento "FUR-001" (diária de R$ 50,00) cadastrados
e disponíveis. Nenhum aluguel é criado: o registro é feito pela tela.
"""

from decimal import Decimal

from config.tests.fabricas import criar_cliente, criar_equipamento


def preparar() -> None:
    criar_cliente(nome_completo="João Silva", cpf="52998224725")
    criar_equipamento(
        codigo="FUR-001", nome="Furadeira Impacto", valor_diaria=Decimal("50.00")
    )
