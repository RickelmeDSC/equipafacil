"""Modelo de equipamentos (RF001–RF004, RN001–RN003, D10, D11).

A disponibilidade não é persistida: é derivada de ``ativo`` e da existência de
aluguel aberto. Detalhes e invariantes em ``docs/modelagem-implementada.md``.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef, Q, Value
from django.db.models.functions import Lower, Trim

from config import mensagens
from config.validacao import ModeloValidado


class Categoria(models.TextChoices):
    """Categorias fixas aprovadas (D8)."""

    FERRAMENTAS = "ferramentas", "Ferramentas"
    AUDIOVISUAIS = "audiovisuais", "Equipamentos Audiovisuais"
    INFORMATICA = "informatica", "Informática"
    CONSTRUCAO_CIVIL = "construcao_civil", "Construção Civil"
    OUTROS = "outros", "Outros"


_ERROS_OBRIGATORIO = {
    "blank": mensagens.CAMPO_OBRIGATORIO,
    "null": mensagens.CAMPO_OBRIGATORIO,
}
_ERROS_DIARIA = {
    **_ERROS_OBRIGATORIO,
    "invalid": mensagens.DIARIA_INVALIDA,
    "min_value": mensagens.DIARIA_INVALIDA,
    "max_digits": mensagens.DIARIA_INVALIDA,
    "max_decimal_places": mensagens.DIARIA_INVALIDA,
    "max_whole_digits": mensagens.DIARIA_INVALIDA,
}


class EquipamentoQuerySet(models.QuerySet):
    def com_situacao(self):
        """Anota ``possui_historico`` e ``possui_aluguel_aberto`` na mesma consulta.

        As propriedades ``tem_historico``, ``tem_aluguel_aberto`` e ``disponivel``
        usam essas anotações quando presentes, evitando uma consulta por linha.
        """
        from alugueis.models import Aluguel

        alugueis = Aluguel.objects.filter(equipamento=OuterRef("pk"))
        return self.annotate(
            possui_historico=Exists(alugueis),
            possui_aluguel_aberto=Exists(
                alugueis.filter(data_devolucao_real__isnull=True)
            ),
        )

    def disponiveis(self):
        """Equipamentos ativos e sem aluguel aberto, inclusive de retirada futura (RN001 c, I1)."""
        return self.com_situacao().filter(ativo=True, possui_aluguel_aberto=False)

    def pesquisar(self, termo: str | None):
        """Pesquisa só por código ou nome (RF002), sem diferenciar maiúsculas."""
        termo = (termo or "").strip()
        if not termo:
            return self
        return self.filter(Q(codigo__icontains=termo) | Q(nome__icontains=termo))


class Equipamento(ModeloValidado):
    codigo = models.CharField(
        "código", max_length=30, error_messages=_ERROS_OBRIGATORIO
    )
    nome = models.CharField("nome", max_length=120, error_messages=_ERROS_OBRIGATORIO)
    categoria = models.CharField(
        "categoria",
        max_length=30,
        choices=Categoria.choices,
        error_messages={
            **_ERROS_OBRIGATORIO,
            "invalid_choice": mensagens.CATEGORIA_INVALIDA,
        },
    )
    valor_diaria = models.DecimalField(
        "valor da diária",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        error_messages=_ERROS_DIARIA,
    )
    descricao = models.TextField("descrição", blank=True)
    ativo = models.BooleanField("ativo", default=True)

    objects = EquipamentoQuerySet.as_manager()

    class Meta:
        verbose_name = "equipamento"
        verbose_name_plural = "equipamentos"
        constraints = [
            # D11: único sem diferenciar maiúsculas e minúsculas, no próprio banco.
            models.UniqueConstraint(
                Lower("codigo"),
                name="equipamento_codigo_unico_ci",
                violation_error_message=mensagens.CODIGO_DUPLICADO,
            ),
            # D11: o código é gravado sem espaços nas extremidades e não vazio.
            models.CheckConstraint(
                condition=Q(codigo=Trim("codigo")) & ~Q(codigo=""),
                name="equipamento_codigo_normalizado",
            ),
            models.CheckConstraint(
                condition=~Q(nome=""), name="equipamento_nome_preenchido"
            ),
            models.CheckConstraint(
                condition=Q(categoria__in=Categoria.values),
                name="equipamento_categoria_valida",
            ),
            models.CheckConstraint(
                condition=Q(valor_diaria__gt=0), name="equipamento_diaria_positiva"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"

    # Normalização e validação -------------------------------------------------

    def normalizar(self) -> None:
        if isinstance(self.codigo, str):
            self.codigo = self.codigo.strip()
        if isinstance(self.nome, str):
            self.nome = self.nome.strip()

    def clean(self) -> None:
        erros = {}
        if self.codigo and self._codigo_em_uso():
            erros["codigo"] = mensagens.CODIGO_DUPLICADO
        if self._codigo_alterado_apos_aluguel():
            erros["codigo"] = mensagens.CODIGO_BLOQUEADO
        if erros:
            raise ValidationError(erros)

    def _codigo_em_uso(self) -> bool:
        iguais = Equipamento.objects.annotate(codigo_ci=Lower("codigo")).filter(
            codigo_ci=Lower(Value(self.codigo))
        )
        if self.pk:
            iguais = iguais.exclude(pk=self.pk)
        return iguais.exists()

    def _codigo_alterado_apos_aluguel(self) -> bool:
        # Inclui mudança só de maiúsculas (D11). A corrida com o primeiro aluguel é
        # tratada pelo serviço, que bloqueia a linha do equipamento.
        if not self.pk:
            return False
        original = (
            Equipamento.objects.filter(pk=self.pk)
            .values_list("codigo", flat=True)
            .first()
        )
        return original is not None and original != self.codigo and self.tem_historico

    # Atributos derivados (nunca persistidos) ---------------------------------

    @property
    def tem_historico(self) -> bool:
        anotado = self.__dict__.get("possui_historico")
        if anotado is not None:
            return anotado
        return bool(self.pk) and self.alugueis.exists()

    @property
    def tem_aluguel_aberto(self) -> bool:
        anotado = self.__dict__.get("possui_aluguel_aberto")
        if anotado is not None:
            return anotado
        return (
            bool(self.pk)
            and self.alugueis.filter(data_devolucao_real__isnull=True).exists()
        )

    @property
    def disponivel(self) -> bool:
        """Ativo e sem aluguel aberto, inclusive de retirada futura (RN001 c, I1)."""
        return self.ativo and not self.tem_aluguel_aberto

    @property
    def codigo_editavel(self) -> bool:
        return not self.tem_historico
