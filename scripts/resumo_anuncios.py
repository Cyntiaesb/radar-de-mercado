"""Resume coletas/<slug>/anuncios.json: por página, anúncios no ar, dias no ar,
vencedores (+30 dias), criativos duplicados (base B), mais antigos (base C), copy parecida entre páginas (base A),
destinos, formatos e calendário de início por mês. Toda conta sai daqui, não da IA.

Uso: python scripts/resumo_anuncios.py <slug> "<página>" ["<página>" ...] [--hoje 2026-10-26]
Grava coletas/<slug>/anuncios-resumo.json.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def texto(i: dict) -> str:
    s = i.get("snapshot") or {}
    b = s.get("body")
    t = b.get("text") if isinstance(b, dict) else b
    if not t or "{{" in str(t):
        cards = s.get("cards") or []
        t = (cards[0].get("body") if cards else "") or s.get("title") or ""
    return " ".join(str(t).split())


def dia(ts) -> date | None:
    if ts in (None, ""):
        return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc).date()
    return date.fromisoformat(str(ts)[:10])


def abertura(t: str) -> str:
    return re.split(r"(?<=[.!?…])\s", t.lower(), maxsplit=1)[0][:60]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    slug = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    hoje = date.fromisoformat(sys.argv[sys.argv.index("--hoje") + 1]) if "--hoje" in sys.argv else date.today()
    paginas = [a for a in args if a != str(hoje)]
    itens = json.loads((RAIZ / "coletas" / slug / "anuncios.json").read_text(encoding="utf-8"))
    vistos, por = set(), defaultdict(list)
    for i in itens:
        if i.get("page_name") in paginas and i.get("ad_archive_id") not in vistos:
            vistos.add(i.get("ad_archive_id"))
            por[i["page_name"]].append(i)
    aberturas = defaultdict(set)
    saida = {}
    for p, ads in por.items():
        linhas = []
        for i in ads:
            ini, fim = dia(i.get("start_date")), dia(i.get("end_date"))
            ativo = bool(i.get("is_active"))
            dias = ((hoje if ativo else (fim or hoje)) - ini).days if ini else None
            s = i.get("snapshot") or {}
            t = texto(i)
            if t:
                aberturas[abertura(t)].add(p)
            img = None
            if s.get("videos"):
                img = s["videos"][0].get("video_preview_image_url")
            elif s.get("images"):
                img = s["images"][0].get("original_image_url")
            elif s.get("cards"):
                img = s["cards"][0].get("video_preview_image_url") or s["cards"][0].get("original_image_url")
            linhas.append({"id": i.get("ad_archive_id"), "ativo": ativo, "inicio": str(ini) if ini else None, "dias": dias,
                           "formato": s.get("display_format"), "copias": i.get("collation_count") or 1,
                           "destino": (s.get("link_url") or "").split("?")[0], "cta": s.get("cta_text") or s.get("cta_type"),
                           "titulo": s.get("title"), "texto": t[:600], "img": img})
        ativos = [l for l in linhas if l["ativo"]]
        meses = Counter(l["inicio"][:7] for l in linhas if l["inicio"])
        saida[p] = {
            "total": len(linhas), "ativos": len(ativos),
            "vencedores": sum(1 for l in ativos if (l["dias"] or 0) > 30),
            "mais_antigo_ativo": max((l["dias"] or 0 for l in ativos), default=0),
            "formatos": Counter(l["formato"] for l in ativos).most_common(),
            "destinos": Counter(re.sub(r"https?://(www\.)?", "", l["destino"]).rstrip("/") for l in ativos if l["destino"]).most_common(6),
            "duplicados": sorted(({"id": l["id"], "copias": l["copias"], "texto": l["texto"][:100]} for l in ativos if l["copias"] > 1),
                                 key=lambda x: -x["copias"])[:5],
            "meses": sorted(meses.items()),
            "top": sorted(ativos, key=lambda l: -(l["dias"] or 0))[:8],
        }
    comum = [{"abertura": a, "paginas": sorted(ps)} for a, ps in aberturas.items() if len(ps) > 1]
    saida["_base_a"] = comum
    (RAIZ / "coletas" / slug / "anuncios-resumo.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    for p, s in saida.items():
        if p.startswith("_"):
            continue
        print(f"## {p}: {s['total']} no histórico · {s['ativos']} ativos · {s['vencedores']} com +30 dias · mais antigo ativo {s['mais_antigo_ativo']} dias")
        print("   formatos", s["formatos"], "| destinos", s["destinos"][:4])
        print("   meses", s["meses"])
        for t in s["top"][:6]:
            print(f"   {t['dias']:>4}d {t['formato']} x{t['copias']} → {t['destino'][:50]} | {t['texto'][:150]}")
    print("BASE A (abertura igual entre páginas):", comum[:5])


if __name__ == "__main__":
    main()
