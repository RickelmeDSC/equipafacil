"""Modelo de aluguéis (RF006–RF008, RN001, RN003, RN004, I1, I2, D13).

Aluguel aberto = ``data_devolucao_real`` nula. Não há campo de status, multa,
cancelamento ou pagamento: a situação é calculada. O registro com bloqueio de
linha fica em ``alugueis.services.registrar_aluguel``.
"""

from datetime import date
from decimal import Decimal

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from clientes.models import Cliente
from config import mensagens
from config.validacao import ModeloValidado
from equipamentos.models import Equipamento

_ERROS_OBRIGATORIO = {
    "blank": mensagens.CAMPO_OBRIGATORIO,
    "null": mensagens.CAMPO_OBRIGATORIO,
}
_CAMPOS_REGISTRADOS = (
    "equipamento_id",
    "cliente_id",
    "data_retirada",
    "data_devolucao_prevista",
    "valor_diaria_contratada",
    "quantidade_diarias",
    "valor_contratado",
)


def calcular_diarias(data_retirada: date, data_devolucao_prevista: date) -> int:
    """Diárias inclusivas: (prevista − retirada) + 1 (RN004 d)."""
    return (data_devolucao_prevista - data_retirada).days + 1


def calcular_valor_contratado(
    quantidade_diarias: int, valor_diaria: Decimal
) -> Decimal:
    """Valor exato em Decimal, com duas casas (RN004 e)."""
    return (valor_diaria * quantidade_diarias).quantize(Decimal("0.01"))


class Situacao(models.TextChoices):
    """Situação de apresentação (RN004 g); nunca persistida."""

    ATIVO = "ativo", "Ativo"
    ATRASADO = "atrasado", "Atrasado"
    ENCERRADO = "encerrado", "Encerrado"
    ENCERRADO_COM_ATRASO = "encerrado_com_atraso", "Encerrado com atraso"


class AluguelQuerySet(models.QuerySet):
    def abertos(self):
        return self.filter(data_devolucao_real__isnull=True)

    def encerrados(self):
        return self.filter(data_devolucao_real__isnull=False)


