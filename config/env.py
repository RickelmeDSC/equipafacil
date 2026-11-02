"""Leitura da configuração do EquipaFácil a partir de variáveis de ambiente.

Sem dependências externas. O arquivo ``.env`` é opcional e serve apenas ao
desenvolvimento local: variáveis já definidas no ambiente sempre prevalecem.
Mensagens de erro citam o nome da variável, nunca o valor, para não expor
segredos em logs.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableMapping
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

_VERDADEIROS = {"1", "true", "yes", "on", "sim"}
_FALSOS = {"0", "false", "no", "off", "nao", "não"}


def _ambiente(ambiente: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if ambiente is None else ambiente


def carregar_arquivo_env(
    caminho: Path, ambiente: MutableMapping[str, str] | None = None
) -> None:
    """Carrega linhas ``CHAVE=valor`` de ``caminho`` sem sobrescrever o ambiente.

    Aceita UTF-8 com ou sem BOM, linhas em branco, comentários iniciados por
    ``#``, o prefixo ``export`` e valores entre aspas simples ou duplas. Não
    aceita comentário na mesma linha de um valor.
    """
    destino = os.environ if ambiente is None else ambiente
    if not caminho.is_file():
        return
    # utf-8-sig descarta o BOM que editores e o PowerShell 5.1 gravam no início.
    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
    for numero, linha in enumerate(linhas, start=1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("export "):
            linha = linha[len("export ") :].lstrip()
        chave, separador, valor = linha.partition("=")
        chave = chave.strip()
        if not separador or not chave:
            raise ImproperlyConfigured(
                f"Linha {numero} inválida em {caminho.name}: use CHAVE=valor."
            )
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        destino.setdefault(chave, valor)


def obter_obrigatorio(nome: str, ambiente: Mapping[str, str] | None = None) -> str:
    """Retorna o valor de ``nome`` ou falha se ausente ou vazio."""
    valor = _ambiente(ambiente).get(nome, "").strip()
    if not valor:
        raise ImproperlyConfigured(f"Defina a variável de ambiente {nome}.")
    return valor


def validar_chave_secreta(chave: str, debug: bool) -> None:
    """Recusa chave fraca fora do desenvolvimento, com o critério do Django.

    Mesmo critério do aviso ``security.W009`` do ``check --deploy`` (menos de 50
    caracteres, menos de 5 caracteres distintos ou prefixo ``django-insecure-``),
    mas aplicado na inicialização, para que a chave de exemplo nunca rode com
    ``DEBUG`` desativado.
    """
    if debug:
        return
    if len(chave) < 50 or len(set(chave)) < 5 or chave.startswith("django-insecure-"):
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY fraca para uso com DEBUG desativado: gere uma chave "
            "aleatória com pelo menos 50 caracteres (veja o README)."
        )


def obter_booleano(
    nome: str, padrao: bool, ambiente: Mapping[str, str] | None = None
) -> bool:
    """Interpreta ``nome`` como booleano; ausente ou vazio retorna ``padrao``."""
    valor = _ambiente(ambiente).get(nome, "").strip().lower()
    if not valor:
        return padrao
    if valor in _VERDADEIROS:
        return True
    if valor in _FALSOS:
        return False
    raise ImproperlyConfigured(f"A variável {nome} deve ser True ou False (ou 1/0).")


def obter_inteiro(
    nome: str, padrao: int, ambiente: Mapping[str, str] | None = None
) -> int:
    """Interpreta ``nome`` como inteiro não negativo; ausente retorna ``padrao``."""
    valor = _ambiente(ambiente).get(nome, "").strip()
    if not valor:
        return padrao
    if not valor.isdigit():
        raise ImproperlyConfigured(
            f"A variável {nome} deve ser um número inteiro não negativo."
        )
    return int(valor)


def obter_lista(nome: str, ambiente: Mapping[str, str] | None = None) -> list[str]:
    """Interpreta ``nome`` como lista separada por vírgulas, sem itens vazios."""
    valor = _ambiente(ambiente).get(nome, "")
    return [item.strip() for item in valor.split(",") if item.strip()]


def configurar_banco(
    ambiente: Mapping[str, str], base_dir: Path, debug: bool
) -> dict[str, dict[str, object]]:
    """Monta ``DATABASES`` a partir de ``DB_ENGINE`` e das variáveis ``DB_*``.

    PostgreSQL é o banco-alvo do projeto e o padrão. SQLite é um recurso
    temporário, permitido apenas no desenvolvimento local (``DEBUG`` ativo).
    """
    motor = ambiente.get("DB_ENGINE", "postgresql").strip().lower()
    if motor == "sqlite":
        if not debug:
            raise ImproperlyConfigured(
                "DB_ENGINE=sqlite é apenas para desenvolvimento local e exige "
                "DJANGO_DEBUG=True. Fora do desenvolvimento, use PostgreSQL."
            )
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": base_dir / "db.sqlite3",
            }
        }
    if motor == "postgresql":
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": obter_obrigatorio("DB_NAME", ambiente),
                "USER": obter_obrigatorio("DB_USER", ambiente),
                "PASSWORD": ambiente.get("DB_PASSWORD", ""),
                "HOST": ambiente.get("DB_HOST", "localhost").strip() or "localhost",
                "PORT": ambiente.get("DB_PORT", "5432").strip() or "5432",
                "OPTIONS": {
                    "sslmode": ambiente.get("DB_SSLMODE", "prefer").strip() or "prefer",
                },
            }
        }
    raise ImproperlyConfigured("DB_ENGINE deve ser 'postgresql' ou 'sqlite'.")
