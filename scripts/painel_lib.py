"""Funções comuns aos painéis por especialista. Usadas pelos arquivos em especialistas/ e por monta_painel.py.

O modelo visual (abas, CSS, código) fica em modelo/painel.html e não tem texto de nicho nenhum:
tudo o que muda de um especialista pro outro vem do objeto D.
"""
import base64
import hashlib
import io
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COL = RAIZ / "coletas"
MODELO = RAIZ / "modelo" / "painel.html"

# Chaves que o modelo aceita sem: o código tem valor padrão ou esconde a seção.
OPCIONAIS = {"ads", "buscaYt", "grupos", "gruposTitulo", "nomes", "confianca", "limites", "errado", "fontes", "precosFormato"}
# Selo de confiança, veredito e tipo de fonte aceitos no painel.
SELOS = {"alta", "moderada", "baixa"}
VEREDITOS = {"Confirmada", "Em parte", "Divergente", "Sem lastro"}
TIPOS_FONTE = {"especialista", "concorrente", "checkout", "registro", "imprensa", "reclamacao", "rede", "coleta"}
OPCIONAIS_TXT = {"ytFora"}
# Palavra pedida no comentário do reel ("comenta QUERO").
PALAVRA = re.compile(r"(?i:comenta|comente|digite|escreva|comentar)\s+(?i:aqui\s+)?(?i:a palavra\s+)?[\"“']?([A-ZÀ-Ú]{3,})\b")


def ler(p):
    return json.loads((COL / p).read_text(encoding="utf-8"))


def capa(url, cache):
    """Baixa a capa, reduz pra 320px JPEG e guarda em cache (o link do Instagram expira em poucos dias)."""
    k = hashlib.sha1(url.split("?")[0].encode()).hexdigest()[:16]
    if k not in cache:
        from PIL import Image
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((320, 320))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=68)
        cache[k] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    return cache[k]


def reels_ig(slug, perfis, brutos, resumo):
    """perfis = [(handle, nome no painel, quantos reels mostrar)]. Devolve (reelsIG, perfisIG) prontos pro D.
    brutos = itens do reels.json (um ou mais arquivos somados); resumo = reels-resumo.json somados."""
    arq = COL / slug / "capas-cache.json"
    cache = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    reels, out = [], []
    for h, nome, n in perfis:
        meus = [i for i in brutos if i.get("ownerUsername") == h]
        for i in sorted(meus, key=lambda i: -(i.get("videoPlayCount") or 0))[:n]:
            leg = (i.get("caption") or "").strip()
            m = PALAVRA.search(leg)
            try:
                c = capa(i["displayUrl"], cache)
            except Exception as e:
                print("capa falhou", h, e)
                c = None
            reels.append({"de": nome, "h": h, "views": i.get("videoPlayCount") or 0, "data": i["timestamp"][:10], "dur": round(i.get("videoDuration") or 0),
                          "likes": i.get("likesCount") or 0, "coment": i.get("commentsCount") or 0, "url": i.get("url"),
                          "palavra": m.group(1).upper() if m else None, "legenda": leg.replace("\n", " ")[:280].replace("�", ""), "capa": c})
        r = resumo[h]
        out.append({"h": h, "nome": nome, "dias": len({i["timestamp"][:10] for i in meus}),
                    **{k: r[k] for k in ("reels", "de", "ate", "mediana", "maior", "coment_med", "com_palavra", "palavras", "com_direct")}})
    arq.write_text(json.dumps(cache), encoding="utf-8")
    return reels, out


def fichas(cartoes, linhas):
    """Ficha de cada anúncio, na ordem de anuncios-painel.json: [gancho, promessa, oferta, CTA, consciência, etapa, é lançamento?]."""
    assert len(cartoes) == len(linhas), f"{len(cartoes)} anúncios e {len(linhas)} fichas"
    return {a["id"]: dict(zip(["gancho", "promessa", "oferta", "cta", "consc", "etapa", "lanc"], f)) for a, f in zip(cartoes, linhas)}


