"""Cenários CT01–CT08 (QA) automatizados pelas views de equipamentos.

Execução automatizada, não manual. Expectativas conforme os requisitos vigentes:
CT08 considera D10 (a inativação continua disponível para equipamento com
histórico e sem aluguel aberto).
"""

from decimal import Decimal

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from config import mensagens
from config.tests.fabricas import (
    criar_equipamento,
    criar_funcionario,
    dias,
    encerrar,
    registrar,
)
from equipamentos.models import Categoria, Equipamento

DADOS = {
    "codigo": "FUR-01",
    "nome": "Furadeira",
    "categoria": Categoria.FERRAMENTAS,
    "descricao": "",
    "valor_diaria": "50,00",
}


class CenariosDeEquipamentosTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def test_ct01_cadastro_valido_fica_ativo_e_disponivel(self):
        self.client.post(reverse("equipamentos:criar"), DADOS)
        equipamento = Equipamento.objects.get()
        self.assertTrue(equipamento.ativo)
        self.assertTrue(equipamento.disponivel)

    def test_ct02_codigo_ja_existente_e_recusado(self):
        criar_equipamento(codigo="FUR-01")
        resposta = self.client.post(reverse("equipamentos:criar"), DADOS)
        self.assertEqual(
            resposta.context["form"].errors["codigo"], [mensagens.CODIGO_DUPLICADO]
        )
        self.assertEqual(Equipamento.objects.count(), 1)

    def test_ct03_pesquisa_por_codigo_mostra_disponibilidade_calculada(self):
        alugado = criar_equipamento(codigo="FUR-01")
        registrar(equipamento=alugado)
        resposta = self.client.get(reverse("equipamentos:lista"), {"q": "FUR-01"})
        [linha] = resposta.context["object_list"]
        self.assertEqual(linha.codigo, "FUR-01")
        self.assertFalse(linha.disponivel)
        self.assertContains(resposta, "Indisponível")

    def test_ct04_termo_inexistente_mostra_mensagem(self):
        criar_equipamento()
        resposta = self.client.get(reverse("equipamentos:lista"), {"q": "nada-assim"})
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_ct05_nova_diaria_preserva_valor_contratado(self):
        equipamento = criar_equipamento(codigo="FUR-01", valor_diaria=Decimal("50.00"))
        aluguel = registrar(equipamento=equipamento, prevista=dias(2))
        self.client.post(
            reverse("equipamentos:editar", args=[equipamento.pk]),
            {**DADOS, "valor_diaria": "75,00"},
        )
        aluguel.refresh_from_db()
        self.assertEqual(aluguel.valor_contratado, Decimal("150.00"))

    def test_ct06_diaria_zero_e_recusada(self):
        resposta = self.client.post(
            reverse("equipamentos:criar"), {**DADOS, "valor_diaria": "0,00"}
        )
        self.assertEqual(
            resposta.context["form"].errors["valor_diaria"], [mensagens.DIARIA_INVALIDA]
        )
        self.assertFalse(Equipamento.objects.exists())

    def test_ct07_exclusao_sem_historico_com_confirmacao(self):
        equipamento = criar_equipamento()
        self.client.post(
            reverse("equipamentos:excluir", args=[equipamento.pk]),
            {"confirmacao": "sim"},
        )
        self.assertFalse(Equipamento.objects.exists())

    def test_ct08_exclusao_com_historico_bloqueada_e_inativacao_disponivel(self):
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        resposta = self.client.post(
            reverse("equipamentos:excluir", args=[equipamento.pk]),
            {"confirmacao": "sim"},
        )
        self.assertIn(
            mensagens.EXCLUSAO_COM_HISTORICO,
            [str(m) for m in get_messages(resposta.wsgi_request)],
        )
        self.assertTrue(Equipamento.objects.filter(pk=equipamento.pk).exists())
        contexto = self.client.get(
            reverse("equipamentos:acoes", args=[equipamento.pk])
        ).context
        self.assertTrue(contexto["pode_inativar"])