class Aluguel(ModeloValidado):
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.PROTECT,
        related_name="alugueis",
        verbose_name="equipamento",
        error_messages=_ERROS_OBRIGATORIO,
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="alugueis",
        verbose_name="cliente",
        error_messages=_ERROS_OBRIGATORIO,
    )
    data_retirada = models.DateField(
        "data de retirada", error_messages=_ERROS_OBRIGATORIO
    )
    data_devolucao_prevista = models.DateField(
        "devolução prevista", error_messages=_ERROS_OBRIGATORIO
    )
    data_devolucao_real = models.DateField("data de devolução", null=True, blank=True)
    valor_diaria_contratada = models.DecimalField(
        "diária contratada", max_digits=10, decimal_places=2
    )
    quantidade_diarias = models.PositiveIntegerField("quantidade de diárias")
    valor_contratado = models.DecimalField(
        "valor contratado", max_digits=12, decimal_places=2
    )

    objects = AluguelQuerySet.as_manager()

    class Meta:
        verbose_name = "aluguel"
        verbose_name_plural = "aluguéis"
        constraints = [
            # RN001: no máximo um aluguel aberto por equipamento, inclusive com
            # retirada futura (I1). Índice único parcial no PostgreSQL e no SQLite.
            models.UniqueConstraint(
                fields=["equipamento"],
                condition=Q(data_devolucao_real__isnull=True),
                name="aluguel_um_aberto_por_equipamento",
                violation_error_message=mensagens.EQUIPAMENTO_INDISPONIVEL,
            ),
            models.CheckConstraint(
                condition=Q(data_devolucao_prevista__gte=F("data_retirada")),
                name="aluguel_prevista_apos_retirada",
            ),
            models.CheckConstraint(
                condition=Q(data_devolucao_real__isnull=True)
                | Q(data_devolucao_real__gte=F("data_retirada")),
                name="aluguel_devolucao_apos_retirada",
            ),
            models.CheckConstraint(
                condition=Q(valor_diaria_contratada__gt=0)
                & Q(quantidade_diarias__gte=1)
                & Q(valor_contratado__gt=0),
                name="aluguel_valores_positivos",
            ),
        ]

    def __str__(self) -> str:
        return f"Aluguel {self.pk} — {self.equipamento_id} para {self.cliente_id}"

    # Validação ----------------------------------------------------------------

    def clean(self) -> None:
        erros: dict[str, str] = {}
        retirada, prevista, real = (
            self.data_retirada,
            self.data_devolucao_prevista,
            self.data_devolucao_real,
        )
        if retirada and prevista and prevista < retirada:
            erros["data_devolucao_prevista"] = mensagens.PREVISTA_ANTES_DA_RETIRADA
        if retirada and real and real < retirada:
            erros["data_devolucao_real"] = mensagens.DEVOLUCAO_ANTES_DA_RETIRADA

        if self._state.adding:
            erros.update(self._validar_registro(erros))
        else:
            self._validar_alteracao()
        if erros:
            raise ValidationError(erros)

    def _validar_registro(self, erros_de_data: dict[str, str]) -> dict[str, str]:
        """Invariantes do registro: equipamento disponível e valores congelados coerentes."""
        erros: dict[str, str] = {}
        if self.equipamento_id and self.data_devolucao_real is None:
            equipamento = self.equipamento
            aberto = Aluguel.objects.abertos().filter(
                equipamento_id=self.equipamento_id
            )
            if not equipamento.ativo or aberto.exists():
                erros["equipamento"] = mensagens.EQUIPAMENTO_INDISPONIVEL
        valores = (
            self.data_retirada,
            self.data_devolucao_prevista,
            self.valor_diaria_contratada,
            self.quantidade_diarias,
            self.valor_contratado,
        )
        if (
            self.equipamento_id
            and not erros_de_data
            and all(v is not None for v in valores)
        ):
            diarias = calcular_diarias(self.data_retirada, self.data_devolucao_prevista)
            esperado = calcular_valor_contratado(diarias, self.valor_diaria_contratada)
            if (
                self.quantidade_diarias != diarias
                or self.valor_contratado != esperado
                or self.valor_diaria_contratada != self.equipamento.valor_diaria
            ):
                erros[NON_FIELD_ERRORS] = mensagens.VALORES_DO_ALUGUEL_INCONSISTENTES
        return erros

    def _validar_alteracao(self) -> None:
        """Aluguel registrado não muda (I2); só a devolução é gravada, uma única vez."""
        original = (
            Aluguel.objects.filter(pk=self.pk)
            .values(*_CAMPOS_REGISTRADOS, "data_devolucao_real")
            .first()
        )
        if original is None:
            return
        if original["data_devolucao_real"] is not None:
            if any(
                getattr(self, campo) != original[campo]
                for campo in (*_CAMPOS_REGISTRADOS, "data_devolucao_real")
            ):
                raise ValidationError(mensagens.ALUGUEL_ENCERRADO)
            return
        if any(
            getattr(self, campo) != original[campo] for campo in _CAMPOS_REGISTRADOS
        ):
            raise ValidationError(mensagens.ALUGUEL_INALTERAVEL)

    # Atributos derivados ------------------------------------------------------

    @property
    def aberto(self) -> bool:
        return self.data_devolucao_real is None

    def situacao_codigo(self, hoje: date | None = None) -> str:
        """Calculada com a data atual em America/Recife (RN004 g)."""
        if self.data_devolucao_real is None:
            hoje = hoje or timezone.localdate()
            if self.data_devolucao_prevista < hoje:
                return Situacao.ATRASADO
            return Situacao.ATIVO
        if self.data_devolucao_real > self.data_devolucao_prevista:
            return Situacao.ENCERRADO_COM_ATRASO
        return Situacao.ENCERRADO

    def situacao(self, hoje: date | None = None) -> str:
        return Situacao(self.situacao_codigo(hoje)).label

    def pode_devolver(self, hoje: date | None = None) -> bool:
        """Aberto e com a retirada já alcançada (I1)."""
        hoje = hoje or timezone.localdate()
        return self.aberto and hoje >= self.data_retirada
