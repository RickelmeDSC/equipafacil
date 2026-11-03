"""Serviços de clientes: cadastro e edição com CPF imutável após o primeiro aluguel."""

from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from clientes import services
from clientes.models import Cliente
from clientes.validadores import formatar_cpf
from config import mensagens
from config.tests.fabricas import cpf_valido, criar_cliente, encerrar, registrar

CPF_A = cpf_valido("390533447")
CPF_B = cpf_valido("714602318")
DADOS = {
    "nome_completo": "Maria Fictícia da Silva",
    "cpf": formatar_cpf(CPF_A),
    "telefone": "(81) 99999-8888",
    "email": "maria@exemplo.test",
}


class CadastroTests(TestCase):
    def test_cadastra_normalizado_e_ignora_campos_fora_da_lista(self):
        cliente = services.cadastrar_cliente({**DADOS, "id": 999, "pk": 999})
        cliente.refresh_from_db()
        self.assertNotEqual(cliente.pk, 999)
        self.assertEqual((cliente.cpf, cliente.telefone), (CPF_A, "81999998888"))

    def test_cpf_invalido_nao_e_gravado(self):
        with self.assertRaises(ValidationError) as erro:
            services.cadastrar_cliente({**DADOS, "cpf": "529,982,247-25"})
        self.assertEqual(erro.exception.message_dict["cpf"], [mensagens.CPF_INVALIDO])
        self.assertFalse(Cliente.objects.exists())

    def test_corrida_de_cpf_duplicado_vira_erro_de_campo(self):
        """Se dois cadastros passam juntos pela validação, o índice único decide."""
        criar_cliente(cpf=CPF_A)
        with mock.patch.object(Cliente, "full_clean"):
            with self.assertRaises(ValidationError) as erro:
                # Sem full_clean não há normalização: dados já no formato gravado.
                services.cadastrar_cliente(
                    {**DADOS, "cpf": CPF_A, "telefone": "81999998888"}
                )
        self.assertEqual(erro.exception.message_dict["cpf"], [mensagens.CPF_DUPLICADO])
        self.assertEqual(Cliente.objects.count(), 1)


class EdicaoTests(TestCase):
    def test_sem_aluguel_todos_os_campos_sao_editaveis(self):
        cliente = criar_cliente(cpf=CPF_A)
        services.editar_cliente(
            cliente.pk, {**DADOS, "cpf": CPF_B, "nome_completo": "Outra Pessoa"}
        )
        cliente.refresh_from_db()
        self.assertEqual((cliente.cpf, cliente.nome_completo), (CPF_B, "Outra Pessoa"))

    def test_cpf_bloqueado_com_aluguel_aberto_ou_encerrado(self):
        aberto = criar_cliente(cpf=CPF_A)
        registrar(cliente=aberto)
        encerrado = criar_cliente(cpf=CPF_B)
        encerrar(registrar(cliente=encerrado))
        for cliente in (aberto, encerrado):
            with self.subTest(cpf_original=cliente.cpf):
                novo = cpf_valido("123456780")
                with self.assertRaises(ValidationError) as erro:
                    services.editar_cliente(cliente.pk, {**DADOS, "cpf": novo})
                self.assertEqual(
                    erro.exception.message_dict["cpf"], [mensagens.CPF_BLOQUEADO]
                )
                original = cliente.cpf
                cliente.refresh_from_db()
                self.assertEqual(cliente.cpf, original)

    def test_com_historico_nome_e_contatos_seguem_editaveis(self):
        cliente = criar_cliente(cpf=CPF_A)
        encerrar(registrar(cliente=cliente))
        for cpf in (CPF_A, formatar_cpf(CPF_A)):  # mesmo CPF, com ou sem pontuação
            with self.subTest(cpf=cpf):
                services.editar_cliente(
                    cliente.pk,
                    {
                        "nome_completo": "Nome Corrigido",
                        "cpf": cpf,
                        "telefone": "(81) 3333-4444",
                        "email": "novo@exemplo.test",
                    },
                )
                cliente.refresh_from_db()
                self.assertEqual(
                    (
                        cliente.nome_completo,
                        cliente.cpf,
                        cliente.telefone,
                        cliente.email,
                    ),
                    ("Nome Corrigido", CPF_A, "8133334444", "novo@exemplo.test"),
                )

    def test_cpf_de_outro_cliente_e_recusado(self):
        criar_cliente(cpf=CPF_A)
        cliente = criar_cliente(cpf=CPF_B)
        with self.assertRaises(ValidationError) as erro:
            services.editar_cliente(cliente.pk, {**DADOS, "cpf": formatar_cpf(CPF_A)})
        self.assertEqual(erro.exception.message_dict["cpf"], [mensagens.CPF_DUPLICADO])
        cliente.refresh_from_db()
        self.assertEqual(cliente.cpf, CPF_B)

    def test_cliente_inexistente(self):
        with self.assertRaises(Cliente.DoesNotExist):
            services.editar_cliente(999, DADOS)
