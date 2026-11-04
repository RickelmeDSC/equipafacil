"""Formulário de equipamento (P03; RF001, RF003, RN002, D11).

Só os campos editáveis entram no formulário: ``ativo`` e qualquer outro campo
enviado por POST são ignorados. A gravação é feita pelos serviços, que
revalidam tudo dentro da transação.
"""

from django import forms

from config import mensagens
from config.formularios import FormularioBootstrap
from equipamentos.models import Equipamento
from equipamentos.services import CAMPOS_EDITAVEIS

_OBRIGATORIO = {"required": mensagens.CAMPO_OBRIGATORIO}


class EquipamentoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = list(CAMPOS_EDITAVEIS)
        # Aceita a vírgula decimal da localização pt-br (ex.: 35,50).
        localized_fields = ["valor_diaria"]
        error_messages = {
            "codigo": _OBRIGATORIO,
            "nome": _OBRIGATORIO,
            "categoria": {
                **_OBRIGATORIO,
                "invalid_choice": mensagens.CATEGORIA_INVALIDA,
            },
            "valor_diaria": {
                **_OBRIGATORIO,
                "invalid": mensagens.DIARIA_INVALIDA,
                "min_value": mensagens.DIARIA_INVALIDA,
                "max_digits": mensagens.DIARIA_INVALIDA,
                "max_decimal_places": mensagens.DIARIA_INVALIDA,
                "max_whole_digits": mensagens.DIARIA_INVALIDA,
            },
        }

    def __init__(self, *args, codigo_editavel: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.codigo_editavel = codigo_editavel
        if not codigo_editavel:
            # Somente leitura: o Django usa o valor original e ignora o enviado,
            # inclusive mudança só de maiúsculas (D11).
            self.fields["codigo"].disabled = True
