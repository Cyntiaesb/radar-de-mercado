"""Coleta de reputação: Reclame Aqui, Reddit e comentários do YouTube. Grava coletas/<slug>/reputacao-bruta.json.

Uso:
  python scripts/coleta_reputacao.py <slug> \
      --reclameaqui slug-da-empresa "Nome da Empresa" \
      --reddit "Nome da Empresa" "Nome do Concorrente" \
      --youtube <id-do-video> --yt-busca "nome e tema" [--teto 1.0]

- Reclame Aqui: o site bloqueia acesso direto (proteção anti-robô), então vai pelo Apify (blackfalcondata/reclameaqui-scraper,
  ~US$ 0,01 por reclamação + US$ 0,02 por empresa). Valor com hífen e sem espaço = slug da empresa (exato);
  com espaço = busca por nome, que pode trazer homônimo e precisa de filtro.
- Reddit: sem login a API recusa, então vai pelo Apify (trudax/reddit-scraper-lite), posts + comentários.
- YouTube: yt-dlp, sem custo, comentários mais curtidos. --youtube aceita id ou link; --yt-busca acha os 3 primeiros vídeos.
O token do Apify vem do arquivo .env desta pasta (ver coleta_reels.py). --teto é o gasto máximo de cada rodada no Apify.
A leitura (do que reclamam, o que elogiam, o que é homônimo) é feita depois, em cima deste arquivo.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coleta_reels import RAIZ, token  # noqa: E402


def apify(ator, entrada, teto):
    u = f"https://api.apify.com/v2/acts/{ator}/run-sync-get-dataset-items?timeout=300&maxTotalChargeUsd={teto}"
    r = urllib.request.Request(u, data=json.dumps(entrada).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer " + token()})
    try:
        return json.loads(urllib.request.urlopen(r, timeout=360).read())
    except urllib.error.HTTPError as e:
        return {"erro": f"HTTP {e.code}", "msg": e.read()[:300].decode("utf-8", "ignore")}


def reclameaqui(valores, teto, maximo):
    slugs = [v for v in valores if " " not in v and v == v.lower()]
    nomes = [v for v in valores if v not in slugs]
    entrada = {"companies": slugs, "searchQueries": nomes, "includeCompanyProfile": True, "scrapeComplaints": True, "includeInteractions": True,
               "extractContacts": False, "statusFilter": ["LATEST"], "maxComplaintsPerCompany": maximo, "descriptionMaxLength": 800}
    d = apify("blackfalcondata~reclameaqui-scraper", entrada, teto)
    if isinstance(d, dict):
        return {"erro": d, "empresas": [], "reclamacoes": []}
    return {"pedido": {"slugs": slugs, "nomes": nomes},
            "empresas": [x for x in d if x.get("recordType") == "company"],
            "reclamacoes": [x for x in d if x.get("recordType") != "company"]}


def reddit(termos, teto, maximo):
    entrada = {"searches": termos, "searchPosts": True, "searchComments": False, "searchCommunities": False, "searchUsers": False, "skipCommunity": True,
               "sort": "relevance", "maxItems": maximo * len(termos) * 6, "maxPostCount": maximo, "maxComments": 20,
               "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}}
    d = apify("trudax~reddit-scraper-lite", entrada, teto)
    if isinstance(d, dict):
        return {"erro": d, "itens": []}
    campos = ("dataType", "communityName", "createdAt", "upVotes", "numberOfComments", "title", "body", "url", "postId", "parentId")
    return {"termos": termos, "itens": [{k: x.get(k) for k in campos} for x in d]}


def ytdlp(*args):
    if not importlib.util.find_spec("yt_dlp"):
        sys.exit("Falta o yt-dlp: rode pip install -r requirements.txt")
    r = subprocess.run([sys.executable, "-m", "yt_dlp", *args], capture_output=True, text=True, encoding="utf-8", timeout=600)
    return r.stdout


def youtube(ids, buscas, por_video):
    alvos = [i if i.startswith("http") else "https://www.youtube.com/watch?v=" + i for i in ids]
    for b in buscas:
        alvos += ["https://www.youtube.com/watch?v=" + v for v in ytdlp("--flat-playlist", "--print", "id", f"ytsearch3:{b}").split()]
    out = []
    for u in dict.fromkeys(alvos):
        try:
            d = json.loads(ytdlp("--skip-download", "--write-comments", "--extractor-args", f"youtube:max_comments={por_video},all,0,0;comment_sort=top", "-J", u))
        except json.JSONDecodeError:
            d = None
        if not d:
            out.append({"url": u, "erro": "yt-dlp não devolveu o vídeo"})
            continue
        cs = sorted(d.get("comments") or [], key=lambda c: -(c.get("like_count") or 0))
        out.append({"url": u, "titulo": d.get("title"), "canal": d.get("channel"), "views": d.get("view_count"),
                    "comentarios": [{"texto": c.get("text", ""), "likes": c.get("like_count") or 0, "data": c.get("timestamp")} for c in cs]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--reclameaqui", nargs="*", default=[])
    ap.add_argument("--reddit", nargs="*", default=[])
    ap.add_argument("--youtube", nargs="*", default=[])
    ap.add_argument("--yt-busca", nargs="*", default=[])
    ap.add_argument("--max", type=int, default=20, help="reclamações por empresa e posts por termo")
    ap.add_argument("--teto", type=float, default=1.0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    arq = RAIZ / "coletas" / a.slug / "reputacao-bruta.json"
    arq.parent.mkdir(parents=True, exist_ok=True)
    # junta com o que já foi coletado: rodar só uma fonte não apaga as outras
    saida = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    saida["data"] = date.today().strftime("%d/%m/%Y")
    grava = lambda: arq.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.reclameaqui:
        saida["reclameaqui"] = reclameaqui(a.reclameaqui, a.teto, a.max)
        grava()
        print("Reclame Aqui:", len(saida["reclameaqui"]["empresas"]), "empresas,", len(saida["reclameaqui"]["reclamacoes"]), "reclamações")
    if a.reddit:
        saida["reddit"] = reddit(a.reddit, a.teto, a.max)
        grava()
        print("Reddit:", len(saida["reddit"]["itens"]), "posts e comentários")
    if a.youtube or a.yt_busca:
        saida["youtube"] = youtube(a.youtube, a.yt_busca, 120)
        grava()
        print("YouTube:", len(saida["youtube"]), "vídeos,", sum(len(v.get("comentarios", [])) for v in saida["youtube"]), "comentários")
    grava()
    print("ok", arq.relative_to(RAIZ))


if __name__ == "__main__":
    main()
