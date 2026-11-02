"""Execução de duas operações concorrentes em conexões separadas (só PostgreSQL).

Usado pelos testes com ``TransactionTestCase``: a primeira operação roda em uma
thread e mantém a transação aberta; a segunda, em outra thread (outra conexão),
começa em seguida. O executor confirma que a segunda ficou esperando (bloqueio
de linha ou índice único) antes de liberar a primeira.
"""

import threading
from collections.abc import Callable

from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.test import TransactionTestCase

POSTGRESQL = connection.vendor == "postgresql"
ESPERA = 10  # segundos; só usado como limite de segurança
OK = "ok"


def executar_corrida(
    caso: TransactionTestCase,
    primeira: Callable[[], object],
    segunda: Callable[[], object],
) -> tuple[object, object]:
    """Devolve o resultado de cada operação: ``OK`` ou a lista de mensagens de erro."""
    primeira_terminou = threading.Event()
    liberar_primeira = threading.Event()
    resultado: dict[str, object] = {}

    def executar(nome: str, operacao: Callable[[], object]) -> None:
        try:
            operacao()
            resultado[nome] = OK
        except ValidationError as erro:
            resultado[nome] = erro.messages
        except Exception as erro:  # pragma: no cover - diagnóstico
            resultado[nome] = repr(erro)

    def thread_primeira() -> None:
        try:
            with transaction.atomic():
                executar("primeira", primeira)
                primeira_terminou.set()
                liberar_primeira.wait(ESPERA)
        finally:
            connection.close()

    def thread_segunda() -> None:
        try:
            primeira_terminou.wait(ESPERA)
            executar("segunda", segunda)
        finally:
            connection.close()

    threads = [
        threading.Thread(target=thread_primeira),
        threading.Thread(target=thread_segunda),
    ]
    for thread in threads:
        thread.start()
    caso.assertTrue(primeira_terminou.wait(ESPERA))
    threads[1].join(1.0)
    # A segunda fica parada até a primeira transação terminar; nada é decidido
    # com dados antigos.
    caso.assertTrue(threads[1].is_alive(), "a segunda operação não esperou")
    liberar_primeira.set()
    for thread in threads:
        thread.join(ESPERA)
    caso.assertFalse(any(thread.is_alive() for thread in threads))
    return resultado["primeira"], resultado["segunda"]
