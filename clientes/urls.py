"""Rotas de clientes.

PROVISÓRIO: caminhos e nomes seguem o contrato técnico proposto no PR #2
(seção 6), ainda sem aceite de Raphael. D14: sem pesquisa e sem detalhe.
"""

from django.urls import path

from clientes import views

app_name = "clientes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<int:pk>/editar/", views.editar, name="editar"),
]
