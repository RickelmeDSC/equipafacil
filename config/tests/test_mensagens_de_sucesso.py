"""Mensagens de sucesso (RF001 e CT01; contrato proposto, seção 8).

O Documento de Requisitos v1.2 exige "mensagem de sucesso" no cadastro de
equipamento (RF001), e o CT01 a verifica. O EQF-5 não define os textos: os de
``config/mensagens.py`` são o padrão de implementação adotado, sem aprovação
formal da equipe.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.messages import constants, get_messages
from django.test import TestCase
from django.urls import reverse

from alugueis.models import Aluguel
from config import mensagens
from config.tests.fabricas import (
    cpf_valido,
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    encerrar,
    hoje,
    registrar,
)
from equipamentos.models import Categoria


class MensagensDeSucessoTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def _uma_mensagem(self, resposta, texto: str):
        """Segue o redirecionamento, como o navegador: a página de destino recebe
        (e consome) exatamente uma mensagem de sucesso."""
        self.assertEqual(resposta.status_code, 302)
        destino = self.client.get(resposta["Location"])
        self.assertEqual(destino.status_code, 200)
        [mensagem] = list(destino.context["messages"])
        self.assertEqual(mensagem.level, constants.SUCCESS)
        self.assertEqual(mensagem.tags, "success")
        self.assertEqual(str(mensagem), texto)

    def _sem_sucesso(self, resposta):
        niveis = [m.level for m in get_messages(resposta.wsgi_request)]
        self.assertNotIn(constants.SUCCESS, niveis)

    def test_equipamento_cadastro_e_edicao(self):
        dados = {
            "codigo": "FUR-001",
            "nome": "Furadeira Impacto",
            "categoria": Categoria.FERRAMENTAS,
            "descricao": "Furadeira profissional",
            "valor_diaria": "50,00",
        }
        resposta = self.client.post(reverse("equipamentos:criar"), dados)
        self._uma_mensagem(resposta, mensagens.EQUIPAMENTO_CADASTRADO)
        equipamento = criar_equipamento()
        resposta = self.client.post(
            reverse("equipamentos:editar", args=[equipamento.pk]),
            {**dados, "codigo": equipamento.codigo, "valor_diaria": "60,00"},
        )
        self._uma_mensagem(resposta, mensagens.EQUIPAMENTO_ATUALIZADO)

    def test_equipamento_exclusao_inativacao_e_reativacao(self):
        excluido = criar_equipamento()
        resposta = self.client.post(
            reverse("equipamentos:excluir", args=[excluido.pk]), {"confirmacao": "sim"}
        )
        self._uma_mensagem(resposta, mensagens.EQUIPAMENTO_EXCLUIDO)
        equipamento = criar_equipamento()
        resposta = self.client.post(
            reverse("equipamentos:inativar", args=[equipamento.pk])
        )
        self._uma_mensagem(resposta, mensagens.EQUIPAMENTO_INATIVADO)
        resposta = self.client.post(
            reverse("equipamentos:reativar", args=[equipamento.pk])
        )
        self._uma_mensagem(resposta, mensagens.EQUIPAMENTO_REATIVADO)

    def test_cliente_cadastro_e_edicao(self):
        dados = {"nome_completo": "João Silva", "cpf": cpf_valido("390533447")}
        resposta = self.client.post(reverse("clientes:criar"), dados)
        self._uma_mensagem(resposta, mensagens.CLIENTE_CADASTRADO)
        cliente = criar_cliente()
        resposta = self.client.post(
            reverse("clientes:editar", args=[cliente.pk]),
            {"nome_completo": "Nome Corrigido", "cpf": cliente.cpf},
        )
        self._uma_mensagem(resposta, mensagens.CLIENTE_ATUALIZADO)

    def test_aluguel_e_devolucao(self):
        equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        resposta = self.client.post(
            reverse("alugueis:criar"),
            {
                "cliente": criar_cliente().pk,
                "equipamento": equipamento.pk,
                "data_retirada": hoje().isoformat(),
                "data_devolucao_prevista": (hoje() + timedelta(days=2)).isoformat(),
                "acao": "registrar",
            },
        )
        self._uma_mensagem(resposta, mensagens.ALUGUEL_REGISTRADO)
        aluguel = Aluguel.objects.get()
        resposta = self.client.post(
            reverse("alugueis:devolver", args=[aluguel.pk]),
            {"data_devolucao_real": hoje().isoformat()},
        )
        self._uma_mensagem(resposta, mensagens.DEVOLUCAO_REGISTRADA)

    def test_recusas_nao_geram_mensagem_de_sucesso(self):
        criar_equipamento(codigo="FUR-001")
        resposta = self.client.post(
            reverse("equipamentos:criar"),
            {
                "codigo": "fur-001",
                "nome": "Outra",
                "categoria": Categoria.FERRAMENTAS,
                "valor_diaria": "50,00",
            },
        )
        self.assertEqual(resposta.status_code, 200)
        self._sem_sucesso(resposta)
        com_historico = criar_equipamento()
        encerrar(registrar(equipamento=com_historico))
        resposta = self.client.post(
            reverse("equipamentos:excluir", args=[com_historico.pk]),
            {"confirmacao": "sim"},
        )
        self._sem_sucesso(resposta)
        resposta = self.client.post(
            reverse("alugueis:criar"),
            {
                "cliente": criar_cliente().pk,
                "equipamento": com_historico.pk,
                "data_retirada": hoje().isoformat(),
                "data_devolucao_prevista": hoje().isoformat(),
                "acao": "previa",
            },
        )
        self._sem_sucesso(resposta)
