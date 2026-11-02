"""Configuração do projeto EquipaFácil (Django 5.2 LTS).

Tudo o que é sensível ou depende do ambiente vem de variáveis de ambiente
(modelo em ``.env.example``). Nenhum segredo é versionado.
"""

import os
import sys
from pathlib import Path

from config.env import (
    carregar_arquivo_env,
    configurar_banco,
    exigir_banco_local_para_testes,
    obter_booleano,
    obter_inteiro,
    obter_lista,
    obter_obrigatorio,
    validar_chave_secreta,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Arquivo .env opcional, só para desenvolvimento local.
# DJANGO_ENV_FILE aponta outro arquivo; vazio desativa a leitura.
_arquivo_env = os.environ.get("DJANGO_ENV_FILE", str(BASE_DIR / ".env"))
if _arquivo_env:
    carregar_arquivo_env(Path(_arquivo_env))

SECRET_KEY = obter_obrigatorio("DJANGO_SECRET_KEY")
DEBUG = obter_booleano("DJANGO_DEBUG", padrao=False)
validar_chave_secreta(SECRET_KEY, DEBUG)
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
    # WhiteNoise serve os arquivos estáticos; fica logo após o SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Toda página exige login, exceto as marcadas com login_not_required
    # (LoginView e o login do Admin já vêm marcados no Django 5.2).
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
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

# PostgreSQL é o banco-alvo: DATABASE_URL (hospedagem) tem precedência sobre DB_*
# (local); SQLite só no desenvolvimento. Regras em config/env.py.
DATABASES = configurar_banco(os.environ, BASE_DIR, DEBUG)
if sys.argv[1:2] == ["test"]:
    exigir_banco_local_para_testes(DATABASES["default"])

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

# Autenticação nativa (D1, D15): contas criadas pelo Django Admin; sem cadastro
# público e sem recuperação de senha por e-mail. Nomes de rota provisórios até o
# aceite do contrato DEV-01.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "login"

# Segurança. Fora do desenvolvimento (DEBUG desativado), cookies só trafegam por
# HTTPS e o HTTP é redirecionado. HSTS e cabeçalho de proxy são definidos no
# deploy (DEV-08), por variável de ambiente.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = obter_booleano("DJANGO_SECURE_SSL_REDIRECT", padrao=not DEBUG)
SECURE_HSTS_SECONDS = obter_inteiro("DJANGO_SECURE_HSTS_SECONDS", padrao=0)
if obter_booleano("DJANGO_SECURE_PROXY_SSL_HEADER", padrao=False):
    # Só ative atrás de um proxy que sempre define X-Forwarded-Proto.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"

# Idioma e fuso: "data atual" sempre em America/Recife (timezone.localdate()).
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Fora do desenvolvimento, o collectstatic gera nomes com hash e versões
# comprimidas, servidas pelo WhiteNoise. No desenvolvimento e nos testes, o
# armazenamento simples dispensa o collectstatic.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
