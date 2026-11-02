"""Rotas de equipamentos.

PROVISÓRIO: caminhos e nomes seguem o contrato técnico proposto no PR #2
(seção 6), ainda sem aceite de Raphael.
"""

from django.urls import path

from equipamentos import views

app_name = "equipamentos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.criar, name="criar"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/acoes/", views.acoes, name="acoes"),
    path("<int:pk>/excluir/", views.excluir, name="excluir"),
    path("<int:pk>/inativar/", views.inativar, name="inativar"),
    path("<int:pk>/reativar/", views.reativar, name="reativar"),
]
