"""Serviços transacionais de equipamentos (RF001–RF004, RN001–RN003, D10, D11, I3).

Toda operação que altera um equipamento existente bloqueia a linha dele
(``select_for_update``) antes de revalidar as regras. É o mesmo primeiro
bloqueio de ``alugueis.services.registrar_aluguel`` (equipamento, depois
cliente), então edição, exclusão, inativação e registro de aluguel do mesmo
equipamento são serializados no PostgreSQL. No SQLite o bloqueio não tem efeito.

Os indicadores de ``avaliar_acoes`` servem só para a interface: cada operação
revalida tudo dentro da transação.
"""

from copy import copy
from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from config import mensagens
from equipamentos.models import Equipamento

# Únicos campos aceitos do formulário; ``ativo`` só muda por inativação/reativação.
CAMPOS_EDITAVEIS = ("codigo", "nome", "categoria", "descricao", "valor_diaria")
_RESTRICAO_DO_CODIGO = "equipamento_codigo_unico_ci"


@dataclass(frozen=True)
class AcoesDoEquipamento:
    """Ações permitidas e motivos de bloqueio, para exibição (P04)."""

    tem_historico: bool
    tem_aluguel_ativo: bool
    pode_excluir: bool
    pode_inativar: bool
    pode_reativar: bool
    motivo_exclusao: str
    motivo_inativacao: str
    motivo_reativacao: str


def _dados_cadastrais_validos(equipamento: Equipamento) -> bool:
    """Revalida o cadastro com as regras atuais (RN002, D11), sem alterar o objeto."""
    candidato = copy(equipamento)
    candidato.ativo = True
    try:
        candidato.full_clean()
    except ValidationError:
        return False
    return True


def avaliar_acoes(
    equipamento: Equipamento, *, verificar_dados: bool = True
) -> AcoesDoEquipamento:
    """Calcula o que pode ser feito com o equipamento (D10, RN003, I3).

    Com ``verificar_dados=False`` (listagem), a reativação não revalida o
    cadastro; a página de ações e a própria operação revalidam.
    """
    historico = equipamento.tem_historico
    aberto = equipamento.tem_aluguel_aberto

    if aberto:
        motivo_exclusao = mensagens.ALUGUEL_ATIVO_IMPEDE
    elif historico:
        motivo_exclusao = mensagens.EXCLUSAO_COM_HISTORICO
    else:
        motivo_exclusao = ""

    pode_inativar = equipamento.ativo and not aberto
    motivo_inativacao = (
        mensagens.ALUGUEL_ATIVO_IMPEDE if equipamento.ativo and aberto else ""
    )

    pode_reativar = False
    motivo_reativacao = ""
    if not equipamento.ativo:
        dados_ok = not verificar_dados or _dados_cadastrais_validos(equipamento)
        pode_reativar = dados_ok and not aberto
        motivo_reativacao = "" if pode_reativar else mensagens.REATIVACAO_BLOQUEADA

    return AcoesDoEquipamento(
        tem_historico=historico,
        tem_aluguel_ativo=aberto,
        pode_excluir=not historico,
        pode_inativar=pode_inativar,
        pode_reativar=pode_reativar,
        motivo_exclusao=motivo_exclusao,
        motivo_inativacao=motivo_inativacao,
        motivo_reativacao=motivo_reativacao,
    )


def _bloquear(pk: int) -> Equipamento:
    return Equipamento.objects.select_for_update().get(pk=pk)


def _gravar(equipamento: Equipamento) -> Equipamento:
    """Grava com validação completa; corrida de código duplicado vira erro de campo."""
    try:
        with transaction.atomic():
            equipamento.save()
    except IntegrityError as erro:
        if _RESTRICAO_DO_CODIGO in str(erro):
            raise ValidationError({"codigo": mensagens.CODIGO_DUPLICADO}) from None
        raise
    return equipamento


def cadastrar_equipamento(dados: dict[str, Any]) -> Equipamento:
    """RF001: cria ativo, usando só os campos editáveis."""
    equipamento = Equipamento(
        **{campo: dados[campo] for campo in CAMPOS_EDITAVEIS if campo in dados}
    )
    with transaction.atomic():
        return _gravar(equipamento)


def editar_equipamento(pk: int, dados: dict[str, Any]) -> Equipamento:
    """RF003: altera os campos editáveis; o código só muda sem histórico (D11).

    O bloqueio da linha impede que a edição e o primeiro aluguel terminem juntos
    com uma troca de código proibida: quem bloqueia depois revalida o histórico.
    """
    with transaction.atomic():
        equipamento = _bloquear(pk)
        novo_codigo = dados.get("codigo", equipamento.codigo)
        if isinstance(novo_codigo, str):
            novo_codigo = novo_codigo.strip()
        if novo_codigo != equipamento.codigo and equipamento.tem_historico:
            raise ValidationError({"codigo": mensagens.CODIGO_BLOQUEADO})
        for campo in CAMPOS_EDITAVEIS:
            if campo in dados:
                setattr(equipamento, campo, dados[campo])
        return _gravar(equipamento)


def excluir_equipamento(pk: int) -> None:
    """RF004/RN003: exclusão física só sem histórico e sem aluguel aberto."""
    with transaction.atomic():
        equipamento = _bloquear(pk)
        acoes = avaliar_acoes(equipamento, verificar_dados=False)
        if not acoes.pode_excluir:
            raise ValidationError(acoes.motivo_exclusao)
        try:
            with transaction.atomic():
                equipamento.delete()
        except ProtectedError:
            raise ValidationError(mensagens.EXCLUSAO_COM_HISTORICO) from None


def inativar_equipamento(pk: int) -> Equipamento:
    """D10: todo equipamento ativo sem aluguel aberto pode ser inativado.

    Já inativo: nada muda (operação idempotente).
    """
    with transaction.atomic():
        equipamento = _bloquear(pk)
        if not equipamento.ativo:
            return equipamento
        if equipamento.tem_aluguel_aberto:
            raise ValidationError(mensagens.ALUGUEL_ATIVO_IMPEDE)
        Equipamento.objects.filter(pk=pk).update(ativo=False)
        equipamento.ativo = False
        return equipamento


def reativar_equipamento(pk: int) -> Equipamento:
    """RN003/I3: reativa se os dados forem válidos e não houver aluguel aberto.

    Já ativo: nada muda (operação idempotente). O histórico não é alterado.
    """
    with transaction.atomic():
        equipamento = _bloquear(pk)
        if equipamento.ativo:
            return equipamento
        if not avaliar_acoes(equipamento).pode_reativar:
            raise ValidationError(mensagens.REATIVACAO_BLOQUEADA)
        Equipamento.objects.filter(pk=pk).update(ativo=True)
        equipamento.ativo = True
        return equipamento
