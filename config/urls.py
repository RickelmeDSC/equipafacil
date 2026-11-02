"""Rotas do projeto EquipaFácil.

PROVISÓRIO (DEV-02): os nomes ``login``, ``logout`` e ``inicio`` seguem a proposta
do contrato técnico DEV-01, ainda sem aceite. As rotas dos apps de domínio entram
em DEV-04 a DEV-07, depois do aceite do contrato.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from config import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # LoginView já é pública (login_not_required); LogoutView aceita só POST.
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
]
