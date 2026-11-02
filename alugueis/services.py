"""Serviço transacional de registro de aluguel (RF006, RN001, RN004, I1, D13).

Base para o DEV-06: aqui não há formulário nem view. O serviço recebe só
identificadores e datas; diária, diárias e valor são sempre recalculados a
partir do banco, nunca recebidos da tela (D13).
"""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from alugueis.models import Aluguel, calcular_diarias, calcular_valor_contratado
from clientes.models import Cliente
from config import mensagens
from equipamentos.models import Equipamento


def registrar_aluguel(
    *,
    cliente_id: int,
    equipamento_id: int,
    data_retirada: date,
    data_devolucao_prevista: date,
    hoje: date | None = None,
) -> Aluguel:
    """Registra um aluguel aberto, com valores congelados.

    No PostgreSQL, bloqueia a linha do equipamento e depois a do cliente (sempre
    nessa ordem) antes de revalidar a disponibilidade; a restrição única parcial
    é a última barreira. No SQLite, ``select_for_update()`` não tem efeito.
    """
    hoje = hoje or timezone.localdate()
    if data_retirada < hoje:
        raise ValidationError({"data_retirada": mensagens.RETIRADA_NO_PASSADO})
    if data_devolucao_prevista < data_retirada:
        raise ValidationError(
            {"data_devolucao_prevista": mensagens.PREVISTA_ANTES_DA_RETIRADA}
        )

    with transaction.atomic():
        try:
            equipamento = Equipamento.objects.select_for_update().get(pk=equipamento_id)
        except Equipamento.DoesNotExist:
            # Inclui o equipamento excluído enquanto este registro esperava o bloqueio.
            raise ValidationError(
                {"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL}
            ) from None
        cliente = Cliente.objects.select_for_update().get(pk=cliente_id)
        if not equipamento.disponivel:
            raise ValidationError({"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL})

        quantidade_diarias = calcular_diarias(data_retirada, data_devolucao_prevista)
        aluguel = Aluguel(
            equipamento=equipamento,
            cliente=cliente,
            data_retirada=data_retirada,
            data_devolucao_prevista=data_devolucao_prevista,
            valor_diaria_contratada=equipamento.valor_diaria,
            quantidade_diarias=quantidade_diarias,
            valor_contratado=calcular_valor_contratado(
                quantidade_diarias, equipamento.valor_diaria
            ),
        )
        try:
            with transaction.atomic():
                aluguel.save()
        except IntegrityError:
            raise ValidationError(
                {"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL}
            ) from None
    return aluguel
