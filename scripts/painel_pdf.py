"""PDF de um painel: todas as abas em sequência, cada uma em página nova, com subabas abertas.

Uso: python scripts/painel_pdf.py exemplo   → painel/exemplo.pdf
Monta uma cópia do painel só pra impressão (sem botões de aba) e imprime com o Edge ou o Chrome em modo headless.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from painel_lib import RAIZ  # noqa: E402

NAVEGADORES = [Path(p) for p in ("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "C:/Program Files/Google/Chrome/Application/chrome.exe",
                                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium")]
IMPRESSAO = """<style>
@page{size:A4;margin:12mm}
#tabs,.subabas,.fmt-ver{display:none!important}
#vista{animation:none!important}
.aba-pdf{break-before:page;font:500 11px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--cinza);margin:0 0 8px}
.aba-pdf:first-child{break-before:auto}
.folha{box-shadow:none!important}
.cartao,.achado,.cc,.pessoa,.anuncio,tr,.eixo{break-inside:avoid}
[data-painel]{margin-bottom:22px}
</style>
<script>
window.addEventListener("load", () => {
  const v = document.querySelector("#vista");
  v.innerHTML = ABAS.map(a => `<div class="aba-pdf">${a[1]}</div>` + a[2]()).join("");
  v.querySelectorAll("[data-painel]").forEach(p => p.hidden = false);
  v.querySelectorAll(".fmt-tab").forEach(t => t.hidden = false);
  try { reels(); } catch (e) {}
});
</script>
"""

sys.stdout.reconfigure(encoding="utf-8")
slug = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ("-h", "--help") else sys.exit(__doc__)
nav = next((n for n in NAVEGADORES if n.exists()), None) or sys.exit("Edge ou Chrome não encontrado")
h = (RAIZ / "painel" / f"{slug}.html").read_text(encoding="utf-8")
# a última linha do script abre a aba do endereço; trocamos pela montagem de impressão
h = h.replace("abrir(location.hash.slice(1));", "abrir('resumo');")
h = h.replace("</body>", IMPRESSAO + "</body>") if "</body>" in h else h + IMPRESSAO
pasta = Path(tempfile.mkdtemp(prefix="painel-pdf-"))
copia = pasta / f"{slug}.html"
copia.write_text(h, encoding="utf-8")
saida = RAIZ / "painel" / f"{slug}.pdf"
subprocess.run([str(nav), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=30000",
                f"--print-to-pdf={saida}", copia.as_uri()], check=True, timeout=300, capture_output=True)
shutil.rmtree(pasta, ignore_errors=True)
print("ok", saida.relative_to(RAIZ), round(saida.stat().st_size / 1e6, 1), "MB")
