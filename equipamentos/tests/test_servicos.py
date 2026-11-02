"""Serviços de equipamentos: cadastro, edição, exclusão, inativação (D10) e reativação (I3)."""

from decimal import Decimal
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from alugueis.models import Aluguel
from config import mensagens
from config.tests.fabricas import criar_equipamento, dias, encerrar, registrar
from equipamentos import services
from equipamentos.models import Categoria, Equipamento

DADOS = {
    "codigo": "FUR-01",
    "nome": "Furadeira",
    "categoria": Categoria.FERRAMENTAS,
    "descricao": "",
    "valor_diaria": Decimal("35.50"),
}


class CadastroTests(TestCase):
    def test_cadastra_ativo_e_ignora_campos_fora_da_lista(self):
        equipamento = services.cadastrar_equipamento(
            {**DADOS, "codigo": "  FUR-01 ", "ativo": False, "id": 999}
        )
        equipamento.refresh_from_db()
        self.assertTrue(equipamento.ativo)
        self.assertNotEqual(equipamento.pk, 999)
        self.assertEqual(equipamento.codigo, "FUR-01")

    def test_corrida_de_codigo_duplicado_vira_erro_de_campo(self):
        """Se dois cadastros passam pela validação juntos, o índice do banco decide."""
        criar_equipamento(codigo="FUR-01")
        with mock.patch.object(Equipamento, "full_clean"):
            with self.assertRaises(ValidationError) as erro:
                services.cadastrar_equipamento({**DADOS, "codigo": "fur-01"})
        self.assertEqual(
            erro.exception.message_dict["codigo"], [mensagens.CODIGO_DUPLICADO]
        )
        self.assertEqual(Equipamento.objects.count(), 1)


