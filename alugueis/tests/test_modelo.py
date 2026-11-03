"""Aluguel: cálculos, valores congelados, situação, histórico e edição indevida."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase

from alugueis.models import (
    Aluguel,
    Situacao,
    calcular_diarias,
    calcular_valor_contratado,
)
from config import mensagens
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    dias,
    encerrar,
    hoje,
    registrar,
)


def _mensagens(erro: ValidationError) -> list[str]:
    return erro.exception.messages if hasattr(erro, "exception") else erro.messages


class CalculosTests(SimpleTestCase):
    def test_diarias_inclusivas(self):
        self.assertEqual(calcular_diarias(dias(0), dias(0)), 1)
        self.assertEqual(calcular_diarias(dias(0), dias(2)), 3)
        self.assertEqual(calcular_diarias(dias(10), dias(39)), 30)

    def test_valor_em_decimal_exato(self):
        valor = calcular_valor_contratado(3, Decimal("50.00"))
        self.assertEqual(valor, Decimal("150.00"))
        self.assertIsInstance(valor, Decimal)
        self.assertEqual(
            calcular_valor_contratado(3, Decimal("33.33")), Decimal("99.99")
        )


class ValoresCongeladosTests(TestCase):
    def test_ct11_tres_diarias_de_cinquenta_reais(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        aluguel = registrar(equipamento=equipamento, retirada=dias(0), prevista=dias(2))
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.quantidade_diarias, 3)
        self.assertEqual(aluguel.valor_diaria_contratada, Decimal("50.00"))
        self.assertEqual(aluguel.valor_contratado, Decimal("150.00"))

    def test_ct05_nova_diaria_nao_altera_aluguel_registrado(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        aluguel = registrar(equipamento=equipamento, prevista=dias(1))
        encerrar(aluguel)
        equipamento.valor_diaria = Decimal("80.00")
        equipamento.save()
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.valor_diaria_contratada, Decimal("50.00"))
        self.assertEqual(aluguel.valor_contratado, Decimal("100.00"))

    def test_registro_direto_com_valores_inconsistentes_e_recusado(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        cliente = criar_cliente()
        base = {
            "equipamento": equipamento,
            "cliente": cliente,
            "data_retirada": dias(0),
            "data_devolucao_prevista": dias(2),
            "valor_diaria_contratada": Decimal("50.00"),
            "quantidade_diarias": 3,
            "valor_contratado": Decimal("150.00"),
        }
        casos = {
            "diárias erradas": {"quantidade_diarias": 2},
            "valor errado": {"valor_contratado": Decimal("149.99")},
            "diária diferente da do equipamento": {
                "valor_diaria_contratada": Decimal("40.00"),
                "valor_contratado": Decimal("120.00"),
            },
        }
        for descricao, campos in casos.items():
            with self.subTest(caso=descricao):
                with self.assertRaises(ValidationError) as erro:
                    Aluguel(**{**base, **campos}).save()
                self.assertIn(
                    mensagens.VALORES_DO_ALUGUEL_INCONSISTENTES, _mensagens(erro)
                )
        Aluguel(**base).save()  # valores coerentes são aceitos


class RelacionamentosEHistoricoTests(TestCase):
    def test_relacionamentos(self):
        equipamento, cliente = criar_equipamento(), criar_cliente()
        aluguel = registrar(equipamento=equipamento, cliente=cliente)
        self.assertEqual(aluguel.equipamento, equipamento)
        self.assertEqual(aluguel.cliente, cliente)
        self.assertEqual(list(equipamento.alugueis.all()), [aluguel])
        self.assertEqual(list(cliente.alugueis.all()), [aluguel])

    def test_historico_impede_exclusao_de_equipamento_e_cliente(self):
        equipamento, cliente = criar_equipamento(), criar_cliente()
        encerrar(registrar(equipamento=equipamento, cliente=cliente))
        with self.assertRaises(ProtectedError):
            equipamento.delete()
        with self.assertRaises(ProtectedError):
            cliente.delete()
        self.assertEqual(Aluguel.objects.count(), 1)

    def test_historico_preservado_entre_alugueis(self):
        equipamento = criar_equipamento()
        primeiro = encerrar(registrar(equipamento=equipamento))
        segundo = registrar(equipamento=equipamento, prevista=dias(3))
        self.assertEqual(Aluguel.objects.filter(equipamento=equipamento).count(), 2)
        self.assertEqual(list(Aluguel.objects.encerrados()), [primeiro])
        self.assertEqual(list(Aluguel.objects.abertos()), [segundo])


class UmAluguelAbertoTests(TestCase):
    def test_segundo_aluguel_aberto_e_recusado_pelo_modelo(self):
        aluguel = registrar(prevista=dias(2))
        outro = Aluguel(
            equipamento=aluguel.equipamento,
            cliente=criar_cliente(),
            data_retirada=dias(0),
            data_devolucao_prevista=dias(0),
            valor_diaria_contratada=aluguel.valor_diaria_contratada,
            quantidade_diarias=1,
            valor_contratado=aluguel.valor_diaria_contratada,
        )
        with self.assertRaises(ValidationError) as erro:
            outro.save()
        self.assertEqual(
            erro.exception.message_dict["equipamento"],
            [mensagens.EQUIPAMENTO_INDISPONIVEL],
        )

    def test_equipamento_inativo_nao_pode_ser_alugado(self):
        equipamento = criar_equipamento()
        equipamento.ativo = False
        equipamento.save()
        with self.assertRaises(ValidationError) as erro:
            registrar(equipamento=equipamento)
        self.assertEqual(
            erro.exception.message_dict["equipamento"],
            [mensagens.EQUIPAMENTO_INDISPONIVEL],
        )


class DatasTests(TestCase):
    def test_prevista_anterior_a_retirada_e_recusada_pelo_modelo(self):
        equipamento = criar_equipamento()
        aluguel = Aluguel(
            equipamento=equipamento,
            cliente=criar_cliente(),
            data_retirada=dias(2),
            data_devolucao_prevista=dias(1),
            valor_diaria_contratada=equipamento.valor_diaria,
            quantidade_diarias=1,
            valor_contratado=equipamento.valor_diaria,
        )
        with self.assertRaises(ValidationError) as erro:
            aluguel.save()
        self.assertEqual(
            erro.exception.message_dict["data_devolucao_prevista"],
            [mensagens.PREVISTA_ANTES_DA_RETIRADA],
        )

    def test_devolucao_anterior_a_retirada_e_recusada(self):
        aluguel = registrar(retirada=dias(3), prevista=dias(4))
        aluguel.data_devolucao_real = dias(2)
        with self.assertRaises(ValidationError) as erro:
            aluguel.save()
        self.assertEqual(
            erro.exception.message_dict["data_devolucao_real"],
            [mensagens.DEVOLUCAO_ANTES_DA_RETIRADA],
        )


class EdicaoIndevidaTests(TestCase):
    def test_aluguel_aberto_so_aceita_a_devolucao(self):
        aluguel = registrar(prevista=dias(2))
        alteracoes = {
            "valor_contratado": Decimal("1.00"),
            "valor_diaria_contratada": Decimal("1.00"),
            "quantidade_diarias": 9,
            "data_devolucao_prevista": dias(5),
            "data_retirada": dias(1),
            "equipamento": criar_equipamento(),
            "cliente": criar_cliente(),
        }
        for campo, valor in alteracoes.items():
            with self.subTest(campo=campo):
                aluguel.refresh_from_db()
                setattr(aluguel, campo, valor)
                with self.assertRaises(ValidationError) as erro:
                    aluguel.save()
                self.assertIn(mensagens.ALUGUEL_INALTERAVEL, erro.exception.messages)

        aluguel.refresh_from_db()
        encerrar(aluguel, dias(0))
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, dias(0))

    def test_aluguel_encerrado_nao_muda_mais(self):
        aluguel = encerrar(registrar(prevista=dias(2)), dias(0))
        for campo, valor in {
            "data_devolucao_real": dias(1),
            "valor_contratado": Decimal("1.00"),
        }.items():
            with self.subTest(campo=campo):
                aluguel.refresh_from_db()
                setattr(aluguel, campo, valor)
                with self.assertRaises(ValidationError) as erro:
                    aluguel.save()
                self.assertIn(mensagens.ALUGUEL_ENCERRADO, erro.exception.messages)
        aluguel.refresh_from_db()
        aluguel.data_devolucao_real = None
        with self.assertRaises(ValidationError):
            aluguel.save()


class SituacaoTests(TestCase):
    def test_situacao_calculada_e_nao_persistida(self):
        campos = {campo.name for campo in Aluguel._meta.get_fields()}
        self.assertFalse({"situacao", "status"} & campos)

    def test_situacoes(self):
        aluguel = registrar(prevista=dias(2))
        self.assertEqual(aluguel.situacao(hoje()), "Ativo")
        self.assertEqual(aluguel.situacao_codigo(dias(2)), Situacao.ATIVO)
        self.assertEqual(aluguel.situacao(dias(3)), "Atrasado")

        aluguel.data_devolucao_real = dias(2)
        self.assertEqual(aluguel.situacao(dias(10)), "Encerrado")
        aluguel.data_devolucao_real = dias(3)
        self.assertEqual(aluguel.situacao(dias(10)), "Encerrado com atraso")

    def test_retirada_futura_aparece_como_ativo_e_ainda_nao_pode_ser_devolvida(self):
        aluguel = registrar(retirada=dias(5), prevista=dias(7))
        self.assertEqual(aluguel.situacao(hoje()), "Ativo")
        self.assertFalse(aluguel.pode_devolver(hoje()))
        self.assertTrue(aluguel.pode_devolver(dias(5)))
