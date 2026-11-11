"""Modelo de clientes (RF005, RF009, RN002, RN003, I5, D12, D14, D16).

Clientes não são excluídos nem inativados, não têm página de detalhe (D14) e
não têm endereço (fora do escopo aprovado). A pesquisa por nome ou CPF é a do
RF009 (D16, que revisa a D14; EQF-5, comentário 10078).
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from clientes.validadores import (
    digitos_para_pesquisa,
    formatar_cpf,
    formatar_telefone,
    mascarar_cpf,
    normalizar_cpf,
    normalizar_telefone,
    validar_cpf,
    validar_telefone,
)
from config import mensagens
from config.validacao import ModeloValidado

_ERROS_OBRIGATORIO = {
    "blank": mensagens.CAMPO_OBRIGATORIO,
    "null": mensagens.CAMPO_OBRIGATORIO,
}
_CPFS_REPETIDOS = [digito * 11 for digito in "0123456789"]


class ClienteQuerySet(models.QuerySet):
    def pesquisar(self, termo: str | None):
        """RF009 (D16): parte do nome ou do CPF; sem termo, todos os clientes.

        O nome é comparado sem diferenciar maiúsculas e sem ignorar acentos. O CPF
        é comparado pelos dígitos armazenados, parcial ou completo, com ou sem
        pontos e hífen. Só leitura; a ordem fica com quem chama.
        """
        termo = (termo or "").strip()
        if not termo:
            return self
        condicao = Q(nome_completo__icontains=termo)
        digitos = digitos_para_pesquisa(termo)
        if digitos:
            condicao |= Q(cpf__contains=digitos)
        return self.filter(condicao)


class Cliente(ModeloValidado):
    nome_completo = models.CharField(
        "nome completo", max_length=150, error_messages=_ERROS_OBRIGATORIO
    )
    # I5: persistido só com os 11 dígitos; exibido formatado.
    cpf = models.CharField(
        "CPF",
        max_length=11,
        validators=[validar_cpf],
        error_messages={**_ERROS_OBRIGATORIO, "max_length": mensagens.CPF_INVALIDO},
    )
    telefone = models.CharField(
        "telefone",
        max_length=11,
        blank=True,
        validators=[validar_telefone],
        error_messages={"max_length": mensagens.TELEFONE_INVALIDO},
    )
    email = models.EmailField(
        "e-mail", blank=True, error_messages={"invalid": mensagens.EMAIL_INVALIDO}
    )

    objects = ClienteQuerySet.as_manager()

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        constraints = [
            models.UniqueConstraint(
                fields=["cpf"],
                name="cliente_cpf_unico",
                violation_error_message=mensagens.CPF_DUPLICADO,
            ),
            models.CheckConstraint(
                condition=Q(cpf__regex=r"^[0-9]{11}$"), name="cliente_cpf_onze_digitos"
            ),
            models.CheckConstraint(
                condition=~Q(cpf__in=_CPFS_REPETIDOS), name="cliente_cpf_nao_repetido"
            ),
            models.CheckConstraint(
                condition=Q(telefone="") | Q(telefone__regex=r"^[0-9]{10,11}$"),
                name="cliente_telefone_digitos",
            ),
            models.CheckConstraint(
                condition=~Q(nome_completo=""), name="cliente_nome_preenchido"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nome_completo} ({self.cpf_formatado})"

    def normalizar(self) -> None:
        if isinstance(self.nome_completo, str):
            self.nome_completo = self.nome_completo.strip()
        self.cpf = normalizar_cpf(self.cpf)
        self.telefone = normalizar_telefone(self.telefone)

    def clean(self) -> None:
        erros = {}
        if self._cpf_valido() and self._cpf_em_uso():
            erros["cpf"] = mensagens.CPF_DUPLICADO
        if self._cpf_alterado_apos_aluguel():
            erros["cpf"] = mensagens.CPF_BLOQUEADO
        if erros:
            raise ValidationError(erros)

    def _cpf_valido(self) -> bool:
        try:
            validar_cpf(self.cpf)
        except ValidationError:
            return False
        return True

    def _cpf_em_uso(self) -> bool:
        iguais = Cliente.objects.filter(cpf=self.cpf)
        if self.pk:
            iguais = iguais.exclude(pk=self.pk)
        return iguais.exists()

    def _cpf_alterado_apos_aluguel(self) -> bool:
        if not self.pk:
            return False
        original = (
            Cliente.objects.filter(pk=self.pk).values_list("cpf", flat=True).first()
        )
        return original is not None and original != self.cpf and self.tem_aluguel

    @property
    def tem_aluguel(self) -> bool:
        return bool(self.pk) and self.alugueis.exists()

    @property
    def cpf_editavel(self) -> bool:
        return not self.tem_aluguel

    @property
    def cpf_formatado(self) -> str:
        return formatar_cpf(self.cpf)

    @property
    def cpf_mascarado(self) -> str:
        """Para seleções e listas que não precisam do CPF completo (P07)."""
        return mascarar_cpf(self.cpf)

    @property
    def telefone_formatado(self) -> str:
        return formatar_telefone(self.telefone)
