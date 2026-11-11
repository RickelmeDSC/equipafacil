"""Cenários CT11–CT16, CT19 e CT20 (QA) automatizados pelas views de aluguéis.

Execução automatizada, não manual. Expectativas conforme a rastreabilidade
(RF006–RF008, RF010, RN001, RN004). As correções da auditoria QA-AUD-01 não
estavam disponíveis nesta sessão; a validação acadêmica é da equipe de Testes.
CT16 é obrigatório mesmo ausente do documento v1.1 da equipe de QA. CT19 e CT20
vêm do Documento de Casos de Teste v1.4.
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from alugueis.models import Aluguel, Situacao
from config import mensagens
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    dias,
    encerrar,
    hoje,
    registrar,
)
from equipamentos.models import Equipamento


class CenariosDeAlugueisTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())
        self.cliente = criar_cliente(nome_completo="Cliente do Cenário")
        self.equipamento = criar_equipamento(
            codigo="BET-01", nome="Betoneira", valor_diaria=Decimal("50.00")
        )

    def _alugar(self, equipamento=None):
        return self.client.post(
            reverse("alugueis:criar"),
            {
                "cliente": self.cliente.pk,
                "equipamento": (equipamento or self.equipamento).pk,
                "data_retirada": hoje().isoformat(),
                "data_devolucao_prevista": dias(2).isoformat(),
                "acao": "registrar",
            },
        )

    def _devolver(self, aluguel):
        return self.client.post(
            reverse("alugueis:devolver", args=[aluguel.pk]),
            {"data_devolucao_real": hoje().isoformat()},
        )

    def test_ct11_tres_diarias_a_50_reais_contratam_150_reais(self):
        resposta = self._alugar()
        self.assertRedirects(
            resposta, reverse("alugueis:historico"), fetch_redirect_response=False
        )
        aluguel = Aluguel.objects.get()
        self.assertEqual(aluguel.quantidade_diarias, 3)
        self.assertEqual(aluguel.valor_diaria_contratada, Decimal("50.00"))
        self.assertEqual(aluguel.valor_contratado, Decimal("150.00"))
        self.assertTrue(aluguel.aberto)

    def test_ct12_equipamento_com_aluguel_ativo_e_recusado(self):
        registrar(equipamento=self.equipamento)
        resposta = self._alugar()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context["form"].errors["equipamento"],
            [mensagens.EQUIPAMENTO_INDISPONIVEL],
        )
        self.assertEqual(Aluguel.objects.count(), 1)

    def test_ct13_devolucao_com_data_atual_encerra_e_libera(self):
        aluguel = registrar(equipamento=self.equipamento, prevista=dias(2))
        resposta = self._devolver(aluguel)
        self.assertRedirects(
            resposta, reverse("alugueis:historico"), fetch_redirect_response=False
        )
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, hoje())
        self.assertEqual(aluguel.situacao_codigo(), Situacao.ENCERRADO)
        self.assertTrue(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)

    def test_ct14_segunda_devolucao_e_recusada(self):
        aluguel = registrar(equipamento=self.equipamento)
        self._devolver(aluguel)
        resposta = self._devolver(aluguel)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context["form"].non_field_errors(), [mensagens.ALUGUEL_ENCERRADO]
        )
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.data_devolucao_real, hoje())

    def test_ct15_historico_mostra_dados_e_situacao(self):
        registrar(equipamento=self.equipamento, cliente=self.cliente, prevista=dias(2))
        resposta = self.client.get(reverse("alugueis:historico"))
        [aluguel] = resposta.context["object_list"]
        self.assertEqual(aluguel.situacao(), "Ativo")
        for texto in (
            "Cliente do Cenário",
            "BET-01 — Betoneira",
            hoje().strftime("%d/%m/%Y"),
            dias(2).strftime("%d/%m/%Y"),
            "R$ 50,00",
            "R$ 150,00",
            ">Ativo</td>",
        ):
            self.assertContains(resposta, texto)

    def test_ct16_historico_vazio_sem_dados_inexistentes(self):
        resposta = self.client.get(reverse("alugueis:historico"))
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
        self.assertNotContains(resposta, "R$")
        self.assertNotContains(resposta, "Registrar devolução")

    def _historico(self, **params):
        resposta = self.client.get(reverse("alugueis:historico"), params)
        self.assertEqual(resposta.status_code, 200)
        return resposta

    def _ativo_e_encerrado(self):
        ativo = registrar(
            equipamento=self.equipamento, cliente=self.cliente, prevista=dias(2)
        )
        encerrado = encerrar(
            registrar(
                equipamento=criar_equipamento(codigo="FUR-01", nome="Furadeira"),
                prevista=dias(1),
            ),
            hoje(),
        )
        return ativo, encerrado

    def test_ct19_filtro_por_situacao_mostra_so_a_situacao_escolhida(self):
        ativo, encerrado = self._ativo_e_encerrado()
        self.assertEqual(ativo.situacao(), "Ativo")
        resposta = self._historico(situacao=Situacao.ENCERRADO)
        self.assertEqual(list(resposta.context["object_list"]), [encerrado])
        self.assertContains(resposta, ">Encerrado</td>")
        self.assertContains(resposta, "FUR-01 — Furadeira")
        self.assertNotContains(resposta, ">Ativo</td>")
        self.assertNotContains(resposta, "BET-01 — Betoneira")
        self.assertContains(
            resposta, '<option value="encerrado" selected>Encerrado</option>'
        )

    def test_ct20_situacao_sem_registros_informa_ausencia(self):
        self._ativo_e_encerrado()
        todas = self._historico()
        self.assertEqual(len(todas.context["object_list"]), 2)
        self.assertNotContains(todas, ">Encerrado com atraso</td>")  # pré-condição
        resposta = self._historico(situacao=Situacao.ENCERRADO_COM_ATRASO)
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
        self.assertNotContains(resposta, "<tbody>")
        self.assertNotContains(resposta, "R$")
        self.assertContains(resposta, "Limpar filtro")
        self.assertContains(
            resposta,
            '<option value="encerrado_com_atraso" selected>'
            "Encerrado com atraso</option>",
        )
