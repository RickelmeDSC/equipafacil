"""Views de equipamentos (P02, P03, P04; RF001–RF004, D10, D11).

Todas exigem login (LoginRequiredMiddleware). GET só lê; toda alteração é POST
com CSRF e segue POST/redirect/GET. Os indicadores enviados ao template são só
para exibição: cada POST revalida as regras no serviço, dentro da transação.
Rotas, nomes de template e variáveis seguem o contrato proposto (PR #2), ainda
sem aceite.
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from config import mensagens
from config.formularios import aplicar_erros
from equipamentos import services
from equipamentos.forms import EquipamentoForm
from equipamentos.models import Equipamento


@require_safe
def lista(request: HttpRequest) -> HttpResponse:
    """P02: lista e pesquisa por código ou nome, com disponibilidade calculada."""
    query = request.GET.get("q", "").strip()
    equipamentos = list(
        Equipamento.objects.com_situacao().pesquisar(query).order_by("nome", "codigo")
    )
    for equipamento in equipamentos:
        equipamento.acoes = services.avaliar_acoes(equipamento, verificar_dados=False)
    return render(
        request,
        "equipamentos/lista.html",
        {
            "object_list": equipamentos,
            "query": query,
            "empty_message": mensagens.NENHUM_REGISTRO,
        },
    )


@require_http_methods(["GET", "POST"])
def criar(request: HttpRequest) -> HttpResponse:
    """P03 (cadastro): o equipamento nasce ativo."""
    form = EquipamentoForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            services.cadastrar_equipamento(form.cleaned_data)
        except ValidationError as erro:
            aplicar_erros(form, erro)
        else:
            messages.success(request, mensagens.EQUIPAMENTO_CADASTRADO)
            return redirect("equipamentos:lista")
    return render(request, "equipamentos/formulario.html", {"form": form})


@require_http_methods(["GET", "POST"])
def editar(request: HttpRequest, pk: int) -> HttpResponse:
    """P03 (edição): código somente leitura depois do primeiro aluguel."""
    equipamento = get_object_or_404(Equipamento, pk=pk)
    codigo_editavel = equipamento.codigo_editavel
    form = EquipamentoForm(
        request.POST if request.method == "POST" else None,
        instance=equipamento,
        codigo_editavel=codigo_editavel,
    )
    if request.method == "POST" and form.is_valid():
        try:
            services.editar_equipamento(pk, form.cleaned_data)
        except Equipamento.DoesNotExist:
            raise Http404 from None
        except ValidationError as erro:
            aplicar_erros(form, erro)
        else:
            messages.success(request, mensagens.EQUIPAMENTO_ATUALIZADO)
            return redirect("equipamentos:lista")
    return render(
        request,
        "equipamentos/formulario.html",
        {"form": form, "object": equipamento, "codigo_editavel": codigo_editavel},
    )


@require_safe
def acoes(request: HttpRequest, pk: int) -> HttpResponse:
    """P04: ações permitidas e motivos de bloqueio (D10)."""
    equipamento = get_object_or_404(Equipamento.objects.com_situacao(), pk=pk)
    avaliacao = services.avaliar_acoes(equipamento)
    return render(
        request,
        "equipamentos/acoes.html",
        {
            "object": equipamento,
            "acoes": avaliacao,
            "tem_historico": avaliacao.tem_historico,
            "tem_aluguel_ativo": avaliacao.tem_aluguel_ativo,
            "pode_excluir": avaliacao.pode_excluir,
            "pode_inativar": avaliacao.pode_inativar,
            "pode_reativar": avaliacao.pode_reativar,
        },
    )


def _executar(
    request: HttpRequest, pk: int, operacao, mensagem_de_sucesso: str
) -> HttpResponse:
    """Executa a operação; recusa volta para P04 com a mensagem, sucesso vai para P02."""
    get_object_or_404(Equipamento, pk=pk)
    try:
        operacao(pk)
    except Equipamento.DoesNotExist:
        raise Http404 from None
    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)
        return redirect("equipamentos:acoes", pk=pk)
    messages.success(request, mensagem_de_sucesso)
    return redirect("equipamentos:lista")


@require_POST
def excluir(request: HttpRequest, pk: int) -> HttpResponse:
    """Exclusão física com confirmação explícita (campo ``confirmacao``)."""
    get_object_or_404(Equipamento, pk=pk)
    if request.POST.get("confirmacao") != "sim":
        messages.error(request, mensagens.CONFIRMACAO_DE_EXCLUSAO_AUSENTE)
        return redirect("equipamentos:acoes", pk=pk)
    return _executar(
        request, pk, services.excluir_equipamento, mensagens.EQUIPAMENTO_EXCLUIDO
    )


@require_POST
def inativar(request: HttpRequest, pk: int) -> HttpResponse:
    return _executar(
        request, pk, services.inativar_equipamento, mensagens.EQUIPAMENTO_INATIVADO
    )


@require_POST
def reativar(request: HttpRequest, pk: int) -> HttpResponse:
    return _executar(
        request, pk, services.reativar_equipamento, mensagens.EQUIPAMENTO_REATIVADO
    )
