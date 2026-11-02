"""Formulário de aluguel (P07) (RF006, RN001, RN004, I1, D13).

Só identificadores e datas entram: diária, diárias e valores nunca vêm do
navegador. As opções mostradas são só orientação; os serviços revalidam tudo
dentro da transação.
"""

from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.formats import number_format

from alugueis.services import validar_datas_do_aluguel
from clientes.models import Cliente
from config import mensagens
from equipamentos.models import Equipamento

_FORMATO_ISO = "%Y-%m-%d"  # valor de <input type="date">


def _campo_de_data(label: str) -> forms.DateField:
    return forms.DateField(
        label=label,
        widget=forms.DateInput(format=_FORMATO_ISO, attrs={"type": "date"}),
        error_messages={"required": mensagens.CAMPO_OBRIGATORIO},
    )


def formatar_reais(valor) -> str:
    """Ex.: R$ 1.500,00 (localização pt-br)."""
    return f"R$ {number_format(valor, 2, use_l10n=True, force_grouping=True)}"


class EscolhaDeCliente(forms.ModelChoiceField):
    def label_from_instance(self, cliente: Cliente) -> str:
        # Nome e CPF mascarado: distingue homônimos sem expor o CPF inteiro.
        return f"{cliente.nome_completo} — CPF {cliente.cpf_mascarado}"


class EscolhaDeEquipamento(forms.ModelChoiceField):
    def label_from_instance(self, equipamento: Equipamento) -> str:
        diaria = formatar_reais(equipamento.valor_diaria)
        return f"{equipamento.codigo} — {equipamento.nome} ({diaria}/dia)"


def clientes_para_escolha():
    return Cliente.objects.order_by("nome_completo", "pk")


def equipamentos_para_escolha():
    """Só os disponíveis: ativos e sem aluguel aberto (RN001, I1)."""
    return Equipamento.objects.disponiveis().order_by("nome", "codigo")


class AluguelForm(forms.Form):
    cliente = EscolhaDeCliente(
        queryset=Cliente.objects.none(),
        label="Cliente",
        error_messages={
            "required": mensagens.CAMPO_OBRIGATORIO,
            "invalid_choice": mensagens.CLIENTE_INEXISTENTE,
        },
    )
    equipamento = EscolhaDeEquipamento(
        queryset=Equipamento.objects.none(),
        label="Equipamento",
        error_messages={
            "required": mensagens.CAMPO_OBRIGATORIO,
            "invalid_choice": mensagens.EQUIPAMENTO_INDISPONIVEL,
        },
    )
    data_retirada = _campo_de_data("Data de retirada")
    data_devolucao_prevista = _campo_de_data("Devolução prevista")

    def __init__(self, *args, hoje: date, **kwargs):
        super().__init__(*args, **kwargs)
        self.hoje = hoje
        self.fields["cliente"].queryset = clientes_para_escolha()
        self.fields["equipamento"].queryset = equipamentos_para_escolha()
        minimo = hoje.strftime(_FORMATO_ISO)
        self.fields["data_retirada"].widget.attrs["min"] = minimo
        self.fields["data_devolucao_prevista"].widget.attrs["min"] = minimo
        if not self.is_bound:
            self.initial.setdefault("data_retirada", hoje)

    def clean(self):
        dados = super().clean()
        retirada = dados.get("data_retirada")
        prevista = dados.get("data_devolucao_prevista")
        if retirada and prevista:
            try:
                validar_datas_do_aluguel(retirada, prevista, self.hoje)
            except ValidationError as erro:
                for campo, mensagens_do_campo in erro.message_dict.items():
                    self.add_error(campo, mensagens_do_campo)
        return dados
