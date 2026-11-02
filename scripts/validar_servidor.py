"""Verifica por HTTP um servidor do EquipaFácil em produção simulada.

Uso: python scripts/validar_servidor.py <url-base> <host-permitido>
Exemplo: python scripts/validar_servidor.py http://127.0.0.1:8765 equipafacil.onrender.com

Só usa a biblioteca padrão e não precisa de banco: verifica health check,
validação de Host, redirecionamento para HTTPS, reconhecimento do proxy
(X-Forwarded-Proto), cookie Secure e arquivos estáticos do WhiteNoise.
Requer o collectstatic já executado (staticfiles/staticfiles.json).
Sai com código 1 se alguma verificação falhar.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class _SemRedirecionar(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


_abridor = urllib.request.build_opener(_SemRedirecionar)


def _requisitar(base: str, caminho: str, cabecalhos: dict[str, str]):
    pedido = urllib.request.Request(base + caminho, headers=cabecalhos)
    try:
        resposta = _abridor.open(pedido, timeout=10)
    except urllib.error.HTTPError as erro:
        resposta = erro
    with resposta:
        return resposta.status, resposta.headers, resposta.read()


def main(base: str, host: str) -> int:
    https = {"Host": host, "X-Forwarded-Proto": "https"}
    css = json.loads((RAIZ / "staticfiles" / "staticfiles.json").read_text())["paths"][
        "admin/css/base.css"
    ]
    falhas = 0

    def verificar(descricao: str, condicao: bool, detalhe: str) -> None:
        nonlocal falhas
        falhas += not condicao
        print(f"[{'ok' if condicao else 'FALHA'}] {descricao}: {detalhe}")

    status, cab, corpo = _requisitar(base, "/healthz/", {"Host": host})
    verificar("health check", status == 200 and corpo == b"ok\n", f"{status} {corpo!r}")

    status, _, _ = _requisitar(base, "/healthz/", {"Host": "site-externo.example"})
    verificar("health check com Host inválido", status == 400, str(status))

    status, cab, _ = _requisitar(base, "/login/", {"Host": host})
    destino = cab.get("Location", "")
    verificar(
        "HTTP redirecionado para HTTPS",
        status == 301 and destino == f"https://{host}/login/",
        f"{status} {destino}",
    )

    status, cab, _ = _requisitar(base, "/login/", https)
    cookie = cab.get("Set-Cookie", "")
    verificar(
        "HTTPS via proxy reconhecido, sem laço",
        status == 200 and "Secure" in cookie,
        f"{status}, cookie {'Secure' if 'Secure' in cookie else 'sem Secure'}",
    )

    status, cab, _ = _requisitar(base, "/", https)
    destino = cab.get("Location", "")
    verificar(
        "página protegida exige login",
        status == 302 and destino.startswith("/login/"),
        f"{status} {destino}",
    )

    status, cab, corpo = _requisitar(
        base, "/static/" + css, {**https, "Accept-Encoding": "gzip"}
    )
    verificar(
        "estático com hash, comprimido e com cache longo",
        status == 200
        and cab.get("Content-Encoding") == "gzip"
        and "immutable" in cab.get("Cache-Control", ""),
        f"{status} {css} {cab.get('Content-Encoding')} {len(corpo)} bytes",
    )

    print("Resultado:", "aprovado" if not falhas else f"{falhas} falha(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1].rstrip("/"), sys.argv[2]))
