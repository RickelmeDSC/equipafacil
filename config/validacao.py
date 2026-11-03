"""Base dos modelos de domínio: normaliza, valida ao gravar e evita mensagens repetidas."""

from django.core.exceptions import ValidationError
from django.db import models


def _sem_mensagens_repetidas(erro: ValidationError) -> ValidationError:
    """Remove mensagens idênticas de um mesmo campo (ex.: dois validadores com o mesmo texto)."""
    if not hasattr(erro, "error_dict"):
        return erro
    resultado = {}
    for campo, lista in erro.error_dict.items():
        vistas: set[str] = set()
        unicos = []
        for item in lista:
            texto = " ".join(item.messages)
            if texto not in vistas:
                vistas.add(texto)
                unicos.append(item)
        resultado[campo] = unicos
    return ValidationError(resultado)


class ModeloValidado(models.Model):
    """Valida o modelo também fora dos formulários.

    ``save()`` chama ``full_clean()``: as regras de aplicação valem para qualquer
    gravação feita pelo ORM com ``save()``. Operações em lote (``bulk_create``,
    ``update``) não passam por aqui; para elas, valem as restrições do banco.
    Validação de aplicação não elimina corridas: operações concorrentes usam os
    serviços transacionais e as restrições do PostgreSQL.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def normalizar(self) -> None:
        """Ajusta os valores de entrada antes da validação (sobrescrito nos modelos)."""

    def full_clean(self, *args, **kwargs) -> None:
        self.normalizar()
        super().full_clean(*args, **kwargs)

    def clean_fields(self, exclude=None) -> None:
        try:
            super().clean_fields(exclude=exclude)
        except ValidationError as erro:
            raise _sem_mensagens_repetidas(erro) from None
