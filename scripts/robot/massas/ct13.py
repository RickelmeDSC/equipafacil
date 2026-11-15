"""Massa do CT13 — Registrar devolução e liberar equipamento.

Pré-condição: aluguel ativo do "FUR-001". O documento usa retirada em
01/11/2026 e devolução em 02/11/2026, datas que já passaram; aqui a retirada é
ontem e a devolução (feita pela tela) é hoje, mantendo um dia entre as duas.

O aluguel é registrado pelo serviço real, como se o registro tivesse sido feito
ontem (``hoje=ontem``): retirada ontem, devolução prevista amanhã, 3 diárias de
R$ 50,00 = R$ 150,00.
"""

from decimal import Decimal

from alugueis.services import registrar_aluguel
from config.tests.fabricas import criar_cliente, criar_equipamento, dias


def preparar() -> None:
    cliente = criar_cliente(nome_completo="João Silva", cpf="52998224725")
    equipamento = criar_equipamento(
        codigo="FUR-001", nome="Furadeira Impacto", valor_diaria=Decimal("50.00")
    )
    ontem = dias(-1)
    registrar_aluguel(
        cliente_id=cliente.pk,
        equipamento_id=equipamento.pk,
        data_retirada=ontem,
        data_devolucao_prevista=dias(1),
        hoje=ontem,
    )
