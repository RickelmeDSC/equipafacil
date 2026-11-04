"""Views de clientes (P05, P06; RF005, D12, D14).

Todas exigem login (LoginRequiredMiddleware). GET só lê; a gravação é POST com
CSRF e segue POST/redirect/GET. Sem pesquisa, sem página de detalhe e sem
exclusão (D14, RN003). Rotas, nomes de template e variáveis seguem o contrato
proposto (PR #2), ainda sem aceite.

CPF, telefone e e-mail são marcados como sensíveis: relatórios de erro do
Django mascaram esses campos do POST.
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_safe

from clientes import services
from clientes.forms import ClienteForm
from clientes.models import Cliente
from config import mensagens
from config.formularios import aplicar_erros

CAMPOS_SENSIVEIS = ("cpf", "telefone", "email")


@require_safe
def lista(request: HttpRequest) -> HttpResponse:
    """P05: todos os clientes, por nome e ordem de cadastro (D14: sem pesquisa)."""
    return render(
        request,
        "clientes/lista.html",
        {
            "object_list": Cliente.objects.order_by("nome_completo", "pk"),
            "empty_message": mensagens.NENHUM_REGISTRO,
        },
    )


@sensitive_post_parameters(*CAMPOS_SENSIVEIS)
@require_http_methods(["GET", "POST"])
def criar(request: HttpRequest) -> HttpResponse:
    """P06 (cadastro)."""
    form = ClienteForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            services.cadastrar_cliente(form.cleaned_data)
        except ValidationError as erro:
            aplicar_erros(form, erro)
        else:
            messages.success(request, mensagens.CLIENTE_CADASTRADO)
            return redirect("clientes:lista")
    return render(request, "clientes/formulario.html", {"form": form})


@sensitive_post_parameters(*CAMPOS_SENSIVEIS)
@require_http_methods(["GET", "POST"])
def editar(request: HttpRequest, pk: int) -> HttpResponse:
    """P06 (edição): CPF somente leitura depois do primeiro aluguel."""
    cliente = get_object_or_404(Cliente, pk=pk)
    cpf_editavel = cliente.cpf_editavel
    form = ClienteForm(
        request.POST if request.method == "POST" else None,
        instance=cliente,
        cpf_editavel=cpf_editavel,
    )
    if request.method == "POST" and form.is_valid():
        try:
            services.editar_cliente(pk, form.cleaned_data)
        except Cliente.DoesNotExist:
            raise Http404 from None
        except ValidationError as erro:
            aplicar_erros(form, erro)
        else:
            messages.success(request, mensagens.CLIENTE_ATUALIZADO)
            return redirect("clientes:lista")
    return render(
        request,
        "clientes/formulario.html",
        {"form": form, "object": cliente, "cpf_editavel": cpf_editavel},
    )
