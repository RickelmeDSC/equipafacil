"""Rotas de aluguéis.

PROVISÓRIO: caminhos e nomes seguem o contrato técnico proposto no PR #2
(seção 6), ainda sem aceite de Raphael. Sem cancelamento e sem edição de
aluguel (I2).
"""

from django.urls import path

from alugueis import views

app_name = "alugueis"

urlpatterns = [
    path("", views.historico, name="historico"),
]
