#!/usr/bin/env bash
# Build do Web Service do EquipaFácil no Render.
# Comando de build no Render: bash scripts/render-build.sh
#
# Instala as dependências de execução, confere a configuração de produção e
# coleta os arquivos estáticos para o WhiteNoise. Não acessa o banco de dados
# e não executa migrations: a estratégia de migrations depende de decisão
# específica (veja docs/deploy-render-neon.md).
set -o errexit
set -o nounset
set -o pipefail

python --version
python -m pip install --requirement requirements.txt
python -m pip check
python manage.py check --deploy
python manage.py collectstatic --noinput
