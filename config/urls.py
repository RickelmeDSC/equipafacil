"""Rotas do projeto EquipaFácil.

PROVISÓRIO (DEV-02): os nomes ``login``, ``logout`` e ``inicio`` seguem a proposta
do contrato técnico DEV-01, ainda sem aceite. As rotas dos apps de domínio
seguem a mesma proposta: equipamentos no DEV-04, clientes no DEV-05 e aluguéis
no DEV-06 e DEV-07.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from config import views
from config.formularios import FormularioDeLogin

urlpatterns = [
    path("admin/", admin.site.urls),
    # LoginView já é pública (login_not_required); LogoutView aceita só POST.
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=FormularioDeLogin),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
    path("equipamentos/", include("equipamentos.urls")),
    path("clientes/", include("clientes.urls")),
    path("alugueis/", include("alugueis.urls")),
]
