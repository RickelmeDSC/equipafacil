"""Apoio comum às views com formulário."""

from django import forms
from django.core.exceptions import ValidationError


def aplicar_erros(form: forms.BaseForm, erro: ValidationError) -> None:
    """Leva ao formulário os erros devolvidos por um serviço.

    Erros de campos que não existem no formulário viram erros gerais.
    """
    if hasattr(erro, "error_dict"):
        for campo, lista in erro.message_dict.items():
            form.add_error(campo if campo in form.fields else None, lista)
    else:
        form.add_error(None, erro.messages)
