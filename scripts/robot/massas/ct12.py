"""Massa do CT12 — Impedir aluguel de equipamento indisponível.

O aluguel ativo do "FUR-001" é registrado pela tela, em uma segunda aba, depois
que a primeira aba já deixou o mesmo aluguel pronto para registrar: só assim a
segunda tentativa chega ao backend (a tela nunca oferece um equipamento
ocupado).

O segundo equipamento ("BET-001") não é alugado. Ele existe porque, sem nenhum
equipamento disponível, a tela troca o formulário por um aviso e a mensagem de
recusa do campo não apareceria.
"""

from decimal import Decimal

from config.tests.fabricas import criar_cliente, criar_equipamento


def preparar() -> None:
    criar_cliente(nome_completo="João Silva", cpf="52998224725")
    criar_cliente(nome_completo="Maria Souza")
    criar_equipamento(
        codigo="FUR-001", nome="Furadeira Impacto", valor_diaria=Decimal("50.00")
    )
    criar_equipamento(
        codigo="BET-001", nome="Betoneira 150 L", valor_diaria=Decimal("80.00")
    )
