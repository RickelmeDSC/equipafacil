"""Massa do CT07 — Excluir equipamento sem histórico.

- "FUR-001": sem nenhum aluguel. É o equipamento excluído pela tela.
- "BET-001": também sem aluguel. Não é tocado; existe para provar que a
  exclusão remove só o equipamento escolhido.
"""

from decimal import Decimal

from config.tests.fabricas import criar_equipamento
from equipamentos.models import Categoria


def preparar() -> None:
    criar_equipamento(
        codigo="FUR-001", nome="Furadeira Impacto", valor_diaria=Decimal("50.00")
    )
    criar_equipamento(
        codigo="BET-001",
        nome="Betoneira 150 L",
        categoria=Categoria.CONSTRUCAO_CIVIL,
        valor_diaria=Decimal("80.00"),
    )
