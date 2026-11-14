"""Zera o banco isolado da automação e cria a massa fictícia de um cenário.

Uso (chamado pela keyword "Preparar Massa"; raramente à mão):

    python scripts/robot/massa.py ct16

Cada cenário tem um módulo em ``scripts/robot/massas/`` com a função
``preparar()``. O usuário fictício de teste é recriado a cada chamada, com a
senha recebida pela variável de ambiente ``EQF_ROBOT_SENHA`` (gerada pelo
``executar.py``; nunca fica gravada no repositório).
"""

import importlib
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))
os.environ["DJANGO_SETTINGS_MODULE"] = "scripts.robot.settings_robot"


def main(argumentos: list[str]) -> int:
    if len(argumentos) != 1 or not re.fullmatch(r"ct\d{2}", argumentos[0]):
        print("Uso: python scripts/robot/massa.py ctNN (ex.: ct16)", file=sys.stderr)
        return 2
    cenario = argumentos[0]
    usuario = os.environ.get("EQF_ROBOT_USUARIO", "")
    senha = os.environ.get("EQF_ROBOT_SENHA", "")
    if not usuario or not senha:
        print(
            "EQF_ROBOT_USUARIO e EQF_ROBOT_SENHA não definidas. "
            "Rode os testes por scripts/robot/executar.py.",
            file=sys.stderr,
        )
        return 2

    import django

    django.setup()

    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.management import call_command

    from scripts.robot.settings_robot import BANCO_ROBOT

    banco = settings.DATABASES["default"]
    e_sqlite = banco["ENGINE"] == "django.db.backends.sqlite3"
    if not e_sqlite or Path(banco["NAME"]) != Path(BANCO_ROBOT):
        print("Recusado: o banco configurado não é o banco isolado.", file=sys.stderr)
        return 3

    try:
        modulo = importlib.import_module(f"scripts.robot.massas.{cenario}")
    except ModuleNotFoundError:
        print(
            f"Massa não encontrada: crie scripts/robot/massas/{cenario}.py "
            "com a função preparar().",
            file=sys.stderr,
        )
        return 2

    BANCO_ROBOT.parent.mkdir(exist_ok=True)
    call_command("migrate", verbosity=0, interactive=False)
    call_command("flush", verbosity=0, interactive=False)
    get_user_model().objects.create_user(username=usuario, password=senha)
    modulo.preparar()
    print(f"Massa do {cenario} preparada em {BANCO_ROBOT.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
