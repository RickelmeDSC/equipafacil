"""Confirmação explícita do registro de aluguel em P07 (RF006, D13).

Sem cancelamento na v1, o registro nunca é o comportamento padrão: só
``acao=registrar`` grava; ``acao=previa`` calcula sem gravar; ação ausente,
desconhecida ou repetida não grava nada.
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from alugueis.models import Aluguel
from config import mensagens
from config.tests.fabricas import (
    criar_cliente,
    criar_equipamento,
    criar_funcionario,
    dias,
    hoje,
)
from equipamentos.models import Equipamento

URL = "/alugueis/novo/"


class ConfirmacaoExplicitaTests(TestCase):
    def setUp(self):
        self.client.force_login(criar_funcionario())
        self.cliente = criar_cliente()
        self.equipamento = criar_equipamento(valor_diaria=Decimal("50.00"))
        self.dados = {
            "cliente": str(self.cliente.pk),
            "equipamento": str(self.equipamento.pk),
            "data_retirada": hoje().isoformat(),
            "data_devolucao_prevista": dias(2).isoformat(),
        }

    def _nada_gravado(self):
        self.assertFalse(Aluguel.objects.exists())
        self.assertTrue(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)

    def _erros_gerais(self, resposta) -> list[str]:
        self.assertEqual(resposta.status_code, 200)
        return list(resposta.context["form"].non_field_errors())

    def test_1_previa_valida_nao_registra(self):
        resposta = self.client.post(URL, {**self.dados, "acao": "previa"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["resumo"].valor_previsto, Decimal("150.00"))
        self.assertEqual(self._erros_gerais(resposta), [])
        self._nada_gravado()

    def test_2_e_7_registro_com_acao_registrar(self):
        resposta = self.client.post(URL, {**self.dados, "acao": "registrar"})
        self.assertRedirects(
            resposta, reverse("alugueis:historico"), fetch_redirect_response=False
        )
        aluguel = Aluguel.objects.get()
        self.assertEqual(
            (aluguel.quantidade_diarias, aluguel.valor_contratado),
            (3, Decimal("150.00")),
        )

    def test_3_post_sem_acao_nao_registra(self):
        resposta = self.client.post(URL, self.dados)
        self.assertEqual(
            self._erros_gerais(resposta), [mensagens.ACAO_DO_ALUGUEL_INVALIDA]
        )
        self.assertIsNone(resposta.context["resumo"])
        self._nada_gravado()

    def test_4_acao_desconhecida_vazia_ou_repetida_nao_registra(self):
        casos = {
            "desconhecida": {"acao": "confirmar"},
            "maiúsculas": {"acao": "REGISTRAR"},
            "vazia": {"acao": ""},
            "com espaços": {"acao": " registrar "},
            "duas ações": {"acao": ["previa", "registrar"]},
            "registrar repetido": {"acao": ["registrar", "registrar"]},
        }
        for descricao, campos in casos.items():
            with self.subTest(caso=descricao):
                resposta = self.client.post(URL, {**self.dados, **campos})
                self.assertEqual(
                    self._erros_gerais(resposta), [mensagens.ACAO_DO_ALUGUEL_INVALIDA]
                )
                self.assertIsNone(resposta.context["resumo"])
        self._nada_gravado()

    def test_5_valores_financeiros_manipulados_sao_ignorados(self):
        self.client.post(
            URL,
            {
                **self.dados,
                "acao": "registrar",
                "valor_diaria_contratada": "0.01",
                "quantidade_diarias": "1",
                "valor_contratado": "0.01",
                "resumo": "0.01",
            },
        )
        aluguel = Aluguel.objects.get()
        self.assertEqual(
            (
                aluguel.valor_diaria_contratada,
                aluguel.quantidade_diarias,
                aluguel.valor_contratado,
            ),
            (Decimal("50.00"), 3, Decimal("150.00")),
        )

    def test_6_duplo_clique_registra_uma_unica_vez(self):
        primeira = self.client.post(URL, {**self.dados, "acao": "registrar"})
        segunda = self.client.post(URL, {**self.dados, "acao": "registrar"})
        self.assertEqual(primeira.status_code, 302)
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(
            segunda.context["form"].errors["equipamento"],
            [mensagens.EQUIPAMENTO_INDISPONIVEL],
        )
        self.assertEqual(Aluguel.objects.abertos().count(), 1)

    def test_8_erros_preservam_os_dados_informados(self):
        casos = {
            "sem ação": dict(self.dados),
            "data inválida": {
                **self.dados,
                "acao": "registrar",
                "data_retirada": dias(-1).isoformat(),
            },
        }
        for descricao, enviados in casos.items():
            with self.subTest(caso=descricao):
                resposta = self.client.post(URL, enviados)
                self.assertEqual(resposta.status_code, 200)
                form = resposta.context["form"]
                self.assertTrue(form.is_bound)
                for campo in (
                    "cliente",
                    "equipamento",
                    "data_retirada",
                    "data_devolucao_prevista",
                ):
                    self.assertEqual(form[campo].value(), enviados[campo])
                html = resposta.content.decode()
                self.assertIn(f'value="{enviados["data_retirada"]}"', html)
                self.assertIn(f'<option value="{self.equipamento.pk}" selected>', html)
        self._nada_gravado()

    def test_previa_seguida_de_registro(self):
        """Fluxo da página: prévia, depois o botão de registro."""
        previa = self.client.post(URL, {**self.dados, "acao": "previa"})
        self.assertContains(previa, 'name="acao" value="registrar"')
        self._nada_gravado()
        registro = self.client.post(URL, {**self.dados, "acao": "registrar"})
        self.assertEqual(registro.status_code, 302)
        self.assertEqual(Aluguel.objects.count(), 1)

    def test_pagina_inicial_oferece_so_a_previa(self):
        resposta = self.client.get(URL)
        self.assertContains(resposta, 'name="acao" value="previa"')
        self.assertNotContains(resposta, 'name="acao" value="registrar"')

    def test_retirada_futura_continua_permitida(self):
        self.client.post(
            URL,
            {
                **self.dados,
                "acao": "registrar",
                "data_retirada": dias(5).isoformat(),
                "data_devolucao_prevista": dias(5).isoformat(),
            },
        )
        aluguel = Aluguel.objects.get()
        self.assertEqual(aluguel.quantidade_diarias, 1)
        self.assertFalse(Equipamento.objects.get(pk=self.equipamento.pk).disponivel)
