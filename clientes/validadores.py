"""Normalização, validação e formatação de CPF e telefone (RF005, RN002, I5, D12)."""

import re

from django.core.exceptions import ValidationError

from config import mensagens

_PONTUACAO_DO_CPF = str.maketrans("", "", ".-")
# Interpretação técnica de D12 para a "máscara usual": parênteses, espaço e hífen.
_MASCARA_DO_TELEFONE = str.maketrans("", "", "() -")
_ONZE_DIGITOS = re.compile(r"[0-9]{11}")
_DEZ_OU_ONZE_DIGITOS = re.compile(r"[0-9]{10,11}")


def normalizar_cpf(valor: str) -> str:
    """Remove apenas pontos e hífen; qualquer outro caractere fica para ser recusado."""
    return valor.translate(_PONTUACAO_DO_CPF) if isinstance(valor, str) else valor


def _digitos_verificadores_validos(cpf: str) -> bool:
    for tamanho in (9, 10):
        soma = sum(
            int(digito) * (tamanho + 1 - posicao)
            for posicao, digito in enumerate(cpf[:tamanho])
        )
        if (soma * 10) % 11 % 10 != int(cpf[tamanho]):
            return False
    return True


def validar_cpf(valor: str) -> None:
    """Exige 11 dígitos, dígitos verificadores válidos e recusa os 11 dígitos iguais."""
    if (
        not isinstance(valor, str)
        or not _ONZE_DIGITOS.fullmatch(valor)
        or len(set(valor)) == 1
        or not _digitos_verificadores_validos(valor)
    ):
        raise ValidationError(mensagens.CPF_INVALIDO, code="cpf_invalido")


def formatar_cpf(cpf: str) -> str:
    if not _ONZE_DIGITOS.fullmatch(cpf or ""):
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def mascarar_cpf(cpf: str) -> str:
    """Só os seis dígitos centrais, para distinguir homônimos sem expor o CPF inteiro."""
    if not _ONZE_DIGITOS.fullmatch(cpf or ""):
        return "***.***.***-**"
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**"


def normalizar_telefone(valor: str) -> str:
    """Remove parênteses, espaços e hífen; outros caracteres (inclusive "+") ficam para ser recusados."""
    return valor.translate(_MASCARA_DO_TELEFONE) if isinstance(valor, str) else valor


def validar_telefone(valor: str) -> None:
    """Telefone com DDD: 10 ou 11 dígitos depois de remover a máscara."""
    if not _DEZ_OU_ONZE_DIGITOS.fullmatch(valor or ""):
        raise ValidationError(mensagens.TELEFONE_INVALIDO, code="telefone_invalido")


def formatar_telefone(telefone: str) -> str:
    if not _DEZ_OU_ONZE_DIGITOS.fullmatch(telefone or ""):
        return telefone
    ddd, numero = telefone[:2], telefone[2:]
    return f"({ddd}) {numero[:-4]}-{numero[-4:]}"
