"""Apoio comum aos formulários e às views com formulário.

As classes do Bootstrap 5.3 ficam nos widgets (contrato proposto, seção 7), para
que os templates do frontend possam usar ``{{ form.campo }}`` sem editar
``forms.py``. O Django já marca campos com erro com ``aria-invalid="true"``; aqui
se acrescenta a classe visual ``is-invalid``.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

CLASSE_DE_ERRO = "is-invalid"


def _classe_base(widget: forms.Widget) -> str | None:
    if widget.is_hidden:
        return None
    if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
        return "form-check-input"
    if isinstance(widget, forms.Select):
        return "form-select"
    return "form-control"


def _acrescentar_classe(widget: forms.Widget, classe: str) -> None:
    atuais = widget.attrs.get("class", "").split()
    if classe not in atuais:
        widget.attrs["class"] = " ".join([*atuais, classe])


class FormularioBootstrap:
    """Mixin: classe base em cada widget e ``is-invalid`` nos campos com erro.

    ``add_error`` é o ponto por onde passam tanto a validação do Django quanto os
    erros devolvidos pelos serviços (``aplicar_erros``). Os campos do formulário
    são cópias por instância, então as classes não vazam entre formulários.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            classe = _classe_base(campo.widget)
            if classe:
                _acrescentar_classe(campo.widget, classe)

    def add_error(self, field, error):
        super().add_error(field, error)
        for nome in self._errors:
            if nome in self.fields:
                _acrescentar_classe(self.fields[nome].widget, CLASSE_DE_ERRO)


class FormularioDeLogin(FormularioBootstrap, AuthenticationForm):
    """P10: o ``AuthenticationForm`` do Django, só com as classes do Bootstrap."""


def aplicar_erros(form: forms.BaseForm, erro: ValidationError) -> None:
    """Leva ao formulário os erros devolvidos por um serviço.

    Erros de campos que não existem no formulário viram erros gerais.
    """
    if hasattr(erro, "error_dict"):
        for campo, lista in erro.message_dict.items():
            form.add_error(campo if campo in form.fields else None, lista)
    else:
        form.add_error(None, erro.messages)
