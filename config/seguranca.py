"""Ajustes de segurança do projeto EquipaFácil."""

import re

from django.views.debug import SafeExceptionReporterFilter


class FiltroDeRelatorioDeErros(SafeExceptionReporterFilter):
    """Mascara também ``DATABASE_URL`` nos relatórios e páginas de erro.

    O filtro padrão do Django só mascara nomes com API, AUTH, TOKEN, KEY,
    SECRET, PASS, SIGNATURE ou HTTP_COOKIE. A ``DATABASE_URL`` contém a senha
    do banco e o ``runserver`` copia o ambiente do processo para
    ``request.META``, então ela apareceria na página de erro com DEBUG ativo.
    """

    hidden_settings = re.compile(
        "API|AUTH|TOKEN|KEY|SECRET|PASS|SIGNATURE|HTTP_COOKIE|DATABASE_URL",
        flags=re.IGNORECASE,
    )
