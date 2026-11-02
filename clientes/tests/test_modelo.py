"""Cliente: CPF com 11 dígitos (I5), unicidade, imutabilidade e campos opcionais (D12)."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from clientes.models import Cliente
from config import mensagens
from config.tests.fabricas import criar_cliente, registrar

CPF_VALIDO = "52998224725"


def _erros(cliente: Cliente) -> dict[str, list[str]]:
    try:
        cliente.full_clean()
    except ValidationError as erro:
        return erro.message_dict
    return {}


def _novo(**campos) -> Cliente:
    dados = {"nome_completo": "Maria Fictícia da Silva", "cpf": CPF_VALIDO}
    dados.update(campos)
    return Cliente(**dados)


class CpfTests(TestCase):
    def test_cpf_com_e_sem_pontuacao_persiste_onze_digitos(self):
        for entrada in ("529.982.247-25", CPF_VALIDO):
            with self.subTest(entrada=entrada):
                Cliente.objects.all().delete()
                cliente = criar_cliente(cpf=entrada)
                cliente.refresh_from_db()
                self.assertEqual(cliente.cpf, CPF_VALIDO)
                self.assertEqual(cliente.cpf_formatado, "529.982.247-25")

    def test_cpf_duplicado_com_ou_sem_pontuacao(self):
        criar_cliente(cpf=CPF_VALIDO)
        for entrada in (CPF_VALIDO, "529.982.247-25"):
            with self.subTest(entrada=entrada):
                self.assertEqual(
                    _erros(_novo(cpf=entrada))["cpf"], [mensagens.CPF_DUPLICADO]
                )

    def test_cpf_invalido_gera_uma_unica_mensagem(self):
        casos = {
            "dígito verificador": "529.982.247-26",
            "dígitos repetidos": "111.111.111-11",
            "caracteres não permitidos": "529/982/247-25",
            "letras": "52998224A25",
            "longo demais": "529.982.247-250",
        }
        for descricao, entrada in casos.items():
            with self.subTest(caso=descricao):
                self.assertEqual(
                    _erros(_novo(cpf=entrada))["cpf"], [mensagens.CPF_INVALIDO]
                )

    def test_cpf_obrigatorio(self):
        self.assertEqual(_erros(_novo(cpf=""))["cpf"], [mensagens.CAMPO_OBRIGATORIO])

    def test_cpf_editavel_sem_aluguel_e_bloqueado_depois(self):
        cliente = criar_cliente()
        self.assertTrue(cliente.cpf_editavel)
        cliente.cpf = "111.444.777-35"
        cliente.save()
        cliente.refresh_from_db()
        self.assertEqual(cliente.cpf, "11144477735")

        registrar(cliente=cliente)
        self.assertFalse(cliente.cpf_editavel)
        cliente.cpf = CPF_VALIDO
        self.assertEqual(_erros(cliente)["cpf"], [mensagens.CPF_BLOQUEADO])
        cliente.cpf = "111.444.777-35"  # mesmo CPF, só com pontuação: não é alteração
        self.assertEqual(_erros(cliente), {})


class CamposTests(TestCase):
    def test_nome_completo_obrigatorio(self):
        for nome in ("", "   "):
            with self.subTest(nome=repr(nome)):
                self.assertEqual(
                    _erros(_novo(nome_completo=nome))["nome_completo"],
                    [mensagens.CAMPO_OBRIGATORIO],
                )

    def test_telefone_e_email_opcionais(self):
        cliente = criar_cliente(telefone="", email="")
        self.assertEqual(cliente.telefone, "")
        self.assertEqual(cliente.email, "")

    def test_telefone_com_mascara_persiste_digitos(self):
        cliente = criar_cliente(telefone="(81) 99999-9999")
        cliente.refresh_from_db()
        self.assertEqual(cliente.telefone, "81999999999")
        self.assertEqual(cliente.telefone_formatado, "(81) 99999-9999")

    def test_telefone_invalido(self):
        for telefone in ("99999-9999", "+55 81 99999-9999", "(81) 9999-ABCD"):
            with self.subTest(telefone=telefone):
                self.assertEqual(
                    _erros(_novo(telefone=telefone))["telefone"],
                    [mensagens.TELEFONE_INVALIDO],
                )

    def test_email_invalido(self):
        self.assertEqual(
            _erros(_novo(email="nao-e-email"))["email"], [mensagens.EMAIL_INVALIDO]
        )
        self.assertEqual(_erros(_novo(email="maria@exemplo.test")), {})

    def test_sem_campo_de_endereco(self):
        campos = {campo.name for campo in Cliente._meta.get_fields()}
        self.assertFalse({"endereco", "endereço", "cep"} & campos)


class RestricoesDoBancoTests(TestCase):
    def _gravar_em_lote(self, **campos) -> None:
        with transaction.atomic():
            Cliente.objects.bulk_create([_novo(**campos)])

    def test_banco_recusa_cpf_duplicado(self):
        criar_cliente(cpf=CPF_VALIDO)
        with self.assertRaises(IntegrityError):
            self._gravar_em_lote(cpf=CPF_VALIDO)

    def test_banco_recusa_valores_invalidos(self):
        casos = {
            "CPF com pontuação": {"cpf": "529.982.247"},
            "CPF com letras": {"cpf": "5299822472A"},
            "CPF com 10 dígitos": {"cpf": "5299822472"},
            "CPF com dígitos repetidos": {"cpf": "11111111111"},
            "telefone com 9 dígitos": {"telefone": "999999999"},
            "telefone com máscara": {"telefone": "(81)9999-99"},
            "nome vazio": {"nome_completo": ""},
        }
        for descricao, campos in casos.items():
            with self.subTest(caso=descricao), self.assertRaises(IntegrityError):
                self._gravar_em_lote(**campos)
