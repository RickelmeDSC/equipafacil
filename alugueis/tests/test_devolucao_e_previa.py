"""Serviços de prévia (D13) e devolução (RF007, RN004, I1, I2)."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from alugueis import services
from alugueis.models import Aluguel, Situacao
from config import mensagens
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    dias,
    hoje,
    registrar,
)
from equipamentos.models import Equipamento


def registrar_no_passado(equipamento, retirada_ha: int, prevista_ha: int) -> Aluguel:
    """Aluguel registrado em data passada (o serviço aceita a data atual da época)."""
    return services.registrar_aluguel(
        cliente_id=criar_cliente().pk,
        equipamento_id=equipamento.pk,
        data_retirada=dias(-retirada_ha),
        data_devolucao_prevista=dias(-prevista_ha),
        hoje=dias(-retirada_ha),
    )


class ResumoTests(TestCase):
    def test_diarias_inclusivas_e_valor_decimal(self):
        casos = [(0, 1, "50.00"), (2, 3, "150.00"), (9, 10, "500.00")]
        for intervalo, diarias, total in casos:
            with self.subTest(intervalo=intervalo):
                resumo = services.calcular_resumo(
                    Decimal("50.00"), hoje(), dias(intervalo)
                )
                self.assertEqual(resumo.quantidade_diarias, diarias)
                self.assertEqual(resumo.valor_previsto, Decimal(total))

    def test_valor_exato_sem_float(self):
        resumo = services.calcular_resumo(Decimal("33.33"), hoje(), dias(2))
        self.assertEqual(resumo.valor_previsto, Decimal("99.99"))


class SimularAluguelTests(TestCase):
    def setUp(self):
        self.equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        self.cliente = criar_cliente()

    def _simular(self, **campos):
        dados = {
            "cliente_id": self.cliente.pk,
            "equipamento_id": self.equipamento.pk,
            "data_retirada": hoje(),
            "data_devolucao_prevista": dias(2),
        }
        dados.update(campos)
        return services.simular_aluguel(**dados)

    def test_calcula_sem_gravar(self):
        resumo = self._simular()
        self.assertEqual(
            (resumo.quantidade_diarias, resumo.valor_diaria, resumo.valor_previsto),
            (3, Decimal("50.00"), Decimal("150.00")),
        )
        self.assertFalse(Aluguel.objects.exists())

    def test_mesmas_recusas_do_registro(self):
        registrar(equipamento=criar_equipamento(codigo="ALU-01"))
        alugado = Equipamento.objects.get(codigo="ALU-01")
        inativo = criar_equipamento(ativo=False)
        casos = {
            "retirada no passado": ({"data_retirada": dias(-1)}, "data_retirada"),
            "prevista antes": (
                {"data_devolucao_prevista": dias(-1)},
                "data_devolucao_prevista",
            ),
            "equipamento alugado": ({"equipamento_id": alugado.pk}, "equipamento"),
            "equipamento inativo": ({"equipamento_id": inativo.pk}, "equipamento"),
            "equipamento inexistente": ({"equipamento_id": 999}, "equipamento"),
            "cliente inexistente": ({"cliente_id": 999}, "cliente"),
        }
        for descricao, (campos, campo) in casos.items():
            with self.subTest(caso=descricao):
                with self.assertRaises(ValidationError) as erro:
                    self._simular(**campos)
                self.assertIn(campo, erro.exception.message_dict)
        self.assertEqual(Aluguel.objects.count(), 1)


class RegistroTests(TestCase):
    def test_cliente_inexistente_vira_erro_de_campo(self):
        with self.assertRaises(ValidationError) as erro:
            services.registrar_aluguel(
                cliente_id=999,
                equipamento_id=criar_equipamento().pk,
                data_retirada=hoje(),
                data_devolucao_prevista=hoje(),
            )
        self.assertEqual(
            erro.exception.message_dict["cliente"], [mensagens.CLIENTE_INEXISTENTE]
        )
        self.assertFalse(Aluguel.objects.exists())

    def test_retirada_e_prevista_invalidas_juntas(self):
        with self.assertRaises(ValidationError) as erro:
            services.registrar_aluguel(
                cliente_id=criar_cliente().pk,
                equipamento_id=criar_equipamento().pk,
                data_retirada=dias(-1),
                data_devolucao_prevista=dias(-2),
            )
        self.assertEqual(
            set(erro.exception.message_dict),
            {"data_retirada", "data_devolucao_prevista"},
        )

    def test_nova_diaria_nao_altera_aluguel_registrado(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        aluguel = registrar(equipamento=equipamento, prevista=dias(2))
        equipamento.valor_diaria = Decimal("90.00")
        equipamento.save()
        aluguel.refresh_from_db()
        self.assertEqual(
            (aluguel.valor_diaria_contratada, aluguel.valor_contratado),
            (Decimal("50.00"), Decimal("150.00")),
        )


class DevolucaoTests(TestCase):
    def setUp(self):
        self.equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))

    def _devolver(self, aluguel, data):
        return services.registrar_devolucao(
            aluguel_id=aluguel.pk, data_devolucao_real=data
        )

    def test_devolucao_hoje_encerra_e_libera_o_equipamento(self):
        aluguel = registrar(equipamento=self.equipamento, prevista=dias(2))
        self._devolver(aluguel, hoje())
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, hoje())
        self.assertEqual(aluguel.situacao_codigo(), Situacao.ENCERRADO)
        self.assertEqual(aluguel.valor_contratado, Decimal("150.00"))
        self.assertTrue(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)

    def test_devolucao_em_atraso_sem_multa_nem_recalculo(self):
        aluguel = registrar_no_passado(self.equipamento, retirada_ha=5, prevista_ha=3)
        self.assertEqual(aluguel.situacao_codigo(), Situacao.ATRASADO)
        self._devolver(aluguel, hoje())
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.situacao_codigo(), Situacao.ENCERRADO_COM_ATRASO)
        self.assertEqual(
            (aluguel.quantidade_diarias, aluguel.valor_contratado),
            (3, Decimal("150.00")),
        )

    def test_data_real_fora_do_intervalo(self):
        aluguel = registrar_no_passado(self.equipamento, retirada_ha=2, prevista_ha=1)
        casos = {
            dias(-3): mensagens.DEVOLUCAO_ANTES_DA_RETIRADA,
            dias(1): mensagens.DEVOLUCAO_FUTURA,
        }
        for data, mensagem in casos.items():
            with self.subTest(data=data):
                with self.assertRaises(ValidationError) as erro:
                    self._devolver(aluguel, data)
                self.assertEqual(
                    erro.exception.message_dict["data_devolucao_real"], [mensagem]
                )
        aluguel.refresh_from_db()
        self.assertTrue(aluguel.aberto)

    def test_retirada_futura_ainda_nao_pode_ser_devolvida(self):
        aluguel = registrar(
            equipamento=self.equipamento, retirada=dias(3), prevista=dias(4)
        )
        self.assertFalse(aluguel.pode_devolver())
        with self.assertRaises(ValidationError):
            self._devolver(aluguel, hoje())
        aluguel.refresh_from_db()
        self.assertTrue(aluguel.aberto)
        self.assertFalse(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)

    def test_segunda_devolucao_e_correcao_sao_recusadas(self):
        aluguel = registrar_no_passado(self.equipamento, retirada_ha=3, prevista_ha=1)
        self._devolver(aluguel, dias(-1))
        for data in (dias(-1), hoje(), dias(-2)):
            with self.subTest(data=data):
                with self.assertRaisesMessage(
                    ValidationError, mensagens.ALUGUEL_ENCERRADO
                ):
                    self._devolver(aluguel, data)
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, dias(-1))

    def test_equipamento_inativo_continua_indisponivel_apos_devolucao(self):
        """Massa preparada fora da interface: inativo com aluguel aberto."""
        aluguel = registrar(equipamento=self.equipamento)
        Equipamento.objects.filter(pk=self.equipamento.pk).update(ativo=False)
        self._devolver(aluguel, hoje())
        equipamento = Equipamento.objects.get(pk=self.equipamento.pk)
        self.assertFalse(equipamento.tem_aluguel_aberto)
        self.assertFalse(equipamento.disponivel)

    def test_aluguel_inexistente(self):
        with self.assertRaises(Aluguel.DoesNotExist):
            services.registrar_devolucao(aluguel_id=999, data_devolucao_real=hoje())

    def test_devolucao_nao_altera_outros_campos(self):
        aluguel = registrar(equipamento=self.equipamento, prevista=dias(1))
        antes = Aluguel.objects.filter(pk=aluguel.pk).values().get()
        self._devolver(aluguel, hoje())
        depois = Aluguel.objects.filter(pk=aluguel.pk).values().get()
        depois.pop("data_devolucao_real")
        antes.pop("data_devolucao_real")
        self.assertEqual(antes, depois)
