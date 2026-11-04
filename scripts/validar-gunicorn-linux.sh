#!/usr/bin/env bash
# Valida em Linux o comando de início do Render com o Gunicorn.
# Uso, na raiz do repositório: bash scripts/validar-gunicorn-linux.sh
#
# Cria um ambiente virtual temporário com requirements.txt, roda o
# collectstatic e sobe o Gunicorn com o mesmo comando do Render em produção
# simulada. A DATABASE_URL é fictícia e local (porta 1): nenhuma conexão sai da
# máquina e nenhum banco é usado. O proxy do Render é simulado: o cliente local
# não está em FORWARDED_ALLOW_IPS, como acontece com o IP do proxy real.
# O comando do Render escuta em 0.0.0.0; durante os segundos do teste, a porta
# fica acessível na rede local. Ao terminar, encerra o Gunicorn e apaga o
# ambiente temporário. Sai com código diferente de zero se algo falhar.
set -o errexit
set -o nounset
set -o pipefail

PYTHON="${PYTHON:-python3.13}"
export PORT="${PORT:-8765}"
TEMP="$(mktemp -d)"
PID=""

encerrar() {
    if [[ -n "$PID" ]]; then
        kill "$PID" 2>/dev/null || true
        wait "$PID" 2>/dev/null || true
    fi
    rm -rf "$TEMP"
}
trap encerrar EXIT

"$PYTHON" --version
"$PYTHON" -m venv "$TEMP/venv"
VENV_PY="$TEMP/venv/bin/python"
"$VENV_PY" -m pip install --quiet --requirement requirements.txt
"$VENV_PY" -m pip check

export DJANGO_ENV_FILE=""
export DJANGO_DEBUG="False"
DJANGO_SECRET_KEY="$("$VENV_PY" -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_SECRET_KEY
export DATABASE_URL="postgresql://app@127.0.0.1:1/equipafacil?sslmode=require"
export RENDER_EXTERNAL_HOSTNAME="equipafacil.onrender.com"
export DJANGO_SECURE_PROXY_SSL_HEADER="True"
export FORWARDED_ALLOW_IPS="192.0.2.1"
unset WEB_CONCURRENCY DB_ENGINE DB_NAME DB_USER DB_HOST

"$VENV_PY" manage.py check --deploy
"$VENV_PY" manage.py collectstatic --noinput > /dev/null

# Mesmo comando de início configurado no Render.
PATH="$TEMP/venv/bin:$PATH" gunicorn config.wsgi:application --bind 0.0.0.0:$PORT \
    > "$TEMP/gunicorn.log" 2>&1 &
PID=$!

for _ in $(seq 1 60); do
    if "$VENV_PY" -c "import socket; socket.create_connection(('127.0.0.1', $PORT), 1)" 2>/dev/null; then
        break
    fi
    sleep 0.5
done

"$VENV_PY" scripts/validar_servidor.py "http://127.0.0.1:$PORT" "$RENDER_EXTERNAL_HOSTNAME"

WORKERS="$(grep -c "Booting worker" "$TEMP/gunicorn.log" || true)"
TRACEBACKS="$(grep -c "Traceback" "$TEMP/gunicorn.log" || true)"
# A verificação "health check com Host inválido" provoca, de propósito, um
# DisallowedHost, que o Django registra com traceback (avisos de Host inválido vão
# para o console). Ele é esperado uma única vez; qualquer outro traceback é falha.
HOST_INVALIDO="$(grep -c "^django.core.exceptions.DisallowedHost:" "$TEMP/gunicorn.log" || true)"
ERROS=$((TRACEBACKS - HOST_INVALIDO))
echo "Workers iniciados: $WORKERS (esperado: 1) | Host inválido registrado: $HOST_INVALIDO (esperado: 1) | outros tracebacks: $ERROS (esperado: 0)"
cat "$TEMP/gunicorn.log"
[[ "$WORKERS" == "1" && "$HOST_INVALIDO" == "1" && "$ERROS" == "0" ]]
