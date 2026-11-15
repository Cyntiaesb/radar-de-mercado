"""Monta painel/<slug>.html a partir de especialistas/<slug>.py e do modelo em modelo/painel.html.

Uso: python scripts/monta_painel.py exemplo
O arquivo do especialista define TITULO, CABECALHO e D. Pra um especialista novo, copiar especialistas/_novo.py.
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from painel_lib import RAIZ, grava  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
slug = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ("-h", "--help") else sys.exit(__doc__)
arq = RAIZ / "especialistas" / f"{slug}.py"
if not arq.exists():
    sys.exit(f"não achei {arq.relative_to(RAIZ)}")
g = runpy.run_path(str(arq))
grava(slug, g["TITULO"], g["CABECALHO"], g["D"])
