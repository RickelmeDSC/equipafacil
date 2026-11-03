"""Serviços transacionais de aluguel e devolução (RF006, RF007, RN001, RN004, I1, I2, D13).

O serviço recebe só identificadores e datas; diária, diárias e valor são sempre
recalculados a partir do banco, nunca recebidos da tela (D13). A prévia usa as
mesmas funções de cálculo do registro, sem gravar nada.

Protocolo de bloqueios (PostgreSQL; no SQLite ``select_for_update()`` não tem
efeito), sempre com a linha do equipamento primeiro:

- registro de aluguel: equipamento → cliente;
- devolução: equipamento → aluguel;
- edição, exclusão, inativação e reativação de equipamento: só o equipamento;
- edição de cliente: só o cliente.

Ninguém espera por um equipamento segurando um cliente ou um aluguel, então não
há ciclo de espera. O índice único parcial ``aluguel_um_aberto_por_equipamento``
continua sendo a última barreira contra dois aluguéis abertos.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from alugueis.models import Aluguel, calcular_diarias, calcular_valor_contratado
from clientes.models import Cliente
from config import mensagens
from equipamentos.models import Equipamento


@dataclass(frozen=True)
class ResumoDoAluguel:
    """Valores calculados no backend (D13). Na prévia, são só informativos."""

    quantidade_diarias: int
    valor_diaria: Decimal
    valor_previsto: Decimal


def calcular_resumo(
    valor_diaria: Decimal, data_retirada: date, data_devolucao_prevista: date
) -> ResumoDoAluguel:
    """Diárias inclusivas e valor em Decimal (RN004 d, e)."""
    quantidade = calcular_diarias(data_retirada, data_devolucao_prevista)
    return ResumoDoAluguel(
        quantidade_diarias=quantidade,
        valor_diaria=valor_diaria,
        valor_previsto=calcular_valor_contratado(quantidade, valor_diaria),
    )


def validar_datas_do_aluguel(
    data_retirada: date, data_devolucao_prevista: date, hoje: date
) -> None:
    """Retirada não anterior a hoje (America/Recife; futura permitida, I1) e prevista ≥ retirada."""
    erros = {}
    if data_retirada < hoje:
        erros["data_retirada"] = mensagens.RETIRADA_NO_PASSADO
    if data_devolucao_prevista < data_retirada:
        erros["data_devolucao_prevista"] = mensagens.PREVISTA_ANTES_DA_RETIRADA
    if erros:
        raise ValidationError(erros)


def simular_aluguel(
    *,
    cliente_id: int,
    equipamento_id: int,
    data_retirada: date,
    data_devolucao_prevista: date,
    hoje: date | None = None,
) -> ResumoDoAluguel:
    """Prévia de P07 (D13): valida como o registro, calcula e não grava nada.

    Sem bloqueio: o registro revalida tudo dentro da transação.
    """
    hoje = hoje or timezone.localdate()
    validar_datas_do_aluguel(data_retirada, data_devolucao_prevista, hoje)
    if not Cliente.objects.filter(pk=cliente_id).exists():
        raise ValidationError({"cliente": mensagens.CLIENTE_INEXISTENTE})
    equipamento = Equipamento.objects.disponiveis().filter(pk=equipamento_id).first()
    if equipamento is None:
        raise ValidationError({"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL})
    return calcular_resumo(
        equipamento.valor_diaria, data_retirada, data_devolucao_prevista
    )


def registrar_aluguel(
    *,
    cliente_id: int,
    equipamento_id: int,
    data_retirada: date,
    data_devolucao_prevista: date,
    hoje: date | None = None,
) -> Aluguel:
    """Registra um aluguel aberto, com valores congelados (RF006).

    Bloqueia a linha do equipamento e depois a do cliente antes de revalidar a
    disponibilidade; a restrição única parcial é a última barreira.
    """
    hoje = hoje or timezone.localdate()
    validar_datas_do_aluguel(data_retirada, data_devolucao_prevista, hoje)

    with transaction.atomic():
        try:
            equipamento = Equipamento.objects.select_for_update().get(pk=equipamento_id)
        except Equipamento.DoesNotExist:
            # Inclui o equipamento excluído enquanto este registro esperava o bloqueio.
            raise ValidationError(
                {"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL}
            ) from None
        try:
            cliente = Cliente.objects.select_for_update().get(pk=cliente_id)
        except Cliente.DoesNotExist:
            raise ValidationError({"cliente": mensagens.CLIENTE_INEXISTENTE}) from None
        if not equipamento.disponivel:
            raise ValidationError({"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL})

        resumo = calcular_resumo(
            equipamento.valor_diaria, data_retirada, data_devolucao_prevista
        )
        aluguel = Aluguel(
            equipamento=equipamento,
            cliente=cliente,
            data_retirada=data_retirada,
            data_devolucao_prevista=data_devolucao_prevista,
            valor_diaria_contratada=resumo.valor_diaria,
            quantidade_diarias=resumo.quantidade_diarias,
            valor_contratado=resumo.valor_previsto,
        )
        try:
            with transaction.atomic():
                aluguel.save()
        except IntegrityError:
            raise ValidationError(
                {"equipamento": mensagens.EQUIPAMENTO_INDISPONIVEL}
            ) from None
    return aluguel


def registrar_devolucao(
    *, aluguel_id: int, data_devolucao_real: date, hoje: date | None = None
) -> Aluguel:
    """Grava a devolução uma única vez (RF007, RN004, I1, I2).

    Data real entre a retirada e a data atual em America/Recife. Atraso é só
    indicado pela situação calculada: sem multa e sem recálculo do valor. A
    gravação é condicional ("só se ainda aberto"), além do bloqueio da linha.
    """
    hoje = hoje or timezone.localdate()
    # O equipamento de um aluguel nunca muda (I2): pode ser lido antes do bloqueio.
    equipamento_id = (
        Aluguel.objects.filter(pk=aluguel_id)
        .values_list("equipamento_id", flat=True)
        .first()
    )
    if equipamento_id is None:
        raise Aluguel.DoesNotExist

    with transaction.atomic():
        Equipamento.objects.select_for_update().get(pk=equipamento_id)
        aluguel = Aluguel.objects.select_for_update().get(pk=aluguel_id)
        if not aluguel.aberto:
            raise ValidationError(mensagens.ALUGUEL_ENCERRADO)
        if data_devolucao_real < aluguel.data_retirada:
            raise ValidationError(
                {"data_devolucao_real": mensagens.DEVOLUCAO_ANTES_DA_RETIRADA}
            )
        if data_devolucao_real > hoje:
            raise ValidationError({"data_devolucao_real": mensagens.DEVOLUCAO_FUTURA})
        aluguel.data_devolucao_real = data_devolucao_real
        aluguel.full_clean()
        gravados = Aluguel.objects.filter(
            pk=aluguel_id, data_devolucao_real__isnull=True
        ).update(data_devolucao_real=data_devolucao_real)
        if gravados != 1:  # pragma: no cover - defesa além do bloqueio
            raise ValidationError(mensagens.ALUGUEL_ENCERRADO)
    return aluguel
