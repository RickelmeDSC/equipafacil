"""Restrições de aluguel no banco: valem no PostgreSQL e no SQLite; introspecção só no PostgreSQL."""

from decimal import Decimal
from unittest import skipUnless

from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from alugueis.models import Aluguel
from config.tests.fabricas import criar_cliente, criar_equipamento, dias

POSTGRESQL = connection.vendor == "postgresql"


class RestricoesDoAluguelTests(TestCase):
    """Gravação em lote ignora o modelo e o serviço: o banco precisa recusar sozinho."""

    def setUp(self):
        self.equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        self.cliente = criar_cliente()

    def _aluguel(self, **campos) -> Aluguel:
        dados = {
            "equipamento": self.equipamento,
            "cliente": self.cliente,
            "data_retirada": dias(0),
            "data_devolucao_prevista": dias(0),
            "valor_diaria_contratada": Decimal("50.00"),
            "quantidade_diarias": 1,
            "valor_contratado": Decimal("50.00"),
        }
        dados.update(campos)
        return Aluguel(**dados)

    def _gravar_em_lote(self, *alugueis: Aluguel) -> None:
        with transaction.atomic():
            Aluguel.objects.bulk_create(alugueis)

    def test_indice_parcial_recusa_dois_abertos_do_mesmo_equipamento(self):
        self._gravar_em_lote(self._aluguel())
        with self.assertRaises(IntegrityError):
            self._gravar_em_lote(self._aluguel())

    def test_indice_parcial_aceita_historico_encerrado_e_um_aberto(self):
        self._gravar_em_lote(
            self._aluguel(data_devolucao_real=dias(0)),
            self._aluguel(data_devolucao_real=dias(0)),
            self._aluguel(),
        )
        self.assertEqual(
            Aluguel.objects.filter(equipamento=self.equipamento).count(), 3
        )

    def test_abertos_de_equipamentos_diferentes_sao_aceitos(self):
        outro = criar_equipamento(valor_diaria=Decimal("50.00"))
        self._gravar_em_lote(self._aluguel(), self._aluguel(equipamento=outro))
        self.assertEqual(Aluguel.objects.abertos().count(), 2)

    def test_banco_recusa_datas_e_valores_invalidos(self):
        casos = {
            "prevista antes da retirada": {"data_devolucao_prevista": dias(-1)},
            "devolução antes da retirada": {"data_devolucao_real": dias(-1)},
            "diária zero": {"valor_diaria_contratada": Decimal("0.00")},
            "zero diárias": {"quantidade_diarias": 0},
            "valor zero": {"valor_contratado": Decimal("0.00")},
        }
        for descricao, campos in casos.items():
            with self.subTest(caso=descricao), self.assertRaises(IntegrityError):
                self._gravar_em_lote(self._aluguel(**campos))


@skipUnless(POSTGRESQL, "introspecção específica do PostgreSQL")
class RestricoesNoPostgreSQLTests(TestCase):
    def _definicao_do_indice(self, nome: str) -> str:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT indexdef FROM pg_indexes WHERE indexname = %s", [nome]
            )
            linha = cursor.fetchone()
        self.assertIsNotNone(linha, f"índice {nome} não encontrado")
        return linha[0]

    def test_indice_unico_parcial_do_aluguel_aberto(self):
        definicao = self._definicao_do_indice("aluguel_um_aberto_por_equipamento")
        self.assertIn("CREATE UNIQUE INDEX", definicao)
        self.assertIn("(equipamento_id)", definicao)
        self.assertIn("WHERE (data_devolucao_real IS NULL)", definicao)

    def test_indice_unico_do_codigo_sem_diferenciar_maiusculas(self):
        definicao = self._definicao_do_indice("equipamento_codigo_unico_ci")
        self.assertIn("CREATE UNIQUE INDEX", definicao)
        self.assertIn("lower((codigo)::text)", definicao)

    def test_restricoes_nomeadas_existem(self):
        esperadas = {
            "equipamentos_equipamento": {
                "equipamento_codigo_normalizado",
                "equipamento_nome_preenchido",
                "equipamento_categoria_valida",
                "equipamento_diaria_positiva",
            },
            "clientes_cliente": {
                "cliente_cpf_unico",
                "cliente_cpf_onze_digitos",
                "cliente_cpf_nao_repetido",
                "cliente_telefone_digitos",
                "cliente_nome_preenchido",
            },
            "alugueis_aluguel": {
                "aluguel_prevista_apos_retirada",
                "aluguel_devolucao_apos_retirada",
                "aluguel_valores_positivos",
            },
        }
        with connection.cursor() as cursor:
            for tabela, nomes in esperadas.items():
                with self.subTest(tabela=tabela):
                    existentes = set(
                        connection.introspection.get_constraints(cursor, tabela)
                    )
                    self.assertLessEqual(nomes, existentes)

    def test_chaves_estrangeiras_impedem_apagar_referenciado(self):
        equipamento, cliente = criar_equipamento(), criar_cliente()
        Aluguel.objects.bulk_create(
            [
                Aluguel(
                    equipamento=equipamento,
                    cliente=cliente,
                    data_retirada=dias(0),
                    data_devolucao_prevista=dias(0),
                    valor_diaria_contratada=equipamento.valor_diaria,
                    quantidade_diarias=1,
                    valor_contratado=equipamento.valor_diaria,
                )
            ]
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM equipamentos_equipamento WHERE id = %s",
                        [equipamento.pk],
                    )
                    cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