class EdicaoTests(TestCase):
    def test_edita_campos_e_codigo_sem_historico(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        services.editar_equipamento(
            equipamento.pk,
            {**DADOS, "codigo": "FUR-02", "nome": "Furadeira de impacto"},
        )
        equipamento.refresh_from_db()
        self.assertEqual(equipamento.codigo, "FUR-02")
        self.assertEqual(equipamento.nome, "Furadeira de impacto")

    def test_codigo_bloqueado_com_historico_inclusive_maiusculas(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        encerrar(registrar(equipamento=equipamento))
        for codigo in ("FUR-09", "fur-01"):
            with self.subTest(codigo=codigo):
                with self.assertRaises(ValidationError) as erro:
                    services.editar_equipamento(
                        equipamento.pk, {**DADOS, "codigo": codigo}
                    )
                self.assertEqual(
                    erro.exception.message_dict["codigo"], [mensagens.CODIGO_BLOQUEADO]
                )
        equipamento.refresh_from_db()
        self.assertEqual(equipamento.codigo, "FUR-01")

    def test_com_historico_os_demais_campos_continuam_editaveis(self):
        equipamento = criar_equipamento(codigo="FUR-01", valor_diaria=Decimal("50.00"))
        aluguel = encerrar(registrar(equipamento=equipamento, prevista=dias(1)))
        services.editar_equipamento(
            equipamento.pk,
            {**DADOS, "codigo": "FUR-01", "valor_diaria": Decimal("80.00")},
        )
        equipamento.refresh_from_db()
        aluguel.refresh_from_db()
        self.assertEqual(equipamento.valor_diaria, Decimal("80.00"))
        self.assertEqual(aluguel.valor_diaria_contratada, Decimal("50.00"))
        self.assertEqual(aluguel.valor_contratado, Decimal("100.00"))


class ExclusaoTests(TestCase):
    def test_exclui_sem_historico(self):
        equipamento = criar_equipamento()
        services.excluir_equipamento(equipamento.pk)
        self.assertFalse(Equipamento.objects.filter(pk=equipamento.pk).exists())

    def test_recusa_com_historico_e_preserva_tudo(self):
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        with self.assertRaisesMessage(
            ValidationError, mensagens.EXCLUSAO_COM_HISTORICO
        ):
            services.excluir_equipamento(equipamento.pk)
        self.assertTrue(Equipamento.objects.filter(pk=equipamento.pk).exists())
        self.assertEqual(Aluguel.objects.filter(equipamento=equipamento).count(), 1)

    def test_recusa_com_aluguel_aberto(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento, retirada=dias(3), prevista=dias(4))
        with self.assertRaisesMessage(ValidationError, mensagens.ALUGUEL_ATIVO_IMPEDE):
            services.excluir_equipamento(equipamento.pk)
        self.assertTrue(Equipamento.objects.filter(pk=equipamento.pk).exists())


class InativacaoTests(TestCase):
    def test_inativa_sem_historico(self):
        equipamento = criar_equipamento()
        services.inativar_equipamento(equipamento.pk)
        equipamento.refresh_from_db()
        self.assertFalse(equipamento.ativo)

    def test_inativa_com_historico_encerrado(self):
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        services.inativar_equipamento(equipamento.pk)
        equipamento.refresh_from_db()
        self.assertFalse(equipamento.ativo)
        self.assertEqual(Aluguel.objects.filter(equipamento=equipamento).count(), 1)

    def test_recusa_com_aluguel_aberto(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento)
        with self.assertRaisesMessage(ValidationError, mensagens.ALUGUEL_ATIVO_IMPEDE):
            services.inativar_equipamento(equipamento.pk)
        equipamento.refresh_from_db()
        self.assertTrue(equipamento.ativo)

    def test_ja_inativo_nao_muda_nada(self):
        equipamento = criar_equipamento(ativo=False)
        resultado = services.inativar_equipamento(equipamento.pk)
        self.assertFalse(resultado.ativo)


class ReativacaoTests(TestCase):
    def test_reativa_sem_alterar_historico(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        aluguel = encerrar(registrar(equipamento=equipamento))
        services.inativar_equipamento(equipamento.pk)
        services.reativar_equipamento(equipamento.pk)
        equipamento.refresh_from_db()
        aluguel.refresh_from_db()
        self.assertTrue(equipamento.ativo)
        self.assertEqual(aluguel.valor_contratado, Decimal("50.00"))
        self.assertFalse(aluguel.aberto)

    def test_recusa_dados_inconsistentes(self):
        """I3: massa preparada fora da interface (nome só com espaços)."""
        equipamento = criar_equipamento(ativo=False)
        Equipamento.objects.filter(pk=equipamento.pk).update(nome="   ")
        with self.assertRaisesMessage(ValidationError, mensagens.REATIVACAO_BLOQUEADA):
            services.reativar_equipamento(equipamento.pk)
        equipamento.refresh_from_db()
        self.assertFalse(equipamento.ativo)

    def test_ja_ativo_nao_muda_nada(self):
        equipamento = criar_equipamento()
        self.assertTrue(services.reativar_equipamento(equipamento.pk).ativo)


class AvaliarAcoesTests(TestCase):
    def test_sem_historico_e_ativo(self):
        acoes = services.avaliar_acoes(criar_equipamento())
        self.assertEqual(
            (acoes.pode_excluir, acoes.pode_inativar, acoes.pode_reativar),
            (True, True, False),
        )

    def test_com_historico_encerrado(self):
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        acoes = services.avaliar_acoes(equipamento)
        self.assertFalse(acoes.pode_excluir)
        self.assertEqual(acoes.motivo_exclusao, mensagens.EXCLUSAO_COM_HISTORICO)
        self.assertTrue(acoes.pode_inativar)

    def test_com_aluguel_aberto(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento)
        acoes = services.avaliar_acoes(equipamento)
        self.assertFalse(acoes.pode_excluir)
        self.assertFalse(acoes.pode_inativar)
        self.assertEqual(acoes.motivo_exclusao, mensagens.ALUGUEL_ATIVO_IMPEDE)
        self.assertEqual(acoes.motivo_inativacao, mensagens.ALUGUEL_ATIVO_IMPEDE)

    def test_inativo_valido_e_inconsistente(self):
        equipamento = criar_equipamento(ativo=False)
        self.assertTrue(services.avaliar_acoes(equipamento).pode_reativar)
        Equipamento.objects.filter(pk=equipamento.pk).update(nome="   ")
        equipamento.refresh_from_db()
        acoes = services.avaliar_acoes(equipamento)
        self.assertFalse(acoes.pode_reativar)
        self.assertEqual(acoes.motivo_reativacao, mensagens.REATIVACAO_BLOQUEADA)
