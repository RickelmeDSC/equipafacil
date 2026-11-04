"""Integração dos formulários com o Bootstrap 5.3 (contrato proposto, seções 5 e 7).

O backend aplica as classes dos widgets (``form-control``, ``form-select`` e
``is-invalid``) para que o frontend não precise editar ``forms.py``; o nível de
mensagem ``error`` vira a classe ``danger`` do Bootstrap.
"""

import secrets

from django.contrib.messages import constants, get_messages
from django.contrib.messages.storage.base import Message
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from alugueis.forms import AluguelForm, DevolucaoForm
from clientes.forms import ClienteForm
from config.formularios import FormularioDeLogin, aplicar_erros
from config.tests.fabricas import (
    criar_equipamento,
    criar_funcionario,
    encerrar,
    hoje,
    registrar,
)
from equipamentos.forms import EquipamentoForm


def _classes(form, campo: str) -> list[str]:
    return form.fields[campo].widget.attrs.get("class", "").split()


class ClassesBaseTests(TestCase):
    def _conferir(self, form, esperado: dict[str, str]):
        for campo, classe in esperado.items():
            with self.subTest(formulario=type(form).__name__, campo=campo):
                self.assertEqual(_classes(form, campo), [classe])

    def test_equipamento(self):
        self._conferir(
            EquipamentoForm(),
            {
                "codigo": "form-control",
                "nome": "form-control",
                "categoria": "form-select",
                "descricao": "form-control",
                "valor_diaria": "form-control",
            },
        )

    def test_cliente(self):
        self._conferir(
            ClienteForm(),
            {
                campo: "form-control"
                for campo in ("nome_completo", "cpf", "telefone", "email")
            },
        )

    def test_aluguel_e_devolucao(self):
        self._conferir(
            AluguelForm(hoje=hoje()),
            {
                "cliente": "form-select",
                "equipamento": "form-select",
                "data_retirada": "form-control",
                "data_devolucao_prevista": "form-control",
            },
        )
        self._conferir(
            DevolucaoForm(data_minima=hoje(), data_maxima=hoje()),
            {"data_devolucao_real": "form-control"},
        )

    def test_login(self):
        self._conferir(
            FormularioDeLogin(),
            {"username": "form-control", "password": "form-control"},
        )

    def test_preserva_atributos_e_somente_leitura(self):
        form = AluguelForm(hoje=hoje())
        self.assertEqual(
            form.fields["data_retirada"].widget.attrs["min"], hoje().isoformat()
        )
        self.assertEqual(form.fields["data_retirada"].widget.input_type, "date")
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        form = EquipamentoForm(instance=equipamento, codigo_editavel=False)
        self.assertTrue(form.fields["codigo"].disabled)
        self.assertEqual(_classes(form, "codigo"), ["form-control"])

    def test_instancias_nao_compartilham_classes(self):
        com_erro = ClienteForm({"nome_completo": "", "cpf": ""})
        com_erro.is_valid()
        self.assertIn("is-invalid", _classes(com_erro, "cpf"))
        self.assertEqual(_classes(ClienteForm(), "cpf"), ["form-control"])


class ClasseDeErroTests(TestCase):
    def test_so_os_campos_com_erro_recebem_is_invalid(self):
        form = ClienteForm(
            {"nome_completo": "Maria Fictícia", "cpf": "123", "email": "x"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(_classes(form, "cpf"), ["form-control", "is-invalid"])
        self.assertEqual(_classes(form, "email"), ["form-control", "is-invalid"])
        self.assertEqual(_classes(form, "nome_completo"), ["form-control"])
        self.assertEqual(_classes(form, "telefone"), ["form-control"])

    def test_erro_vindo_do_servico_tambem_marca_o_campo(self):
        form = ClienteForm({"nome_completo": "Maria Fictícia", "cpf": "52998224725"})
        self.assertTrue(form.is_valid())
        aplicar_erros(
            form, ValidationError({"cpf": "Já existe um cliente com este CPF."})
        )
        self.assertEqual(_classes(form, "cpf"), ["form-control", "is-invalid"])
        aplicar_erros(form, ValidationError("Erro geral."))
        self.assertEqual(form.non_field_errors(), ["Erro geral."])
        self.assertEqual(_classes(form, "nome_completo"), ["form-control"])

    def test_html_renderizado(self):
        form = AluguelForm({"cliente": "", "equipamento": ""}, hoje=hoje())
        self.assertFalse(form.is_valid())
        html = str(form["equipamento"])
        self.assertIn('class="form-select is-invalid"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertNotIn("is-invalid", str(FormularioDeLogin()["username"]))


class NivelDeMensagemTests(SimpleTestCase):
    def test_error_vira_danger(self):
        self.assertEqual(Message(constants.ERROR, "x").tags, "danger")
        for nivel, classe in (
            (constants.SUCCESS, "success"),
            (constants.WARNING, "warning"),
            (constants.INFO, "info"),
        ):
            with self.subTest(classe=classe):
                self.assertEqual(Message(nivel, "x").tags, classe)


class IntegracaoComAsViewsTests(TestCase):
    def test_mensagem_de_erro_de_p04_usa_danger(self):
        self.client.force_login(criar_funcionario())
        equipamento = criar_equipamento()
        encerrar(registrar(equipamento=equipamento))
        resposta = self.client.post(
            reverse("equipamentos:excluir", args=[equipamento.pk]),
            {"confirmacao": "sim"},
        )
        [mensagem] = list(get_messages(resposta.wsgi_request))
        self.assertEqual(mensagem.tags, "danger")

    def test_login_usa_o_formulario_com_classes_e_continua_funcionando(self):
        resposta = self.client.get(reverse("login"))
        self.assertIsInstance(resposta.context["form"], FormularioDeLogin)
        for campo in ("username", "password"):
            with self.subTest(campo=campo):
                html = str(resposta.context["form"][campo])
                self.assertIn('class="form-control"', html)
        usuario = criar_funcionario("funcionario.login")
        senha = secrets.token_urlsafe(16)  # temporária, só deste teste
        usuario.set_password(senha)
        usuario.save()
        resposta = self.client.post(
            reverse("login"), {"username": "funcionario.login", "password": senha}
        )
        self.assertRedirects(resposta, reverse("inicio"), fetch_redirect_response=False)
