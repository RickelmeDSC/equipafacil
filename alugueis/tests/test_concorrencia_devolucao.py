"""Devolução sob concorrência (RF007, RN001, I2, D10).

A devolução bloqueia o equipamento e depois o aluguel, com o mesmo primeiro
bloqueio do registro e dos serviços de equipamento. Cada teste segura a primeira
operação aberta em uma thread e confirma que a segunda, em outra conexão, espera
e decide com o estado já gravado.

Só no PostgreSQL: o SQLite ignora select_for_update() e os testes usam um banco
em memória que não é compartilhado entre threads.
"""

from unittest import skipUnless

from django.test import TransactionTestCase

from alugueis import services
from alugueis.models import Aluguel
from config import mensagens
from config.tests.concorrencia import OK, POSTGRESQL, executar_corrida
from config.tests.fabricas import criar_cliente, criar_equipamento, dias, hoje
from equipamentos import services as servicos_de_equipamento
from equipamentos.models import Equipamento


@skipUnless(POSTGRESQL, "concorrência real exige PostgreSQL")
class DevolucaoConcorrenteTests(TransactionTestCase):
    def setUp(self):
        self.equipamento = criar_equipamento()
        self.aluguel = services.registrar_aluguel(
            cliente_id=criar_cliente().pk,
            equipamento_id=self.equipamento.pk,
            data_retirada=dias(-3),
            data_devolucao_prevista=dias(-1),
            hoje=dias(-3),
        )

    def _devolver(self, data):
        return lambda: services.registrar_devolucao(
            aluguel_id=self.aluguel.pk, data_devolucao_real=data
        )

    def _novo_aluguel(self) -> None:
        services.registrar_aluguel(
            cliente_id=criar_cliente().pk,
            equipamento_id=self.equipamento.pk,
            data_retirada=hoje(),
            data_devolucao_prevista=dias(1),
        )

    def _inativar(self) -> None:
        servicos_de_equipamento.inativar_equipamento(self.equipamento.pk)

    def test_duas_devolucoes_do_mesmo_aluguel(self):
        primeira, segunda = executar_corrida(
            self, self._devolver(dias(-1)), self._devolver(hoje())
        )
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.ALUGUEL_ENCERRADO])
        aluguel = Aluguel.objects.get(pk=self.aluguel.pk)
        self.assertEqual(aluguel.data_devolucao_real, dias(-1))  # a segunda não corrige

    def test_novo_aluguel_espera_a_devolucao_e_e_aceito(self):
        primeira, segunda = executar_corrida(
            self, self._devolver(hoje()), self._novo_aluguel
        )
        self.assertEqual((primeira, segunda), (OK, OK))
        self.assertEqual(Aluguel.objects.abertos().count(), 1)
        self.assertFalse(Aluguel.objects.get(pk=self.aluguel.pk).aberto)

    def test_inativacao_espera_a_devolucao_e_e_aceita(self):
        primeira, segunda = executar_corrida(
            self, self._devolver(hoje()), self._inativar
        )
        self.assertEqual((primeira, segunda), (OK, OK))
        equipamento = Equipamento.objects.get(pk=self.equipamento.pk)
        self.assertFalse(equipamento.ativo)
        self.assertFalse(equipamento.disponivel)
        self.assertFalse(equipamento.tem_aluguel_aberto)

    def test_devolucao_espera_a_edicao_do_equipamento(self):
        """Edição da diária (com histórico) segurando o bloqueio: a devolução espera
        e não altera o valor contratado."""
        valor_contratado = self.aluguel.valor_contratado
        dados = {
            "codigo": self.equipamento.codigo,
            "nome": self.equipamento.nome,
            "categoria": self.equipamento.categoria,
            "descricao": "",
            "valor_diaria": self.equipamento.valor_diaria * 3,
        }
        primeira, segunda = executar_corrida(
            self,
            lambda: servicos_de_equipamento.editar_equipamento(
                self.equipamento.pk, dados
            ),
            self._devolver(hoje()),
        )
        self.assertEqual((primeira, segunda), (OK, OK))
        aluguel = Aluguel.objects.get(pk=self.aluguel.pk)
        self.assertEqual(aluguel.valor_contratado, valor_contratado)
        self.assertEqual(aluguel.data_devolucao_real, hoje())
