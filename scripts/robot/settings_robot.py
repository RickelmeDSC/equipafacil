"""Configuração do Django usada SOMENTE pela automação com Robot Framework.

Reaproveita ``config.settings`` e troca apenas o banco: um arquivo SQLite
descartável em ``resultados-robot/``. O ``.env`` não é lido e ``DATABASE_URL`` é
descartada, então Neon, Render e o ``db.sqlite3`` de desenvolvimento nunca são
usados pela automação.
"""

import os
import secrets
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
PASTA_DE_RESULTADOS = RAIZ / "resultados-robot"
BANCO_ROBOT = PASTA_DE_RESULTADOS / "robot.sqlite3"

# Precisa vir antes de importar config.settings, que lê o ambiente ao carregar.
os.environ["DJANGO_ENV_FILE"] = ""
os.environ.pop("DATABASE_URL", None)
os.environ["DB_ENGINE"] = "sqlite"
os.environ["DJANGO_DEBUG"] = "True"
os.environ["DJANGO_ALLOWED_HOSTS"] = "127.0.0.1,localhost"
os.environ.setdefault("DJANGO_SECRET_KEY", secrets.token_urlsafe(50))

from config.settings import *  # noqa: E402, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BANCO_ROBOT,
    }
}
