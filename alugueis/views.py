"""Views de aluguéis: histórico (P08).

RF008, RN004. Exige login (LoginRequiredMiddleware); GET só lê. Rota, template e
variáveis seguem o contrato proposto (PR #2), ainda sem aceite.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from alugueis.models import Aluguel
from config import mensagens


@require_safe
def historico(request: HttpRequest) -> HttpResponse:
    """P08: todos os aluguéis, do mais recente para o mais antigo.

    Inclui equipamentos inativos. Situação e ``pode_devolver`` são calculados
    com a data atual; cliente e equipamento vêm na mesma consulta.
    """
    alugueis = Aluguel.objects.select_related("cliente", "equipamento").order_by(
        "-data_retirada", "-pk"
    )
    return render(
        request,
        "alugueis/historico.html",
        {"object_list": alugueis, "empty_message": mensagens.NENHUM_REGISTRO},
    )
