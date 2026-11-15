"""Massa do CT16 — Consultar histórico sem registros.

Pré-condição do cenário: o sistema não possui nenhum aluguel registrado. O
banco já chega zerado (só com o usuário de teste), então nada é criado aqui.

Para cenários que precisam de dados, use as fábricas de
``config/tests/fabricas.py`` (``criar_equipamento``, ``criar_cliente``,
``registrar``, ``encerrar``), sempre com dados fictícios.
"""


def preparar() -> None:
    """Não cria nada: o CT16 exige o histórico vazio."""
