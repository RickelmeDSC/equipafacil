"""Cenários CT09, CT10, CT17 e CT18 (QA) automatizados pelas views de clientes.

Execução automatizada, não manual. Expectativas conforme a rastreabilidade
(RF005, RF009, RN002), D12 e D16 (Documento de Casos de Teste v1.4); a
validação acadêmica dos cenários é da equipe de Testes.
"""

from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from clientes.validadores import formatar_cpf
from config import mensagens
from config.tests.fabricas import cpf_valido, criar_cliente, criar_funcionario

CPF = cpf_valido("390533447")


class CenariosDeClientesTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def test_ct09_cliente_com_nome_e_cpf_validos_sem_contatos(self):
        resposta = self.client.post(
            reverse("clientes:criar"),
            {
                "nome_completo": "Maria Fictícia da Silva",
                "cpf": formatar_cpf(CPF),
                "telefone": "",
                "email": "",
            },
        )
        self.assertRedirects(
            resposta, reverse("clientes:lista"), fetch_redirect_response=False
        )
        cliente = Cliente.objects.get()
        self.assertEqual(cliente.cpf, CPF)
        self.assertEqual((cliente.telefone, cliente.email), ("", ""))
        lista = self.client.get(reverse("clientes:lista"))
        self.assertContains(lista, "Maria Fictícia da Silva")
        self.assertContains(lista, formatar_cpf(CPF))

    def test_ct10_cpf_ja_cadastrado_e_recusado(self):
        criar_cliente(cpf=CPF, nome_completo="Cliente Já Cadastrado")
        for entrada in (CPF, formatar_cpf(CPF)):
            with self.subTest(entrada=entrada):
                resposta = self.client.post(
                    reverse("clientes:criar"),
                    {"nome_completo": "Outra Pessoa", "cpf": entrada},
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(
                    resposta.context["form"].errors["cpf"], [mensagens.CPF_DUPLICADO]
                )
                self.assertContains(resposta, mensagens.CPF_DUPLICADO)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_ct17_pesquisa_por_nome_parcial_sem_diferenciar_maiusculas(self):
        maria = criar_cliente(nome_completo="Maria QA Pesquisa", cpf=CPF)
        criar_cliente(nome_completo="João Silva")
        resposta = self.client.get(reverse("clientes:lista"), {"q": "maria qa"})
        self.assertEqual(list(resposta.context["object_list"]), [maria])
        self.assertContains(resposta, "Maria QA Pesquisa")
        self.assertContains(resposta, formatar_cpf(CPF))
        self.assertNotContains(resposta, "João Silva")
        self.assertContains(resposta, 'name="q" value="maria qa"')

    def test_ct18_pesquisa_sem_correspondencia_informa_ausencia(self):
        criar_cliente(nome_completo="Maria QA Pesquisa")
        resposta = self.client.get(
            reverse("clientes:lista"), {"q": "CLIENTE_FANTASMA_999"}
        )
        self.assertEqual(list(resposta.context["object_list"]), [])
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)
        self.assertNotContains(resposta, "Maria QA Pesquisa")
        self.assertNotContains(resposta, "<tbody>")
        self.assertContains(resposta, "Limpar pesquisa")
