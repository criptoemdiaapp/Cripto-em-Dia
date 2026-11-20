#!/usr/bin/env python3
"""Trava de segurança da rotina automática: só permite commitar arquivos de conteúdo.

Uso: python checar_mudancas.py   (rode ANTES do git commit)
Sai com erro se houver alteração fora das pastas permitidas ou HTML/links inseguros no Markdown.
"""
import re
import subprocess
import sys

PERMITIDOS = (
    re.compile(r"^conteudo/boletim/\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9\-]*\.md$"),
    re.compile(r"^conteudo/paginas/[a-z0-9\-]+\.md$"),
    re.compile(r"^PENDENCIAS\.md$"),
    re.compile(r"^docs/"),
)
PROIBIDO_NO_TEXTO = re.compile(
    r"<\s*(script|iframe|object|embed|form|img|svg|style|link|meta)|javascript:|data:text/html|\bon\w+\s*=",
    re.I)

out = subprocess.run(["git", "status", "--porcelain", "-uall"], capture_output=True, text=True, check=True).stdout
erros = []
for line in out.splitlines():
    path = line[3:].strip().strip('"')
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    if not any(p.match(path) for p in PERMITIDOS):
        erros.append(f"arquivo fora das pastas permitidas: {path}")
        continue
    if path.endswith(".md") and line[:2].strip() != "D":
        txt = open(path, encoding="utf-8").read()
        if PROIBIDO_NO_TEXTO.search(txt):
            erros.append(f"HTML ou link inseguro em {path}")
if erros:
    print("BLOQUEADO:\n  " + "\n  ".join(erros), file=sys.stderr)
    print("Desfaça essas alterações (git checkout -- <arquivo> / remova o arquivo) e rode de novo.", file=sys.stderr)
    sys.exit(1)
print("ok: só conteúdo permitido foi alterado")
