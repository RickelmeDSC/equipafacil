"""Views do projeto (fora dos apps de domínio)."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def inicio(request: HttpRequest) -> HttpResponse:
    """Página inicial PROVISÓRIA, usada só para validar a autenticação.

    Protegida pelo LoginRequiredMiddleware. O conteúdo e o layout definitivos da
    página inicial (P01) são do frontend, conforme o contrato DEV-01.
    """
    return render(request, "inicio.html")
