"""Clientes sob concorrência: troca de CPF × primeiro aluguel e cadastros simultâneos.

Protocolo: ``registrar_aluguel`` bloqueia o equipamento e depois o cliente; a
edição de cliente bloqueia só o cliente. Não há ciclo de espera, e quem bloqueia
o cliente por último decide com o estado gravado pelo primeiro. Cadastros
simultâneos com o mesmo CPF são decididos pelo índice único.

Só no PostgreSQL: o SQLite ignora select_for_update() e os testes usam um banco
em memória que não é compartilhado entre threads.
"""

from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.test import TransactionTestCase

from alugueis.models import Aluguel
from alugueis.services import registrar_aluguel
from clientes import services
from clientes.models import Cliente
from clientes.validadores import formatar_cpf
from config import mensagens
from config.tests.concorrencia import OK, POSTGRESQL, executar_corrida
from config.tests.fabricas import (
    cpf_valido,
    criar_cliente,
    criar_equipamento,
    dias,
    hoje,
)

CPF_ORIGINAL = cpf_valido("390533447")
CPF_NOVO = cpf_valido("714602318")


@skipUnless(POSTGRESQL, "concorrência real exige PostgreSQL")
class CpfVersusPrimeiroAluguelTests(TransactionTestCase):
    def setUp(self):
        self.cliente = criar_cliente(cpf=CPF_ORIGINAL, nome_completo="Maria Fictícia")
        self.equipamento = criar_equipamento()

    def _alugar(self) -> None:
        registrar_aluguel(
            cliente_id=self.cliente.pk,
            equipamento_id=self.equipamento.pk,
            data_retirada=hoje(),
            data_devolucao_prevista=dias(1),
            hoje=hoje(),
        )

    def _trocar_cpf(self) -> None:
        services.editar_cliente(
            self.cliente.pk,
            {
                "nome_completo": "Maria Fictícia",
                "cpf": formatar_cpf(CPF_NOVO),
                "telefone": "",
                "email": "",
            },
        )

    def _cpf_gravado(self) -> str:
        return Cliente.objects.get(pk=self.cliente.pk).cpf

    def test_31_edicao_primeiro_o_aluguel_espera_e_usa_o_cpf_novo(self):
        """Cenário A: ordem serial edição → aluguel; sem impasse."""
        primeira, segunda = executar_corrida(self, self._trocar_cpf, self._alugar)
        self.assertEqual((primeira, segunda), (OK, OK))
        self.assertEqual(self._cpf_gravado(), CPF_NOVO)
        self.assertEqual(Aluguel.objects.get().cliente_id, self.cliente.pk)
        # Daqui em diante o CPF está congelado.
        with self.assertRaisesMessage(ValidationError, mensagens.CPF_BLOQUEADO):
            services.editar_cliente(self.cliente.pk, {"cpf": CPF_ORIGINAL})

    def test_32_aluguel_primeiro_a_edicao_espera_e_e_recusada(self):
        """Cenário B: a edição encontra o histórico e recusa a troca."""
        primeira, segunda = executar_corrida(self, self._alugar, self._trocar_cpf)
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.CPF_BLOQUEADO])
        self.assertEqual(self._cpf_gravado(), CPF_ORIGINAL)
        self.assertEqual(Aluguel.objects.count(), 1)


@skipUnless(POSTGRESQL, "concorrência real exige PostgreSQL")
class CadastrosSimultaneosTests(TransactionTestCase):
    def _cadastrar(self, nome: str, cpf: str):
        return lambda: services.cadastrar_cliente({"nome_completo": nome, "cpf": cpf})

    def test_33_34_mesmo_cpf_um_grava_o_outro_recebe_erro_de_campo(self):
        """Cenário C: a segunda gravação espera no índice único e é recusada."""
        cpf = cpf_valido("123456780")
        primeira, segunda = executar_corrida(
            self,
            self._cadastrar("Primeira Pessoa", cpf),
            self._cadastrar("Segunda Pessoa", formatar_cpf(cpf)),
        )
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.CPF_DUPLICADO])
        # 34: integridade preservada e banco utilizável depois do conflito.
        self.assertEqual(
            list(Cliente.objects.values_list("nome_completo", "cpf")),
            [("Primeira Pessoa", cpf)],
        )
        outro = services.cadastrar_cliente(
            {"nome_completo": "Terceira Pessoa", "cpf": cpf_valido("987654320")}
        )
        self.assertEqual(Cliente.objects.count(), 2)
        self.assertTrue(Cliente.objects.filter(pk=outro.pk).exists())

    def test_34_edicoes_simultaneas_para_o_mesmo_cpf(self):
        """Dois clientes trocando para o mesmo CPF: só a primeira troca grava."""
        cpf = cpf_valido("123456780")
        ana = criar_cliente(nome_completo="Ana Fictícia")
        bia = criar_cliente(nome_completo="Bia Fictícia")
        originais = {ana.pk: ana.cpf, bia.pk: bia.cpf}
        primeira, segunda = executar_corrida(
            self,
            lambda: services.editar_cliente(ana.pk, {"cpf": cpf}),
            lambda: services.editar_cliente(bia.pk, {"cpf": formatar_cpf(cpf)}),
        )
        self.assertEqual(primeira, OK)
        self.assertEqual(segunda, [mensagens.CPF_DUPLICADO])
        gravados = dict(Cliente.objects.values_list("pk", "cpf"))
        self.assertEqual(gravados, {ana.pk: cpf, bia.pk: originais[bia.pk]})
