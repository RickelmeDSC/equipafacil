"""Duas tentativas simultâneas de alugar o mesmo equipamento (RN001, CT12).

Só no PostgreSQL: o SQLite ignora select_for_update() e os testes usam um banco
em memória que não é compartilhado entre threads.
"""

import threading
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TransactionTestCase

from alugueis.models import Aluguel
from alugueis.services import registrar_aluguel
from config import mensagens
from config.tests.fabricas import criar_cliente, criar_equipamento, dias, hoje

POSTGRESQL = connection.vendor == "postgresql"
ESPERA = 10  # segundos; só usado como limite de segurança


@skipUnless(POSTGRESQL, "concorrência real exige PostgreSQL")
class AlugueisSimultaneosTests(TransactionTestCase):
    def setUp(self):
        self.equipamento = criar_equipamento()
        self.clientes = [criar_cliente(), criar_cliente()]

    def _registrar(self, cliente) -> Aluguel:
        return registrar_aluguel(
            cliente_id=cliente.pk,
            equipamento_id=self.equipamento.pk,
            data_retirada=hoje(),
            data_devolucao_prevista=dias(1),
            hoje=hoje(),
        )

    def test_segunda_tentativa_espera_o_bloqueio_e_e_recusada(self):
        primeira_bloqueou = threading.Event()
        liberar_primeira = threading.Event()
        resultado: dict[str, object] = {}

        def primeira():
            try:
                with transaction.atomic():
                    self._registrar(self.clientes[0])
                    primeira_bloqueou.set()
                    liberar_primeira.wait(ESPERA)
                resultado["primeira"] = "registrado"
            except Exception as erro:  # pragma: no cover - diagnóstico
                resultado["primeira"] = repr(erro)
            finally:
                connection.close()

        def segunda():
            try:
                primeira_bloqueou.wait(ESPERA)
                self._registrar(self.clientes[1])
                resultado["segunda"] = "registrado"
            except ValidationError as erro:
                resultado["segunda"] = erro.messages
            finally:
                connection.close()

        threads = [threading.Thread(target=primeira), threading.Thread(target=segunda)]
        for thread in threads:
            thread.start()
        self.assertTrue(primeira_bloqueou.wait(ESPERA))
        threads[1].join(1.0)
        # Enquanto a primeira transação não termina, a segunda fica bloqueada na linha
        # do equipamento (select_for_update), sem registrar nada.
        self.assertTrue(threads[1].is_alive())
        liberar_primeira.set()
        for thread in threads:
            thread.join(ESPERA)

        self.assertEqual(resultado["primeira"], "registrado")
        self.assertEqual(resultado["segunda"], [mensagens.EQUIPAMENTO_INDISPONIVEL])
        self.assertEqual(
            Aluguel.objects.abertos().filter(equipamento=self.equipamento).count(), 1
        )

    def test_indice_parcial_barra_gravacoes_simultaneas_sem_bloqueio(self):
        """Mesmo ignorando o serviço, o PostgreSQL aceita só um aluguel aberto."""
        pronto = threading.Barrier(2)
        erros: list[str] = []

        def gravar(cliente):
            try:
                pronto.wait(ESPERA)
                with transaction.atomic():
                    Aluguel.objects.bulk_create(
                        [
                            Aluguel(
                                equipamento=self.equipamento,
                                cliente=cliente,
                                data_retirada=hoje(),
                                data_devolucao_prevista=hoje(),
                                valor_diaria_contratada=self.equipamento.valor_diaria,
                                quantidade_diarias=1,
                                valor_contratado=self.equipamento.valor_diaria,
                            )
                        ]
                    )
            except IntegrityError:
                erros.append("integridade")
            finally:
                connection.close()

        threads = [threading.Thread(target=gravar, args=(c,)) for c in self.clientes]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(ESPERA)
        self.assertEqual(erros, ["integridade"])
        self.assertEqual(Aluguel.objects.abertos().count(), 1)
