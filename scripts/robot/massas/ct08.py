from decimal import Decimal

from alugueis.services import registrar_aluguel, registrar_devolucao
from config.tests.fabricas import criar_cliente, criar_equipamento, dias


def preparar() -> None:
    cliente = criar_cliente(nome_completo="João Silva", cpf="52998224725")
    equipamento = criar_equipamento(
        codigo="FUR-001",
        nome="Furadeira Impacto",
        valor_diaria=Decimal("50.00"),
    )

    # Aluguel antigo, já encerrado
    retirada = dias(-5)
    prevista = dias(-3)
    devolvida = dias(-1)

    aluguel = registrar_aluguel(
        cliente_id=cliente.pk,
        equipamento_id=equipamento.pk,
        data_retirada=retirada,
        data_devolucao_prevista=prevista,
        hoje=retirada,
    )
    registrar_devolucao(
        aluguel_id=aluguel.pk,
        data_devolucao_real=devolvida,
    )
