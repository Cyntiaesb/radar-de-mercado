"""Coleta os reels recentes de uma lista de perfis do Instagram pelo Apify.

Uso: python scripts/coleta_reels.py <slug> <@perfil> [<@perfil> ...] [--desde 2026-04-26] [--por-perfil 40] [--teto 2]
Grava coletas/<slug>/reels.json (bruto do Apify). O token vem do arquivo .env desta pasta (ver .env.example).
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENV = RAIZ / ".env"
ATOR = "apify~instagram-reel-scraper"


def token() -> str:
    valor = os.environ.get("APIFY_TOKEN", "")
    if not valor and ENV.exists():
        for l in ENV.read_text(encoding="utf-8").splitlines():
            if l.startswith("APIFY_TOKEN="):
                valor = l.split("=", 1)[1].strip()
    if not valor:
        sys.exit("Falta o APIFY_TOKEN: copie .env.example para .env e cole o seu token.")
    return valor


def api(caminho: str, tok: str, corpo: dict | None = None):
    req = urllib.request.Request("https://api.apify.com/v2/" + caminho,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
                                 method="POST" if corpo is not None else "GET")
    return json.load(urllib.request.urlopen(req, timeout=60))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("perfis", nargs="+")
    ap.add_argument("--desde", default="2026-04-26")
    ap.add_argument("--por-perfil", type=int, default=40)
    ap.add_argument("--teto", type=float, default=2.0, help="gasto máximo em US$")
    a = ap.parse_args()
    tok = token()
    perfis = [p.lstrip("@") for p in a.perfis]
    run = api(f"acts/{ATOR}/runs?maxTotalChargeUsd={a.teto}", tok, {
        "username": perfis, "resultsLimit": a.por_perfil, "onlyPostsNewerThan": a.desde, "skipPinnedPosts": True})["data"]
    print(f"Rodando no Apify ({len(perfis)} perfis)...", flush=True)
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(15)
        run = api(f"actor-runs/{run['id']}", tok)["data"]
    itens = api(f"datasets/{run['defaultDatasetId']}/items?format=json&clean=1", tok) if run["status"] == "SUCCEEDED" else []
    pasta = RAIZ / "coletas" / a.slug
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "reels.json").write_text(json.dumps(itens, ensure_ascii=False), encoding="utf-8")
    por = {}
    for i in itens:
        por[i.get("ownerUsername")] = por.get(i.get("ownerUsername"), 0) + 1
    print(f"Status: {run['status']} · custo US$ {run.get('usageTotalUsd') or 0:.2f} · {len(itens)} reels · {por}")


if __name__ == "__main__":
    main()
