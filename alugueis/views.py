"""Views de aluguéis: registro (P07), histórico (P08) e devolução (P09).

RF006–RF008, RN001, RN004, I1, I2, D13. Todas exigem login
(LoginRequiredMiddleware). GET só lê; gravação é POST com CSRF e segue
POST/redirect/GET. Sem cancelamento e sem edição de aluguel. Rotas, nomes de
template e variáveis seguem o contrato proposto (PR #2), ainda sem aceite.

"Data atual" é sempre ``timezone.localdate()`` (America/Recife); os serviços
usam a própria data atual ao gravar.
"""

from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from alugueis import services
from alugueis.forms import (
    AluguelForm,
    DevolucaoForm,
    clientes_para_escolha,
    equipamentos_para_escolha,
)
from alugueis.models import Aluguel
from config import mensagens
from config.formularios import aplicar_erros

# Valor do botão de prévia (D13). Sem ele, o POST registra o aluguel.
ACAO_PREVIA = "previa"


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


@require_http_methods(["GET", "POST"])
def criar(request: HttpRequest) -> HttpResponse:
    """P07 (D13): formulário único; a prévia não grava e o registro recalcula tudo."""
    hoje = timezone.localdate()
    form = AluguelForm(request.POST if request.method == "POST" else None, hoje=hoje)
    resumo = None
    if request.method == "POST" and form.is_valid():
        dados = {
            "cliente_id": form.cleaned_data["cliente"].pk,
            "equipamento_id": form.cleaned_data["equipamento"].pk,
            "data_retirada": form.cleaned_data["data_retirada"],
            "data_devolucao_prevista": form.cleaned_data["data_devolucao_prevista"],
        }
        try:
            if request.POST.get("acao") == ACAO_PREVIA:
                resumo = services.simular_aluguel(**dados)
            else:
                services.registrar_aluguel(**dados)
                return redirect("alugueis:historico")
        except ValidationError as erro:
            aplicar_erros(form, erro)

    equipamentos = list(equipamentos_para_escolha())
    return render(
        request,
        "alugueis/formulario.html",
        {
            "form": form,
            "resumo": resumo,
            "data_atual": hoje,
            "data_minima": hoje,
            # Prévia em JavaScript (proposta do contrato): via json_script, sem API.
            "diarias_equipamentos": {
                str(equipamento.pk): str(equipamento.valor_diaria)
                for equipamento in equipamentos
            },
            "sem_equipamentos_disponiveis": not equipamentos,
            "sem_clientes": not clientes_para_escolha().exists(),
        },
    )


@require_http_methods(["GET", "POST"])
def devolver(request: HttpRequest, pk: int) -> HttpResponse:
    """P09: devolução única, com data entre a retirada e a data atual."""
    aluguel = get_object_or_404(
        Aluguel.objects.select_related("cliente", "equipamento"), pk=pk
    )
    hoje = timezone.localdate()
    form = DevolucaoForm(
        request.POST if request.method == "POST" else None,
        data_minima=aluguel.data_retirada,
        data_maxima=hoje,
    )
    if request.method == "POST" and form.is_valid():
        try:
            services.registrar_devolucao(
                aluguel_id=pk,
                data_devolucao_real=form.cleaned_data["data_devolucao_real"],
            )
        except Aluguel.DoesNotExist:
            raise Http404 from None
        except ValidationError as erro:
            aplicar_erros(form, erro)
            aluguel.refresh_from_db()
        else:
            return redirect("alugueis:historico")
    return render(
        request,
        "alugueis/devolver.html",
        {
            "object": aluguel,
            "form": form,
            "pode_devolver": aluguel.pode_devolver(hoje),
            "data_atual": hoje,
            "data_minima": aluguel.data_retirada,
            "data_maxima": hoje,
        },
    )
