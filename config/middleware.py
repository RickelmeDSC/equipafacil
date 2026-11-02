"""Middleware do projeto EquipaFácil."""

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.utils.cache import add_never_cache_headers

CAMINHO_HEALTH_CHECK = "/healthz/"


class HealthCheckMiddleware:
    """Responde ``GET`` e ``HEAD`` em ``/healthz/`` para o health check do Render.

    Fica antes do SessionMiddleware: a resposta sai sem ler sessão, sem
    autenticar e sem consultar o PostgreSQL (não acorda o Neon), mesmo que a
    requisição traga cookie de sessão. O corpo é só ``ok``, sem configuração.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path_info != CAMINHO_HEALTH_CHECK:
            return self.get_response(request)
        if request.method not in ("GET", "HEAD"):
            return HttpResponseNotAllowed(["GET", "HEAD"])
        resposta = HttpResponse("ok\n", content_type="text/plain; charset=utf-8")
        add_never_cache_headers(resposta)
        return resposta
