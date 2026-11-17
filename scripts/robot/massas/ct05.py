"""Massa do CT05 — Editar equipamento sem alterar valores de aluguéis anteriores.

Pré-condição: "FUR-001" a R$ 50,00/dia com um aluguel anterior, já encerrado,
de 3 diárias e R$ 150,00.

O aluguel é registrado e devolvido pelos serviços reais, com datas relativas à
execução: retirada há cinco dias, devolução prevista e real há três dias.
"""

from decimal import Decimal

from alugueis.services import registrar_aluguel, registrar_devolucao
from config.tests.fabricas import criar_cliente, criar_equipamento, dias


def preparar() -> None:
    cliente = criar_cliente(nome_completo="João Silva", cpf="52998224725")
    equipamento = criar_equipamento(
        codigo="FUR-001",
        nome="Furadeira Impacto",
        valor_diaria=Decimal("50.00"),
        descricao="Furadeira profissional",
    )
    retirada = dias(-5)
    devolucao = dias(-3)
    aluguel = registrar_aluguel(
        cliente_id=cliente.pk,
        equipamento_id=equipamento.pk,
        data_retirada=retirada,
        data_devolucao_prevista=devolucao,
        hoje=retirada,
    )
    registrar_devolucao(aluguel_id=aluguel.pk, data_devolucao_real=devolucao)
