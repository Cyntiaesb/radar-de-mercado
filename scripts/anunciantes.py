"""Lista os anunciantes de uma coleta de anúncios: quantos anúncios, quantos ativos, destino e um trecho do texto.
Serve pra triar concorrente novo (a pessoa decide quem entra).

Uso: python scripts/anunciantes.py <slug> [--min 1]   → imprime e grava coletas/<slug>/anunciantes.json
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def texto(i: dict) -> str:
    s = i.get("snapshot") or {}
    t = (s.get("body") or {}).get("text") if isinstance(s.get("body"), dict) else s.get("body")
    if not t or "{{" in str(t):
        cards = s.get("cards") or []
        t = (cards[0].get("body") if cards else "") or s.get("title") or ""
    return " ".join(str(t).split())


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    slug = sys.argv[1]
    minimo = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 1
    itens = json.loads((RAIZ / "coletas" / slug / "anuncios.json").read_text(encoding="utf-8"))
    pags = {}
    for i in itens:
        p = pags.setdefault(i.get("page_name") or "?", {"page_id": i.get("page_id"), "n": 0, "ativos": 0, "destinos": set(), "textos": []})
        p["n"] += 1
        p["ativos"] += bool(i.get("is_active"))
        link = (i.get("snapshot") or {}).get("link_url") or ""
        if link:
            p["destinos"].add(link.split("?")[0][:70])
        if len(p["textos"]) < 2:
            p["textos"].append(texto(i)[:160])
    saida = sorted(({"pagina": k, **v, "destinos": sorted(v["destinos"])[:3]} for k, v in pags.items() if v["n"] >= minimo),
                   key=lambda x: -x["n"])
    (RAIZ / "coletas" / slug / "anunciantes.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    for p in saida:
        print(f"{p['n']:>3} ({p['ativos']} ativos) | {p['pagina']} | {', '.join(p['destinos'])} | {p['textos'][0] if p['textos'] else ''}")


if __name__ == "__main__":
    main()
