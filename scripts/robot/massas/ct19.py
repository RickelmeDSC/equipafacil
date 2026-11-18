"""Massa do CT19 — Filtrar histórico por situação.

Cria dois aluguéis em equipamentos diferentes:
um ativo e outro encerrado.
"""

from config.tests.fabricas import criar_cliente, criar_equipamento, encerrar, registrar


def preparar() -> None:
    cliente_ativo = criar_cliente(nome_completo="Cliente CT19 Ativo")
    equipamento_ativo = criar_equipamento(
        codigo="CT19-001",
        nome="Equipamento CT19 Ativo",
    )
    registrar(equipamento=equipamento_ativo, cliente=cliente_ativo)

    cliente_encerrado = criar_cliente(nome_completo="Cliente CT19 Encerrado")
    equipamento_encerrado = criar_equipamento(
        codigo="CT19-002",
        nome="Equipamento CT19 Encerrado",
    )
    aluguel_encerrado = registrar(
        equipamento=equipamento_encerrado,
        cliente=cliente_encerrado,
    )
    encerrar(aluguel_encerrado)
