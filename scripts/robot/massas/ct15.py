"""Massa do CT15 — Consultar histórico de aluguéis.

Um aluguel em cada situação, cada um com o próprio equipamento. Todos são
gravados pelos serviços reais; o parâmetro ``hoje`` simula registros e
devoluções feitos em dias anteriores, já que o sistema recusa retirada no
passado e devolução no futuro.

Na ordem em que o histórico exibe (retirada mais recente primeiro):

- FUR-001, R$ 50,00: retirada hoje, prevista hoje+2, sem devolução;
  3 diárias, R$ 150,00 — Ativo.
- AND-001, R$ 30,00: retirada hoje-1, prevista hoje, devolvido hoje-1;
  2 diárias, R$ 60,00 — Encerrado.
- BET-001, R$ 80,00: retirada hoje-3, prevista hoje-1, sem devolução;
  3 diárias, R$ 240,00 — Atrasado.
- PRJ-001, R$ 100,00: retirada hoje-5, prevista hoje-3, devolvido hoje-1;
  3 diárias, R$ 300,00 — Encerrado com atraso.
"""

from datetime import date
from decimal import Decimal

from alugueis.models import Aluguel
from alugueis.services import registrar_aluguel, registrar_devolucao
from clientes.models import Cliente
from config.tests.fabricas import criar_cliente, criar_equipamento, dias


def _alugar(
    cliente: Cliente,
    codigo: str,
    nome: str,
    diaria: str,
    retirada: date,
    prevista: date,
) -> Aluguel:
    """Registra o aluguel como se o registro tivesse sido feito no dia da retirada."""
    equipamento = criar_equipamento(
        codigo=codigo, nome=nome, valor_diaria=Decimal(diaria)
    )
    return registrar_aluguel(
        cliente_id=cliente.pk,
        equipamento_id=equipamento.pk,
        data_retirada=retirada,
        data_devolucao_prevista=prevista,
        hoje=retirada,
    )


def _devolver(aluguel: Aluguel, devolucao: date) -> None:
    """Registra a devolução como se tivesse sido feita no próprio dia da devolução."""
    registrar_devolucao(
        aluguel_id=aluguel.pk, data_devolucao_real=devolucao, hoje=devolucao
    )


def preparar() -> None:
    joao = criar_cliente(nome_completo="João Silva", cpf="52998224725")
    maria = criar_cliente(nome_completo="Maria Souza")

    _alugar(joao, "FUR-001", "Furadeira Impacto", "50.00", dias(0), dias(2))

    encerrado = _alugar(maria, "AND-001", "Andaime Tubular", "30.00", dias(-1), dias(0))
    _devolver(encerrado, dias(-1))

    _alugar(joao, "BET-001", "Betoneira 150 L", "80.00", dias(-3), dias(-1))

    com_atraso = _alugar(
        maria, "PRJ-001", "Projetor Multimídia", "100.00", dias(-5), dias(-3)
    )
    _devolver(com_atraso, dias(-1))
