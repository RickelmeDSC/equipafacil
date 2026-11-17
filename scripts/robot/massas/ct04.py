from decimal import Decimal

from config.tests.fabricas import criar_equipamento


def preparar() -> None:
    criar_equipamento(
        codigo="FUR-001",
        nome="Furadeira Impacto",
        valor_diaria=Decimal("50.00"),
    )