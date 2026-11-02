"""Dados fictícios para os testes de domínio (nenhum dado real de cliente)."""

from datetime import date, timedelta
from decimal import Decimal
from itertools import count

from django.utils import timezone

from alugueis.models import Aluguel
from alugueis.services import registrar_aluguel
from clientes.models import Cliente
from equipamentos.models import Categoria, Equipamento

_sequencia = count(1)


def hoje() -> date:
    """Data atual em America/Recife, base de todas as datas relativas dos testes."""
    return timezone.localdate()


def dias(quantidade: int) -> date:
    return hoje() + timedelta(days=quantidade)


def cpf_valido(base: str) -> str:
    """Gera um CPF fictício com dígitos verificadores válidos a partir de 9 dígitos."""
    digitos = [int(d) for d in base]
    for tamanho in (9, 10):
        soma = sum(d * (tamanho + 1 - i) for i, d in enumerate(digitos[:tamanho]))
        digitos.append(soma * 10 % 11 % 10)
    return "".join(map(str, digitos))


def criar_equipamento(**campos) -> Equipamento:
    numero = next(_sequencia)
    dados = {
        "codigo": f"EQ-{numero:04d}",
        "nome": f"Equipamento de teste {numero}",
        "categoria": Categoria.FERRAMENTAS,
        "valor_diaria": Decimal("50.00"),
    }
    dados.update(campos)
    return Equipamento.objects.create(**dados)


def criar_cliente(**campos) -> Cliente:
    numero = next(_sequencia)
    dados = {
        "nome_completo": f"Cliente Fictício {numero}",
        "cpf": cpf_valido(f"{100000000 + numero:09d}"),
    }
    dados.update(campos)
    return Cliente.objects.create(**dados)


def registrar(
    equipamento: Equipamento | None = None,
    cliente: Cliente | None = None,
    retirada: date | None = None,
    prevista: date | None = None,
) -> Aluguel:
    equipamento = equipamento or criar_equipamento()
    cliente = cliente or criar_cliente()
    retirada = retirada or hoje()
    return registrar_aluguel(
        cliente_id=cliente.pk,
        equipamento_id=equipamento.pk,
        data_retirada=retirada,
        data_devolucao_prevista=prevista or retirada,
        hoje=hoje(),
    )


def encerrar(aluguel: Aluguel, data: date | None = None) -> Aluguel:
    aluguel.data_devolucao_real = data or aluguel.data_retirada
    aluguel.save()
    return aluguel
