"""Formulário de cliente (P06; RF005, RN002, I5, D12).

Só os campos editáveis entram no formulário: ``id`` e qualquer outro campo
enviado por POST são ignorados. A normalização e a validação de CPF e telefone
são as do modelo (``clientes/validadores.py``); o formulário só limita o
tamanho da entrada. A gravação é feita pelos serviços, que revalidam tudo
dentro da transação.
"""

from django import forms

from clientes.models import Cliente
from clientes.services import CAMPOS_EDITAVEIS
from config import mensagens

# Limite de tamanho da entrada, antes da normalização (máscaras "000.000.000-00" e
# "(81) 99999-8888"). A regra de formato continua sendo a do modelo (D12).
_TAMANHO_MAXIMO_DA_ENTRADA = 20


class ClienteForm(forms.ModelForm):
    # strip=False: D12 remove só pontos e hífen; espaços são recusados pelo modelo.
    cpf = forms.CharField(
        label="CPF",
        max_length=_TAMANHO_MAXIMO_DA_ENTRADA,
        strip=False,
        error_messages={
            "required": mensagens.CAMPO_OBRIGATORIO,
            "max_length": mensagens.CPF_INVALIDO,
        },
    )
    telefone = forms.CharField(
        label="Telefone",
        required=False,
        max_length=_TAMANHO_MAXIMO_DA_ENTRADA,
        error_messages={"max_length": mensagens.TELEFONE_INVALIDO},
    )

    class Meta:
        model = Cliente
        fields = list(CAMPOS_EDITAVEIS)
        error_messages = {
            "nome_completo": {"required": mensagens.CAMPO_OBRIGATORIO},
            "email": {"invalid": mensagens.EMAIL_INVALIDO},
        }

    def __init__(self, *args, cpf_editavel: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpf_editavel = cpf_editavel
        if self.instance.pk:
            # Na edição, CPF e telefone aparecem formatados (contrato, 7.2).
            self.initial["cpf"] = self.instance.cpf_formatado
            self.initial["telefone"] = self.instance.telefone_formatado
        if not cpf_editavel:
            # Somente leitura: o Django usa o valor gravado e ignora o enviado.
            # O serviço também recusa a troca, sob bloqueio da linha.
            self.fields["cpf"].disabled = True
