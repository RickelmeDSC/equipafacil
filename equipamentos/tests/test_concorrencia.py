"""Operações de equipamento simultâneas ao primeiro aluguel (RF003, RF004, D10, D11).

Os serviços de equipamento e ``registrar_aluguel`` bloqueiam primeiro a linha do
equipamento. Cada teste segura o bloqueio em uma thread, confirma que a outra
fica esperando e, ao liberar, verifica que a segunda revalidou as regras com o
estado já gravado pela primeira.

Só no PostgreSQL: o SQLite ignora select_for_update() e os testes usam um banco
em memória que não é compartilhado entre threads.
"""

from decimal import Decimal
from unittest import skipUnless

from django.test import TransactionTestCase

from alugueis.models import Aluguel
from alugueis.services import registrar_aluguel
from config import mensagens
from config.tests.concorrencia import OK, POSTGRESQL, executar_corrida
from config.tests.fabricas import criar_cliente, criar_equipamento, dias, hoje
from equipamentos import services
from equipamentos.models import Categoria, Equipamento


@skipUnless(POSTGRESQL, "concorrência real exige PostgreSQL")
class CorridasComPrimeiroAluguelTests(TransactionTestCase):
    def setUp(self):
        self.equipamento = criar_equipamento(codigo="FUR-01")
        self.cliente = criar_cliente()

    # Operações -----------------------------------------------------------------

    def _alugar(self) -> None:
        registrar_aluguel(
            cliente_id=self.cliente.pk,
            equipamento_id=self.equipamento.pk,
            data_retirada=hoje(),
            data_devolucao_prevista=dias(1),
            hoje=hoje(),
        )

    def _trocar_codigo(self) -> None:
        services.editar_equipamento(
            self.equipamento.pk,
            {
                "codigo": "FUR-99",
                "nome": "Furadeira",
                "categoria": Categoria.FERRAMENTAS,
                "descricao": "",
                "valor_diaria": Decimal("50.00"),
            },
        )

    def _excluir(self) -> None:
        services.excluir_equipamento(self.equipamento.pk)

    def _inativar(self) -> None:
        services.inativar_equipamento(self.equipamento.pk)

    def _corrida(self, primeira, segunda) -> tuple[object, object]:
        return executar_corrida(self, primeira, segunda)

    def _equipamento(self) -> Equipamento:
        return Equipamento.objects.get(pk=self.equipamento.pk)

    # Edição do código × primeiro aluguel (D11) ----------------------------------

    def test_codigo_trocado_antes_do_primeiro_aluguel(self):
        primeira, segunda = self._corrida(self._trocar_codigo, self._alugar)
        self.assertEqual((primeira, segunda), (OK, OK))
        aluguel = Aluguel.objects.get()
        self.assertEqual(aluguel.equipamento.codigo, "FUR-99")

    def test_troca_de_codigo_depois_do_primeiro_aluguel_e_recusada(self):
        primeira, segunda = self._corrida(self._alugar, self._trocar_codigo)
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.CODIGO_BLOQUEADO])
        self.assertEqual(self._equipamento().codigo, "FUR-01")
        self.assertEqual(Aluguel.objects.count(), 1)

    # Exclusão × primeiro aluguel (RF004, RN003) ---------------------------------

    def test_aluguel_depois_da_exclusao_e_recusado(self):
        primeira, segunda = self._corrida(self._excluir, self._alugar)
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.EQUIPAMENTO_INDISPONIVEL])
        self.assertFalse(Equipamento.objects.exists())
        self.assertFalse(Aluguel.objects.exists())

    def test_exclusao_depois_do_primeiro_aluguel_e_recusada(self):
        primeira, segunda = self._corrida(self._alugar, self._excluir)
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.ALUGUEL_ATIVO_IMPEDE])
        self.assertTrue(Equipamento.objects.filter(pk=self.equipamento.pk).exists())
        self.assertEqual(Aluguel.objects.count(), 1)

    # Inativação × primeiro aluguel (D10) ----------------------------------------

    def test_aluguel_depois_da_inativacao_e_recusado(self):
        primeira, segunda = self._corrida(self._inativar, self._alugar)
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.EQUIPAMENTO_INDISPONIVEL])
        self.assertFalse(self._equipamento().ativo)
        self.assertFalse(Aluguel.objects.exists())

    def test_inativacao_depois_do_primeiro_aluguel_e_recusada(self):
        primeira, segunda = self._corrida(self._alugar, self._inativar)
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.ALUGUEL_ATIVO_IMPEDE])
        self.assertTrue(self._equipamento().ativo)
        self.assertEqual(Aluguel.objects.count(), 1)
