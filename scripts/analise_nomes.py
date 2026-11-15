"""Análise de nomes de marca: INPI, Registro.br e buscadores. Grava coletas/<slug>/nomes.json.

Uso: python scripts/analise_nomes.py <slug> "Marca 1" "Marca 2" ... [--setor "marketing"] [--pessoa "Fulana"]

O que sai, por marca:
- inpi: processos do INPI com o nome exato (número, data, marca, situação, titular, classe) e se está ativo.
  Busca anônima no pePI, sem login.
- dominios: .com.br (Registro.br) e .com (Verisign) pelo RDAP público: registrado ou livre, criação e validade.
  O titular não aparece (o Registro.br esconde pela LGPD).
- web: resultados de buscador (título, link, trecho) pra grafia exata, com o setor, com CNPJ e em inglês.
  A leitura (mesmo setor, outro setor, exterior) é feita depois, pelo Claude, em cima desses resultados.

Presença pública não é parecer de disponibilidade: o painel diz isso e quem decide registro é advogado de marcas.
"""
import argparse
import html as H
import http.cookiejar
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
PEPI = "https://busca.inpi.gov.br/pePI/"
INATIVO = ("extint", "arquivad", "indeferid", "cancelad", "nulidade", "renuncia", "renúncia")


def texto(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def inpi(marca):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", UA)]
    op.open(PEPI + "servlet/LoginController?action=login", timeout=30).read()
    dados = urllib.parse.urlencode({"buscaExata": "sim", "txt": "", "marca": marca, "classeInter": "", "registerPerPage": "100",
                                    "Action": "searchMarca", "tipoPesquisa": "BY_MARCA_CLASSIF_BASICA"}, encoding="latin-1").encode()
    bruto = op.open(PEPI + "servlet/MarcasServletController", dados, timeout=150).read()
    try:
        h = bruto.decode("utf-8")
    except UnicodeDecodeError:
        h = bruto.decode("latin-1")
    m = re.search(r"Foram encontrados\s*<b>?\s*(\d+)", h) or re.search(r"Foram encontrados\s*(\d+)", texto(h))
    procs = []
    for linha in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S):
        if "CodPedido" not in linha:
            continue
        c = [texto(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)]
        if len(c) < 8:
            continue
        sit = c[5]
        procs.append({"numero": c[0], "data": c[1], "marca": c[3], "situacao": sit, "titular": c[6], "classe": c[7],
                      "ativo": not any(p in sit.lower() for p in INATIVO)})
    if not m and not procs and "Nenhum resultado" not in h:
        raise RuntimeError("resposta do INPI sem lista nem 'Nenhum resultado' (sessão caiu?)")
    total = int(m.group(1)) if m else len(procs)
    return {"total": total, "processos": procs, "fonte": "busca.inpi.gov.br (pePI, busca exata)"}


def rdap(dominio):
    base = "https://rdap.registro.br/domain/" if dominio.endswith(".br") else "https://rdap.verisign.com/com/v1/domain/"
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(base + dominio, headers={"User-Agent": UA}), timeout=20).read())
    except urllib.error.HTTPError as e:
        return {"dominio": dominio, "registrado": False if e.code == 404 else None, "erro": None if e.code == 404 else f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"dominio": dominio, "registrado": None, "erro": str(e)[:80]}
    ev = {e["eventAction"]: e["eventDate"][:10] for e in j.get("events", [])}
    return {"dominio": dominio, "registrado": True, "criado": ev.get("registration"), "vence": ev.get("expiration"), "status": j.get("status")}


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def dominios(marca):
    base = re.sub(r"[^a-z0-9 ]", "", sem_acento(marca).lower()).split()
    nomes = {"".join(base), "-".join(base)} if len(base) > 1 else {"".join(base)}
    return [rdap(n + tld) for n in sorted(nomes) for tld in (".com.br", ".com")]


def busca(q):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q) + "&kl=br-pt"
    try:
        t = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        return {"q": q, "erro": str(e)[:80], "res": []}
    res = []
    for u, a, s in re.findall(r'class="result__a" href="(.*?)">(.*?)</a>.*?class="result__snippet".*?>(.*?)</a>', t, re.S):
        m = re.search(r"uddg=([^&]+)", u)
        res.append({"titulo": texto(a), "url": urllib.parse.unquote(m.group(1)) if m else u, "trecho": texto(s)})
    return {"q": q, "res": res, "erro": None if res else "sem resultado ou bloqueado"}


def web(marca, setor):
    qs = [f'"{marca}"', f'"{marca}" CNPJ', f'"{marca}" company']
    if setor:
        qs.insert(1, f'"{marca}" {setor}')
    out = []
    for q in qs:
        out.append(busca(q))
        time.sleep(8)  # o DuckDuckGo bloqueia busca em rajada
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("marcas", nargs="+")
    ap.add_argument("--setor", default="")
    ap.add_argument("--pessoa", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    saida = {"data": date.today().strftime("%d/%m/%Y"), "pessoa": a.pessoa, "setor": a.setor, "marcas": []}
    for marca in a.marcas:
        print("==", marca)
        for tentativa in (1, 2, 3):  # o pePI às vezes demora e corta a primeira
            try:
                i = inpi(marca)
                break
            except Exception as e:  # noqa: BLE001
                i = {"total": None, "processos": [], "erro": str(e)[:120]}
                time.sleep(10)
        print(f"   INPI: {i['total']} processos, {sum(p['ativo'] for p in i['processos'])} ativos")
        d = dominios(marca)
        print("   domínios:", ", ".join(f"{x['dominio']} {'ocupado' if x['registrado'] else 'livre' if x['registrado'] is False else '?'}" for x in d))
        w = web(marca, a.setor)
        print("   web:", sum(len(x["res"]) for x in w), "resultados")
        saida["marcas"].append({"nome": marca, "inpi": i, "dominios": d, "web": w})
    arq = RAIZ / "coletas" / a.slug / "nomes.json"
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", arq.relative_to(RAIZ))


if __name__ == "__main__":
    main()
