"""Massa do CT03 — Consultar equipamento e verificar disponibilidade.

Três equipamentos fictícios, um para cada combinação de situação e
disponibilidade (Disponível = ativo e sem aluguel ativo):

- "FUR-001": ativo e sem aluguel — Disponível. É o equipamento pesquisado.
- "BET-001": ativo, com aluguel ativo de "João Silva" — Indisponível.
- "SER-001": inativo — Indisponível.

Os outros dois também provam que a pesquisa filtra: só o "FUR-001" pode
aparecer nas pesquisas por "FUR-001" e por "Furadeira".
"""

from decimal import Decimal

from config.tests.fabricas import criar_cliente, criar_equipamento, registrar
from equipamentos.models import Categoria


def preparar() -> None:
    criar_equipamento(
        codigo="FUR-001", nome="Furadeira Impacto", valor_diaria=Decimal("50.00")
    )
    betoneira = criar_equipamento(
        codigo="BET-001",
        nome="Betoneira 150 L",
        categoria=Categoria.CONSTRUCAO_CIVIL,
        valor_diaria=Decimal("80.00"),
    )
    criar_equipamento(
        codigo="SER-001",
        nome="Serra Circular",
        valor_diaria=Decimal("40.00"),
        ativo=False,
    )
    cliente = criar_cliente(nome_completo="João Silva", cpf="52998224725")
    registrar(equipamento=betoneira, cliente=cliente)
