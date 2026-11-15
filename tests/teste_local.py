"""Teste sem internet e sem custo: roda os resumos com dados fictícios e monta o painel de exemplo.

Uso: python tests/teste_local.py
Cria coletas/_teste, confere as contas e apaga a pasta no fim. Não chama o Apify.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "coletas" / "_teste"
sys.stdout.reconfigure(encoding="utf-8")
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def roda(*args):
    r = subprocess.run([sys.executable, *map(str, args)], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", env=ENV)
    assert r.returncode == 0, r.stderr[-600:]
    return r.stdout


REELS = [{"ownerUsername": "exemplo", "videoPlayCount": v, "timestamp": f"2026-10-0{n}T10:00:00Z", "videoDuration": 30, "likesCount": 10, "commentsCount": c,
          "url": f"https://exemplo.invalid/{n}", "displayUrl": "https://exemplo.invalid/c.jpg", "caption": cap}
         for n, v, c, cap in [(1, 100, 2, "Comenta BOLO que eu te mando."), (2, 300, 4, "Link na bio."), (3, 200, 6, "Me chama no direct.")]]
ANUNCIOS = [{"ad_archive_id": str(n), "page_id": "1", "page_name": "Pagina Exemplo", "is_active": ativo, "start_date": "2026-09-01", "end_date": None if ativo else "2026-09-20",
             "snapshot": {"body": {"text": t}, "link_url": "https://exemplo.invalid/oferta?x=1", "images": [{"original_image_url": "https://exemplo.invalid/i.jpg"}]}}
            for n, ativo, t in [(1, True, "Aprenda a fazer bolo."), (2, False, "Aprenda a fazer bolo."), (3, True, "Curso de doces.")]]

try:
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "reels.json").write_text(json.dumps(REELS), encoding="utf-8")
    (PASTA / "anuncios.json").write_text(json.dumps(ANUNCIOS), encoding="utf-8")

    roda("scripts/resumo_reels.py", "_teste", "@exemplo")
    r = json.loads((PASTA / "reels-resumo.json").read_text(encoding="utf-8"))["exemplo"]
    assert (r["reels"], r["mediana"], r["maior"], r["com_palavra"], r["com_bio"], r["com_direct"]) == (3, 200, 300, 1, 1, 1), r

    roda("scripts/anunciantes.py", "_teste")
    a = json.loads((PASTA / "anunciantes.json").read_text(encoding="utf-8"))[0]
    assert (a["n"], a["ativos"]) == (3, 2), a

    roda("scripts/resumo_anuncios.py", "_teste", "Pagina Exemplo", "--hoje", "2026-10-31")
    assert (PASTA / "anuncios-resumo.json").exists()

    roda("scripts/monta_painel.py", "exemplo")
    assert (RAIZ / "painel" / "exemplo.html").exists()

    sem = {k: v for k, v in ENV.items() if k != "APIFY_TOKEN"}
    if not (RAIZ / ".env").exists():
        r = subprocess.run([sys.executable, "scripts/coleta_reels.py", "_teste", "@exemplo"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", env=sem)
        assert r.returncode != 0 and "APIFY_TOKEN" in r.stderr, r.stderr[-300:]
    print("ok: resumos, painel e aviso de token sem chamar serviço nenhum")
finally:
    shutil.rmtree(PASTA, ignore_errors=True)
    if PASTA.parent.exists() and not any(PASTA.parent.iterdir()):
        PASTA.parent.rmdir()
