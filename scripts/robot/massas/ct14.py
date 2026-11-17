"""Massa do CT14 — Impedir devolução de aluguel já encerrado.

Pré-condição: aluguel ativo do "FUR-001", registrado pelo serviço real como se
o registro tivesse sido feito ontem (``hoje=ontem``): retirada ontem, devolução
prevista amanhã, 3 diárias de R$ 50,00 = R$ 150,00.

O aluguel começa aberto de propósito. A tela não oferece "Registrar devolução"
para um aluguel encerrado; para a segunda devolução chegar ao backend, o
cenário abre a tela de devolução em uma aba, encerra o aluguel em outra e só
então confirma na primeira. A retirada é ontem para as duas tentativas usarem
datas diferentes (hoje na que vale, ontem na recusada).
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
