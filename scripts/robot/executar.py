"""Executa os testes do Robot Framework em ambiente local e isolado.

Uso:

    python scripts/robot/executar.py                      # todos os cenários
    python scripts/robot/executar.py tests/Cenario16.robot
    python scripts/robot/executar.py --visivel tests/Cenario16.robot

O script sobe um servidor do Django em 127.0.0.1 com o banco SQLite isolado
(``resultados-robot/robot.sqlite3``), gera usuário e senha fictícios só para a
execução, roda o Robot e encerra o servidor. Os relatórios ficam em
``resultados-robot/``. Nada é enviado a Render ou Neon.
"""

import argparse
import os
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
RESULTADOS = RAIZ / "resultados-robot"
HOST = "127.0.0.1"


def _porta_em_uso(porta: int) -> bool:
    with socket.socket() as conexao:
        conexao.settimeout(0.5)
        return conexao.connect_ex((HOST, porta)) == 0


def _esperar_servidor(base: str, servidor: subprocess.Popen, segundos: int) -> bool:
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        if servidor.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(f"{base}/healthz/", timeout=2) as resposta:
                if resposta.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--porta", type=int, default=8765)
    analisador.add_argument(
        "--visivel", action="store_true", help="mostra o navegador durante o teste"
    )
    analisador.add_argument(
        "alvos", nargs="*", default=["tests"], help="arquivos .robot ou a pasta tests"
    )
    opcoes, extras = analisador.parse_known_args()

    if _porta_em_uso(opcoes.porta):
        print(
            f"A porta {opcoes.porta} já está em uso. Feche o outro servidor ou "
            "use --porta.",
            file=sys.stderr,
        )
        return 2

    base = f"http://{HOST}:{opcoes.porta}"
    RESULTADOS.mkdir(exist_ok=True)
    ambiente = os.environ.copy()
    ambiente.pop("DATABASE_URL", None)
    ambiente.update(
        DJANGO_SETTINGS_MODULE="scripts.robot.settings_robot",
        DJANGO_SECRET_KEY=secrets.token_urlsafe(50),
        EQF_ROBOT_USUARIO="robot.funcionario",
        EQF_ROBOT_SENHA=secrets.token_urlsafe(16),
        EQF_ROBOT_PYTHON=sys.executable,
        PYTHONPATH=str(RAIZ),
    )

    gerenciar = [sys.executable, str(RAIZ / "manage.py")]
    subprocess.run(
        [*gerenciar, "migrate", "--verbosity", "0"], cwd=RAIZ, env=ambiente, check=True
    )
    with open(RESULTADOS / "servidor.log", "w", encoding="utf-8") as registro:
        servidor = subprocess.Popen(
            [*gerenciar, "runserver", f"{HOST}:{opcoes.porta}", "--noreload"],
            cwd=RAIZ,
            env=ambiente,
            stdout=registro,
            stderr=subprocess.STDOUT,
        )
        try:
            if not _esperar_servidor(base, servidor, segundos=40):
                print(
                    "O servidor de teste não iniciou. Veja "
                    "resultados-robot/servidor.log.",
                    file=sys.stderr,
                )
                return 2
            comando = [
                sys.executable,
                "-m",
                "robot",
                "--outputdir",
                str(RESULTADOS),
                "--variable",
                f"BASE_URL:{base}",
                "--variable",
                f"HEADLESS:{'false' if opcoes.visivel else 'true'}",
                *extras,
                *opcoes.alvos,
            ]
            return subprocess.run(comando, cwd=RAIZ, env=ambiente).returncode
        finally:
            servidor.terminate()
            try:
                servidor.wait(timeout=10)
            except subprocess.TimeoutExpired:
                servidor.kill()


if __name__ == "__main__":
    raise SystemExit(main())
