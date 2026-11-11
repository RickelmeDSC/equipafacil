"""Views de aluguéis: registro (P07), histórico (P08) e devolução (P09).

RF006–RF008, RF010, RN001, RN004, I1, I2, D13. Todas exigem login
(LoginRequiredMiddleware). GET só lê; gravação é POST com CSRF e segue
POST/redirect/GET. Sem cancelamento e sem edição de aluguel. Rotas, nomes de
template e variáveis seguem o contrato proposto (PR #2), ainda sem aceite;
``situacao_selecionada`` e ``opcoes_situacao`` em P08 são acréscimos do RF010.

"Data atual" é sempre ``timezone.localdate()`` (America/Recife); os serviços
usam a própria data atual ao gravar.
"""

from django.contrib import messages
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
from alugueis.models import Aluguel, Situacao
from config import mensagens
from config.formularios import aplicar_erros

# Botões de P07 (D13), campo ``acao``: a prévia não grava; só ``registrar``
# grava. Sem ação, com ação desconhecida ou com mais de uma, nada é gravado:
# não há cancelamento na v1, então o registro nunca é o comportamento padrão.
ACAO_PREVIA = "previa"
ACAO_REGISTRAR = "registrar"
ACOES = (ACAO_PREVIA, ACAO_REGISTRAR)

# Filtro de P08 (RF010), GET ``situacao``: "Todas" é o valor vazio, sem filtro.
OPCOES_SITUACAO = (("", "Todas"), *Situacao.choices)


def _acao_pedida(request: HttpRequest) -> str | None:
    """A ação do POST, só se houver exatamente um valor conhecido."""
    valores = request.POST.getlist("acao")
    return valores[0] if len(valores) == 1 and valores[0] in ACOES else None


def _situacao_pedida(request: HttpRequest) -> str:
    """Situação do filtro (RF010); vazia, "Todas" ou desconhecida vale "Todas"."""
    valor = request.GET.get("situacao", "").strip()
    return valor if valor in Situacao.values else ""


@require_safe
def historico(request: HttpRequest) -> HttpResponse:
    """P08: aluguéis do mais recente para o mais antigo, com o filtro do RF010.

    Inclui equipamentos inativos. Situação e ``pode_devolver`` são calculados
    com a data atual; cliente e equipamento vêm na mesma consulta. O filtro usa
    a data atual em America/Recife e mantém a ordem do histórico sem filtro.
    """
    situacao = _situacao_pedida(request)
    alugueis = Aluguel.objects.select_related("cliente", "equipamento")
    if situacao:
        alugueis = alugueis.na_situacao(situacao, timezone.localdate())
    return render(
        request,
        "alugueis/historico.html",
        {
            "object_list": alugueis.order_by("-data_retirada", "-pk"),
            "situacao_selecionada": situacao,
            "opcoes_situacao": OPCOES_SITUACAO,
            "empty_message": mensagens.NENHUM_REGISTRO,
        },
    )


@require_http_methods(["GET", "POST"])
def criar(request: HttpRequest) -> HttpResponse:
    """P07 (D13): formulário único; a prévia não grava e o registro recalcula tudo.

    Só ``acao=registrar`` grava. Erros devolvem o formulário com os dados
    informados (HTTP 200).
    """
    hoje = timezone.localdate()
    form = AluguelForm(request.POST if request.method == "POST" else None, hoje=hoje)
    resumo = None
    if request.method == "POST":
        acao = _acao_pedida(request)
        valido = form.is_valid()
        if acao is None:
            form.add_error(None, mensagens.ACAO_DO_ALUGUEL_INVALIDA)
        elif valido:
            dados = {
                "cliente_id": form.cleaned_data["cliente"].pk,
                "equipamento_id": form.cleaned_data["equipamento"].pk,
                "data_retirada": form.cleaned_data["data_retirada"],
                "data_devolucao_prevista": form.cleaned_data["data_devolucao_prevista"],
            }
            try:
                if acao == ACAO_PREVIA:
                    resumo = services.simular_aluguel(**dados)
                else:
                    services.registrar_aluguel(**dados)
                    messages.success(request, mensagens.ALUGUEL_REGISTRADO)
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
            messages.success(request, mensagens.DEVOLUCAO_REGISTRADA)
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