def nomes(slug, leituras):
    """Junta coletas/<slug>/nomes.json (scripts/analise_nomes.py) com a leitura feita sobre os resultados.
    leituras = {marca: {"leitura": [título, texto], "ocorrencias": [[nome, o que faz, "mesmo"|"outro"|"exterior", começo do link]],
                        "examinar": [[título, por quê]]}}. O link da ocorrência é completado com o resultado de busca que começa igual."""
    bruto = ler(f"{slug}/nomes.json")
    marcas = []
    for m in bruto["marcas"]:
        links = [r["url"] for q in m["web"] for r in q["res"]]
        lt = leituras.get(m["nome"], {})
        oc = [[o[0], o[1], o[2], next((u for u in links if u.startswith(o[3])), o[3])] for o in lt.get("ocorrencias", [])]
        marcas.append({"nome": m["nome"], "inpi": m["inpi"], "dominios": m["dominios"], "leitura": lt.get("leitura"), "ocorrencias": oc, "examinar": lt.get("examinar", [])})
    return {"data": bruto["data"], "marcas": marcas}


def confere(D, modelo):
    """Lista as chaves que o modelo lê e o D não tem."""
    falta = [k for k in sorted(set(re.findall(r"\bD\.(\w+)", modelo))) if k not in D and k not in OPCIONAIS]
    falta += ["txt." + k for k in sorted(set(re.findall(r"D\.txt\.(\w+)", modelo))) if k not in D.get("txt", {}) and k not in OPCIONAIS_TXT]
    falta += ["cli." + k for k in sorted(set(re.findall(r"\bC\.(\w+)", modelo))) if k not in D.get("cli", {})]
    if not D.get("perfisIG"):
        falta.append("perfisIG (a aba de reels precisa do perfil do especialista: rodar coleta_reels.py e resumo_reels.py)")
    return falta + confere_estudo(D)


def confere_estudo(D):
    """Selo, veredito e tipo de fonte só aceitam os valores combinados; limites ou errado tem que existir."""
    erros = [] if D.get("limites") or D.get("errado") else ["limites (ou errado): o que o painel não sabe"]
    if D.get("confianca") and D["confianca"][0] not in SELOS:
        erros.append(f"confianca: selo {D['confianca'][0]!r} fora de {sorted(SELOS)}")
    erros += [f"achado {a[0]!r}: selo {a[2]!r}" for a in D.get("achados", []) if len(a) > 2 and a[2] not in SELOS]
    erros += [f"declarado {d[0]!r}: veredito {d[2]!r} fora de {sorted(VEREDITOS)}" for d in D.get("declarado", []) if len(d) > 2 and d[2] not in VEREDITOS]
    erros += [f"fonte {f[1]!r}: tipo {f[0]!r} fora de {sorted(TIPOS_FONTE)}" for f in D.get("fontes", []) if f[0] not in TIPOS_FONTE]
    return erros


def grava(slug, titulo, cabecalho, D):
    modelo = MODELO.read_text(encoding="utf-8")
    falta = confere(D, modelo)
    assert not falta, f"faltam no D: {falta}"
    # D["periodo"] (opcional) diz quando a coleta foi feita, ex.: "de 24 a 30/10/2026"; sem ele vale "em " + D["data"]
    selo = D.get("selo") or "Dados reais"  # no exemplo, "Dados fictícios"
    html = modelo.replace("{{TITULO}}", titulo).replace("{{CABECALHO}}", cabecalho).replace("{{COLETA}}", D.get("periodo") or "em " + D["data"]).replace("{{SELO}}", selo)
    html = html.replace("/*__D__*/", "const D = " + json.dumps(D, ensure_ascii=False, indent=1) + ";")
    destino = RAIZ / "painel" / f"{slug}.html"
    destino.write_text(html, encoding="utf-8")
    print("ok", destino.name, round(len(html) / 1024), "KB")
    if shutil.which("node"):
        subprocess.run(["node", str(RAIZ / "scripts" / "checa_painel.js"), str(destino)], check=True)
