"""Resume coletas/<slug>/reels.json: por perfil, quantos reels, mediana e maior view, chamadas pra ação
(palavra-chave de comentário, link na bio, direct) e os mais vistos. Toda conta sai daqui, não da IA.

Uso: python scripts/resumo_reels.py <slug> <@perfil> [...]   → grava coletas/<slug>/reels-resumo.json
"""
import json
import re
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PALAVRA = re.compile(r"(?i:comenta|comente|digite|escreva|comentar)\s+(?i:aqui\s+)?(?i:a palavra\s+)?[\"“']?([A-ZÀ-Ú]{3,})\b")
BIO = re.compile(r"link (?:na|da) bio|link no perfil", re.I)
DIRECT = re.compile(r"\bdirect\b|\bdm\b|me chama", re.I)


def views(i: dict) -> int:
    return i.get("videoPlayCount") or i.get("videoViewCount") or 0


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    slug, perfis = sys.argv[1], [p.lstrip("@") for p in sys.argv[2:]]
    R = json.loads((RAIZ / "coletas" / slug / "reels.json").read_text(encoding="utf-8"))
    saida = {}
    for h in perfis:
        it = [i for i in R if (i.get("ownerUsername") or "").lower() == h.lower()]
        colab = [i for i in R if (i.get("ownerUsername") or "").lower() != h.lower()
                 and h.lower() in json.dumps(i.get("coauthorProducers") or i.get("taggedUsers") or "").lower()]
        v = [views(i) for i in it]
        caps = [i.get("caption") or "" for i in it]
        palavras = [m.group(1).upper() for c in caps for m in [PALAVRA.search(c)] if m]
        top = sorted(it, key=lambda i: -views(i))[:6]
        saida[h] = {
            "reels": len(it), "de": min((i.get("timestamp", "")[:10] for i in it), default=""),
            "ate": max((i.get("timestamp", "")[:10] for i in it), default=""),
            "mediana": int(statistics.median(v)) if v else 0, "maior": max(v, default=0), "soma": sum(v),
            "likes_med": int(statistics.median([i.get("likesCount") or 0 for i in it])) if it else 0,
            "coment_med": int(statistics.median([i.get("commentsCount") or 0 for i in it])) if it else 0,
            "dur_med": round(statistics.median([i.get("videoDuration") or 0 for i in it]), 1) if it else 0,
            "com_palavra": len(palavras), "palavras": sorted(set(palavras)),
            "com_bio": sum(bool(BIO.search(c)) for c in caps), "com_direct": sum(bool(DIRECT.search(c)) for c in caps),
            "colabs": len(colab),
            "top": [{"views": views(i), "data": i.get("timestamp", "")[:10], "dur": i.get("videoDuration"),
                     "likes": i.get("likesCount"), "coment": i.get("commentsCount"), "url": i.get("url"),
                     "capa": i.get("displayUrl"), "legenda": (i.get("caption") or "").replace("\n", " ")[:400]} for i in top],
        }
    (RAIZ / "coletas" / slug / "reels-resumo.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    for h, s in saida.items():
        print(f"## @{h}: {s['reels']} reels ({s['de']} a {s['ate']}) · mediana {s['mediana']:,} · maior {s['maior']:,} · "
              f"palavra {s['com_palavra']} {s['palavras'][:6]} · bio {s['com_bio']} · direct {s['com_direct']} · dur {s['dur_med']}s")
        for t in s["top"][:4]:
            print(f"   {t['views']:>9,} {t['data']} {t['dur']}s | {t['legenda'][:140]}")


if __name__ == "__main__":
    main()
