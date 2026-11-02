"""Serviço registrar_aluguel: datas, disponibilidade e valores recalculados (RF006, I1, D13)."""

import inspect
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from alugueis.models import Aluguel
from alugueis.services import registrar_aluguel
from config import mensagens
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    dias,
    hoje,
    registrar,
)


class RegistrarAluguelTests(TestCase):
    def test_registra_aluguel_aberto_com_valores_do_banco(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("12.34"))
        aluguel = registrar(equipamento=equipamento, retirada=dias(0), prevista=dias(4))
        self.assertTrue(aluguel.aberto)
        self.assertEqual(aluguel.quantidade_diarias, 5)
        self.assertEqual(aluguel.valor_diaria_contratada, Decimal("12.34"))
        self.assertEqual(aluguel.valor_contratado, Decimal("61.70"))

    def test_valores_nunca_vem_de_fora(self):
        parametros = set(inspect.signature(registrar_aluguel).parameters)
        self.assertEqual(
            parametros,
            {
                "cliente_id",
                "equipamento_id",
                "data_retirada",
                "data_devolucao_prevista",
                "hoje",
            },
        )

    def test_retirada_anterior_a_data_atual(self):
        with self.assertRaises(ValidationError) as erro:
            registrar(retirada=dias(-1), prevista=dias(1))
        self.assertEqual(
            erro.exception.message_dict["data_retirada"],
            [mensagens.RETIRADA_NO_PASSADO],
        )

    def test_prevista_anterior_a_retirada(self):
        with self.assertRaises(ValidationError) as erro:
            registrar(retirada=dias(2), prevista=dias(1))
        self.assertEqual(
            erro.exception.message_dict["data_devolucao_prevista"],
            [mensagens.PREVISTA_ANTES_DA_RETIRADA],
        )

    def test_ct12_equipamento_com_aluguel_aberto(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento, prevista=dias(3))
        with self.assertRaises(ValidationError) as erro:
            registrar(equipamento=equipamento)
        self.assertEqual(
            erro.exception.message_dict["equipamento"],
            [mensagens.EQUIPAMENTO_INDISPONIVEL],
        )
        self.assertEqual(Aluguel.objects.count(), 1)

    def test_retirada_futura_reserva_o_equipamento(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento, retirada=dias(10), prevista=dias(12))
        with self.assertRaises(ValidationError):
            registrar(equipamento=equipamento, retirada=dias(0), prevista=dias(1))

    def test_data_atual_padrao_em_america_recife(self):
        aluguel = registrar_aluguel(
            cliente_id=criar_cliente().pk,
            equipamento_id=criar_equipamento().pk,
            data_retirada=hoje(),
            data_devolucao_prevista=hoje(),
        )
        self.assertEqual(aluguel.data_retirada, hoje())
