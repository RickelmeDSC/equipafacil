"""Configuração do projeto EquipaFácil (Django 5.2 LTS).

Tudo o que é sensível ou depende do ambiente vem de variáveis de ambiente
(modelo em ``.env.example``). Nenhum segredo é versionado.
"""

import os
from pathlib import Path

from config.env import (
    carregar_arquivo_env,
    configurar_banco,
    obter_booleano,
    obter_lista,
    obter_obrigatorio,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Arquivo .env opcional, só para desenvolvimento local.
# DJANGO_ENV_FILE aponta outro arquivo; vazio desativa a leitura.
_arquivo_env = os.environ.get("DJANGO_ENV_FILE", str(BASE_DIR / ".env"))
if _arquivo_env:
    carregar_arquivo_env(Path(_arquivo_env))

SECRET_KEY = obter_obrigatorio("DJANGO_SECRET_KEY")
DEBUG = obter_booleano("DJANGO_DEBUG", padrao=False)
ALLOWED_HOSTS = obter_lista("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = obter_lista("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "equipamentos",
    "clientes",
    "alugueis",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# PostgreSQL é o banco-alvo; SQLite só no desenvolvimento local (ver config/env.py).
DATABASES = configurar_banco(os.environ, BASE_DIR, DEBUG)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Idioma e fuso: "data atual" sempre em America/Recife (timezone.localdate()).
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
