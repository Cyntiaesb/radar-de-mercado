"""Coleta anúncios da Biblioteca da Meta pelo Apify (ator jmlp~meta-ad-library-scraper).

Uso: python scripts/coleta_anuncios.py <slug> "<busca>" ["<busca>" ...] [--pais BR] [--status all] [--max 300] [--teto 2] [--frase | --pagina]
Cada busca é um site (exemplo.com.br) ou um nome de anunciante. Com --pagina, cada busca é o page_id da página
(tirado de uma coleta anterior): traz o histórico inteiro e evita homônimo. --max vale pro total da rodada. Grava coletas/<slug>/anuncios.json (bruto,
sem duplicar por ad_archive_id). O token vem do arquivo .env desta pasta.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENV = RAIZ / ".env"
ATOR = "jmlp~meta-ad-library-scraper"


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
    return json.load(urllib.request.urlopen(req, timeout=120))


def url_busca(termo: str, pais: str, status: str, tipo: str) -> str:
    if tipo == "pagina":
        return (f"https://www.facebook.com/ads/library/?active_status={status}&ad_type=all&country={pais}"
                f"&view_all_page_id={termo}&media_type=all")
    q = urllib.parse.quote(termo)
    return (f"https://www.facebook.com/ads/library/?active_status={status}&ad_type=all&country={pais}"
            f"&q={q}&search_type={tipo}&media_type=all")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("buscas", nargs="+")
    ap.add_argument("--pais", default="BR")
    ap.add_argument("--status", default="all", help="active ou all")
    ap.add_argument("--max", type=int, default=300)
    ap.add_argument("--teto", type=float, default=2.0)
    ap.add_argument("--frase", action="store_true", help="frase exata (pra achar anunciante novo pelo tema)")
    ap.add_argument("--pagina", action="store_true", help="cada busca é o page_id (histórico inteiro, sem homônimo)")
    a = ap.parse_args()
    tok = token()
    tipo = "pagina" if a.pagina else "keyword_exact_phrase" if a.frase else "keyword_unordered"
    urls = [url_busca(b, a.pais, a.status, tipo) for b in a.buscas]
    run = api(f"acts/{ATOR}/runs?maxTotalChargeUsd={a.teto}", tok, {"adLibraryUrls": urls, "maxAds": a.max})["data"]
    print(f"Rodando no Apify ({len(urls)} buscas)...", flush=True)
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(20)
        run = api(f"actor-runs/{run['id']}", tok)["data"]
    itens = api(f"datasets/{run['defaultDatasetId']}/items?format=json&clean=1", tok) if run["status"] == "SUCCEEDED" else []
    pasta = RAIZ / "coletas" / a.slug
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / "anuncios.json"
    velhos = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else []
    vistos = {i.get("ad_archive_id") for i in velhos}
    novos = [i for i in itens if i.get("ad_archive_id") not in vistos]
    arq.write_text(json.dumps(velhos + novos, ensure_ascii=False), encoding="utf-8")
    pags = {}
    for i in itens:
        pags[i.get("page_name")] = pags.get(i.get("page_name"), 0) + 1
    top = sorted(pags.items(), key=lambda x: -x[1])[:25]
    print(f"Status: {run['status']} · custo US$ {run.get('usageTotalUsd') or 0:.2f} · {len(itens)} anúncios "
          f"({len(novos)} novos) · páginas: {top}")


if __name__ == "__main__":
    main()
