"""Serviços transacionais de clientes (RF005, RN002, RN003, I5, D12, D14).

Protocolo de bloqueios: ``registrar_aluguel`` bloqueia o equipamento e depois o
cliente. A edição de cliente bloqueia só a linha do cliente e nenhuma linha de
equipamento, então não forma ciclo de espera com o registro de aluguel. Quem
bloqueia o cliente por último decide com o estado já gravado: a edição que
chega depois do primeiro aluguel encontra o histórico e recusa a troca do CPF.
No SQLite o bloqueio não tem efeito.

O cadastro não tem linha a bloquear: dois cadastros simultâneos com o mesmo CPF
são decididos pelo índice único ``cliente_cpf_unico``, e o conflito vira erro de
campo, nunca erro 500.

Não há exclusão, inativação nem página de detalhe de cliente (RN003, D14). A
pesquisa do RF009 (D16) é só leitura e fica em ``ClienteQuerySet.pesquisar``.
"""

from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from clientes.models import Cliente
from clientes.validadores import normalizar_cpf
from config import mensagens

# Únicos campos aceitos do formulário; id e qualquer outro campo são ignorados.
CAMPOS_EDITAVEIS = ("nome_completo", "cpf", "telefone", "email")


def _cpf_de_outro_cliente(cliente: Cliente) -> bool:
    return Cliente.objects.filter(cpf=cliente.cpf).exclude(pk=cliente.pk).exists()


def _gravar(cliente: Cliente) -> Cliente:
    """Grava com validação completa; corrida de CPF duplicado vira erro de campo.

    A conferência é feita de novo depois do ``IntegrityError`` (dentro de um
    savepoint), em vez de interpretar o texto do erro, que muda entre bancos.
    """
    try:
        with transaction.atomic():
            cliente.save()
    except IntegrityError:
        if _cpf_de_outro_cliente(cliente):
            raise ValidationError({"cpf": mensagens.CPF_DUPLICADO}) from None
        raise
    return cliente


def cadastrar_cliente(dados: dict[str, Any]) -> Cliente:
    """RF005: cria o cliente usando só os campos editáveis."""
    cliente = Cliente(
        **{campo: dados[campo] for campo in CAMPOS_EDITAVEIS if campo in dados}
    )
    with transaction.atomic():
        return _gravar(cliente)


def editar_cliente(pk: int, dados: dict[str, Any]) -> Cliente:
    """RF005/D12: altera nome e contatos; o CPF só muda sem nenhum aluguel.

    Aluguel encerrado também bloqueia a troca. O mesmo CPF com outra pontuação
    não é alteração. Nome, telefone e e-mail seguem editáveis com histórico.
    """
    with transaction.atomic():
        cliente = Cliente.objects.select_for_update().get(pk=pk)
        if "cpf" in dados:
            novo_cpf = normalizar_cpf(dados["cpf"])
            if novo_cpf != cliente.cpf and cliente.tem_aluguel:
                raise ValidationError({"cpf": mensagens.CPF_BLOQUEADO})
        for campo in CAMPOS_EDITAVEIS:
            if campo in dados:
                setattr(cliente, campo, dados[campo])
        return _gravar(cliente)
