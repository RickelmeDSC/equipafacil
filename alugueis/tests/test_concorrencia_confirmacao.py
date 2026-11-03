"""Duas confirmações simultâneas de aluguel pela view (RF006, RN001, D13).

Dois funcionários enviam ``acao=registrar`` para o mesmo equipamento, em
conexões separadas. O primeiro segura a transação aberta; o segundo passa pela
validação do formulário (ainda vê o equipamento disponível), espera o bloqueio
da linha em ``registrar_aluguel`` e, ao prosseguir, recebe o erro de campo. Fica
um único aluguel aberto, sem erro 500.

Só no PostgreSQL: o SQLite ignora select_for_update() e os testes usam um banco
em memória que não é compartilhado entre threads.
"""

from unittest import skipUnless

from django.test import Client, TransactionTestCase

from alugueis.models import Aluguel
from config import mensagens
from config.tests.concorrencia import OK, POSTGRESQL, executar_corrida
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    dias,
    hoje,
)

URL = "/alugueis/novo/"


@skipUnless(POSTGRESQL, "concorrência real exige PostgreSQL")
class ConfirmacoesSimultaneasTests(TransactionTestCase):
    def setUp(self):
        self.equipamento = criar_equipamento()
        self.clientes = [criar_cliente(), criar_cliente()]
        self.navegadores = []
        for numero in range(2):
            navegador = Client()
            navegador.force_login(criar_funcionario(f"funcionario.{numero}"))
            self.navegadores.append(navegador)
        self.respostas: dict[int, object] = {}

    def _confirmar(self, numero: int):
        def enviar():
            self.respostas[numero] = self.navegadores[numero].post(
                URL,
                {
                    "cliente": self.clientes[numero].pk,
                    "equipamento": self.equipamento.pk,
                    "data_retirada": hoje().isoformat(),
                    "data_devolucao_prevista": dias(1).isoformat(),
                    "acao": "registrar",
                },
            )

        return enviar

    def test_um_unico_aluguel_aberto(self):
        primeira, segunda = executar_corrida(
            self, self._confirmar(0), self._confirmar(1)
        )
        self.assertEqual((primeira, segunda), (OK, OK))  # nenhuma exceção (sem 500)
        self.assertEqual(self.respostas[0].status_code, 302)
        self.assertEqual(self.respostas[1].status_code, 200)
        self.assertEqual(
            self.respostas[1].context["form"].errors["equipamento"],
            [mensagens.EQUIPAMENTO_INDISPONIVEL],
        )
        abertos = Aluguel.objects.abertos().filter(equipamento=self.equipamento)
        self.assertEqual(abertos.count(), 1)
        self.assertEqual(abertos.get().cliente_id, self.clientes[0].pk)
