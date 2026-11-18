"""Massa do CT20 — Verificar ausência de aluguéis com atraso.

Cria dois aluguéis em equipamentos diferentes:
um ativo e outro encerrado.
"""

from config.tests.fabricas import criar_cliente, criar_equipamento, registrar, encerrar


def preparar() -> None:
    cliente_ativo = criar_cliente(nome_completo="Cliente CT20 Ativo")
    equipamento_ativo = criar_equipamento(
        codigo="CT20-001",
        nome="Equipamento CT20 Ativo",
    )
    registrar(equipamento=equipamento_ativo, cliente=cliente_ativo)

    cliente_encerrado = criar_cliente(nome_completo="Cliente CT20 Encerrado")
    equipamento_encerrado = criar_equipamento(
        codigo="CT20-002",
        nome="Equipamento CT20 Encerrado",
    )
    aluguel_encerrado = registrar(
        equipamento=equipamento_encerrado,
        cliente=cliente_encerrado,
    )
    encerrar(aluguel_encerrado)