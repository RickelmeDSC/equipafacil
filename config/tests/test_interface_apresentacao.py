"""Ajustes de interface para a apresentação (tarefa 18B; DEV-07).

Cobrem só o que o servidor renderiza: os formulários que gravam levam
``data-envio-unico`` (o comportamento fica em static/js/envio-unico.js), as
ajudas das datas e do CPF e a região da estimativa de P07. Nenhuma regra de
negócio muda; os testes de domínio continuam nos módulos de cada app.
"""

from django.test import TestCase
from django.urls import reverse

from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    encerrar,
    hoje,
    registrar,
)

AJUDA_DO_CPF = "Com ou sem pontos e hífen."
SCRIPT_DE_ENVIO_UNICO = "js/envio-unico.js"


class EnvioUnicoTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def test_formularios_que_gravam_marcados_e_script_carregado(self):
        aberto = registrar()
        equipamento = criar_equipamento()
        cliente = criar_cliente()
        for url in (
            reverse("equipamentos:criar"),
            reverse("equipamentos:editar", args=[equipamento.pk]),
            reverse("clientes:criar"),
            reverse("clientes:editar", args=[cliente.pk]),
            reverse("alugueis:criar"),
            reverse("alugueis:devolver", args=[aberto.pk]),
        ):
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(
                    resposta, 'method="post" novalidate data-envio-unico>'
                )
                self.assertContains(resposta, SCRIPT_DE_ENVIO_UNICO)


class AjudasDasDatasTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def test_novo_aluguel_orienta_as_datas_e_esconde_a_estimativa(self):
        criar_cliente()
        criar_equipamento()
        resposta = self.client.get(reverse("alugueis:criar"))
        self.assertContains(resposta, "Hoje ou uma data futura.")
        self.assertContains(resposta, "Igual ou posterior à retirada.")
        self.assertContains(
            resposta,
            '<p class="eqf-estimativa" id="previa-ao-vivo" hidden></p>',
            html=True,
        )

    def test_devolucao_mostra_o_intervalo_em_dia_mes_ano(self):
        aberto = registrar()
        resposta = self.client.get(reverse("alugueis:devolver", args=[aberto.pk]))
        data = hoje().strftime("%d/%m/%Y")
        self.assertContains(resposta, f"Entre {data} (retirada) e {data} (hoje).")


class AjudaDoCpfTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())

    def test_ajuda_aparece_com_cpf_editavel(self):
        cliente = criar_cliente()
        for url in (
            reverse("clientes:criar"),
            reverse("clientes:editar", args=[cliente.pk]),
        ):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), AJUDA_DO_CPF)

    def test_ajuda_some_com_cpf_bloqueado_e_aviso_continua(self):
        cliente = criar_cliente()
        encerrar(registrar(cliente=cliente))
        resposta = self.client.get(reverse("clientes:editar", args=[cliente.pk]))
        self.assertNotContains(resposta, AJUDA_DO_CPF)
        self.assertContains(
            resposta,
            "O CPF não pode ser alterado porque o cliente já possui aluguel registrado.",
        )
        self.assertRegex(
            resposta.content.decode(), r'<input[^>]*name="cpf"[^>]*disabled'
        )
