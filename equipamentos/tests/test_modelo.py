"""Equipamento: validações, normalização do código (D11), situação e disponibilidade."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from config import mensagens
from config.tests.fabricas import criar_equipamento, dias, encerrar, registrar
from equipamentos.models import Categoria, Equipamento


def _erros(equipamento: Equipamento) -> dict[str, list[str]]:
    try:
        equipamento.full_clean()
    except ValidationError as erro:
        return erro.message_dict
    return {}


def _novo(**campos) -> Equipamento:
    dados = {
        "codigo": "NOVO-01",
        "nome": "Furadeira",
        "categoria": Categoria.FERRAMENTAS,
        "valor_diaria": Decimal("35.50"),
    }
    dados.update(campos)
    return Equipamento(**dados)


class CodigoTests(TestCase):
    def test_codigo_valido_cria_equipamento_ativo(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        equipamento.refresh_from_db()
        self.assertEqual(equipamento.codigo, "FUR-01")
        self.assertTrue(equipamento.ativo)
        self.assertTrue(equipamento.disponivel)

    def test_espacos_externos_removidos_e_grafia_preservada(self):
        equipamento = criar_equipamento(codigo="  Fur-Ab 01  ")
        equipamento.refresh_from_db()
        self.assertEqual(equipamento.codigo, "Fur-Ab 01")

    def test_codigo_duplicado_sem_diferenciar_maiusculas(self):
        criar_equipamento(codigo="FUR-01")
        for codigo in ("fur-01", "Fur-01", "  FUR-01 "):
            with self.subTest(codigo=codigo):
                erros = _erros(_novo(codigo=codigo))
                self.assertEqual(erros["codigo"], [mensagens.CODIGO_DUPLICADO])

    def test_editar_o_proprio_equipamento_nao_acusa_duplicidade(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        equipamento.nome = "Furadeira de impacto"
        equipamento.save()
        self.assertEqual(Equipamento.objects.get().nome, "Furadeira de impacto")

    def test_codigo_obrigatorio(self):
        for codigo in ("", "   "):
            with self.subTest(codigo=repr(codigo)):
                self.assertEqual(
                    _erros(_novo(codigo=codigo))["codigo"],
                    [mensagens.CAMPO_OBRIGATORIO],
                )

    def test_codigo_editavel_sem_aluguel_e_bloqueado_depois(self):
        equipamento = criar_equipamento(codigo="FUR-01")
        self.assertTrue(equipamento.codigo_editavel)
        equipamento.codigo = "FUR-02"
        equipamento.save()

        registrar(equipamento=equipamento)
        equipamento.refresh_from_db()
        self.assertFalse(equipamento.codigo_editavel)
        for codigo in ("FUR-03", "fur-02"):  # inclui mudança só de maiúsculas
            with self.subTest(codigo=codigo):
                equipamento.codigo = codigo
                self.assertEqual(
                    _erros(equipamento)["codigo"], [mensagens.CODIGO_BLOQUEADO]
                )


class CamposTests(TestCase):
    def test_nome_obrigatorio(self):
        for nome in ("", "   "):
            with self.subTest(nome=repr(nome)):
                self.assertEqual(
                    _erros(_novo(nome=nome))["nome"], [mensagens.CAMPO_OBRIGATORIO]
                )

    def test_diaria_invalida(self):
        for valor in (
            Decimal("0"),
            Decimal("0.00"),
            Decimal("-10.00"),
            Decimal("10.005"),
        ):
            with self.subTest(valor=valor):
                self.assertEqual(
                    _erros(_novo(valor_diaria=valor))["valor_diaria"],
                    [mensagens.DIARIA_INVALIDA],
                )

    def test_diaria_ausente(self):
        self.assertEqual(
            _erros(_novo(valor_diaria=None))["valor_diaria"],
            [mensagens.CAMPO_OBRIGATORIO],
        )

    def test_diaria_valida_com_ate_duas_casas(self):
        for valor in (Decimal("0.01"), Decimal("1500.5"), Decimal("1500.50")):
            with self.subTest(valor=valor):
                self.assertEqual(_erros(_novo(valor_diaria=valor)), {})

    def test_categoria_invalida(self):
        self.assertEqual(
            _erros(_novo(categoria="jardinagem"))["categoria"],
            [mensagens.CATEGORIA_INVALIDA],
        )

    def test_as_cinco_categorias_fixas(self):
        self.assertEqual(
            Categoria.labels,
            [
                "Ferramentas",
                "Equipamentos Audiovisuais",
                "Informática",
                "Construção Civil",
                "Outros",
            ],
        )
        for numero, categoria in enumerate(Categoria.values):
            with self.subTest(categoria=categoria):
                criar_equipamento(codigo=f"CAT-{numero}", categoria=categoria)

    def test_descricao_opcional(self):
        self.assertEqual(_erros(_novo(descricao="")), {})


class SituacaoEDisponibilidadeTests(TestCase):
    def test_disponibilidade_nao_e_campo_persistido(self):
        campos = {campo.name for campo in Equipamento._meta.get_fields()}
        self.assertNotIn("disponivel", campos)
        self.assertNotIn("disponibilidade", campos)

    def test_ativo_por_padrao_e_inativo_indisponivel(self):
        equipamento = criar_equipamento()
        self.assertTrue(equipamento.disponivel)
        equipamento.ativo = False
        equipamento.save()
        self.assertFalse(equipamento.disponivel)
        self.assertNotIn(equipamento, Equipamento.objects.disponiveis())

    def test_aluguel_aberto_torna_indisponivel_e_devolucao_libera(self):
        equipamento = criar_equipamento()
        aluguel = registrar(equipamento=equipamento)
        self.assertFalse(equipamento.disponivel)
        self.assertNotIn(equipamento, Equipamento.objects.disponiveis())
        encerrar(aluguel)
        self.assertTrue(equipamento.disponivel)
        self.assertIn(equipamento, Equipamento.objects.disponiveis())

    def test_retirada_futura_reserva_imediatamente(self):
        equipamento = criar_equipamento()
        registrar(equipamento=equipamento, retirada=dias(5), prevista=dias(7))
        self.assertFalse(equipamento.disponivel)


class RestricoesDoBancoTests(TestCase):
    """Gravação em lote ignora a validação do modelo: o banco precisa recusar sozinho."""

    def _gravar_em_lote(self, **campos) -> None:
        with transaction.atomic():
            Equipamento.objects.bulk_create([_novo(**campos)])

    def test_banco_recusa_codigo_duplicado_sem_diferenciar_maiusculas(self):
        criar_equipamento(codigo="FUR-01")
        with self.assertRaises(IntegrityError):
            self._gravar_em_lote(codigo="fur-01")

    def test_banco_recusa_valores_invalidos(self):
        casos = {
            "código com espaço externo": {"codigo": " FUR-09"},
            "código vazio": {"codigo": ""},
            "nome vazio": {"nome": ""},
            "categoria fora da lista": {"categoria": "jardinagem"},
            "diária zero": {"valor_diaria": Decimal("0.00")},
            "diária negativa": {"valor_diaria": Decimal("-1.00")},
        }
        for descricao, campos in casos.items():
            with self.subTest(caso=descricao), self.assertRaises(IntegrityError):
                self._gravar_em_lote(**campos)
