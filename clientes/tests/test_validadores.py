"""Normalização, validação e formatação de CPF e telefone (D12)."""

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from clientes.validadores import (
    formatar_cpf,
    formatar_telefone,
    normalizar_cpf,
    normalizar_telefone,
    validar_cpf,
    validar_telefone,
)
from config import mensagens

CPF_VALIDO = "52998224725"  # CPF fictício de exemplo, com dígitos verificadores válidos


class CpfTests(SimpleTestCase):
    def test_remove_somente_pontos_e_hifen(self):
        self.assertEqual(normalizar_cpf("529.982.247-25"), CPF_VALIDO)
        self.assertEqual(normalizar_cpf(CPF_VALIDO), CPF_VALIDO)
        self.assertEqual(normalizar_cpf(" 529 982/247"), " 529 982/247")

    def test_cpf_valido(self):
        validar_cpf(CPF_VALIDO)
        validar_cpf(normalizar_cpf("111.444.777-35"))

    def test_cpfs_invalidos(self):
        casos = {
            "dígito verificador errado": "52998224726",
            "todos os dígitos iguais": "11111111111",
            "zeros": "00000000000",
            "letras": "5299822472A",
            "barra": normalizar_cpf("529/982/247-25"),
            "espaço": normalizar_cpf("529 982 247 25"),
            "10 dígitos": "5299822472",
            "12 dígitos": "529982247250",
            "dígitos não ASCII": "５２９９８２２４７２５",
            "vazio": "",
        }
        for descricao, valor in casos.items():
            with self.subTest(caso=descricao):
                with self.assertRaisesMessage(ValidationError, mensagens.CPF_INVALIDO):
                    validar_cpf(valor)

    def test_formatacao(self):
        self.assertEqual(formatar_cpf(CPF_VALIDO), "529.982.247-25")


class TelefoneTests(SimpleTestCase):
    def test_remove_a_mascara_usual(self):
        self.assertEqual(normalizar_telefone("(81) 99999-9999"), "81999999999")
        self.assertEqual(normalizar_telefone("(81) 3333-4444"), "8133334444")

    def test_telefones_validos(self):
        for valor in ("81999999999", "8133334444"):
            with self.subTest(valor=valor):
                validar_telefone(valor)

    def test_telefones_invalidos(self):
        casos = {
            "sem DDD": "999999999",
            "12 dígitos": "819999999999",
            "com +55": normalizar_telefone("+55 81 99999-9999"),
            "letras": "81 9999-ABCD",
            "ponto": normalizar_telefone("81.99999.9999"),
        }
        for descricao, valor in casos.items():
            with self.subTest(caso=descricao):
                with self.assertRaisesMessage(
                    ValidationError, mensagens.TELEFONE_INVALIDO
                ):
                    validar_telefone(valor)

    def test_formatacao(self):
        self.assertEqual(formatar_telefone("81999999999"), "(81) 99999-9999")
        self.assertEqual(formatar_telefone("8133334444"), "(81) 3333-4444")
