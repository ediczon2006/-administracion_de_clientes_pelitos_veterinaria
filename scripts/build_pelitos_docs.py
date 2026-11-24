"""
build_pelitos_docs.py - Sincronizador de Logo Base64 para index.html
====================================================================
Actualiza la constante única `LOGO_PELITOS_DATA_URI` dentro de `index.html`
leyendo `assets/logo_pelitos.png`, evitando duplicar el código HTML/JS en Python.
"""
import base64
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logo_pelitos.png"
INDEX_PATH = BASE_DIR / "index.html"


def sincronizar_logo() -> int:
    if not LOGO_PATH.exists():
        raise FileNotFoundError(f"No se encontró el logo en {LOGO_PATH}")
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"No se encontró index.html en {INDEX_PATH}")

    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    data_uri = f"data:image/png;base64,{b64}"

    html = INDEX_PATH.read_text(encoding="utf-8")
    patron = re.compile(
        r"/\* LOGO_B64_START \*/\s*const LOGO_PELITOS_DATA_URI = \"[^\"]*\";\s*/\* LOGO_B64_END \*/",
        re.DOTALL,
    )
    if not patron.search(html):
        raise RuntimeError("No se encontraron los marcadores LOGO_B64_START / LOGO_B64_END en index.html")

    reemplazo = (
        "/* LOGO_B64_START */\n"
        f'const LOGO_PELITOS_DATA_URI = "{data_uri}";\n'
        "/* LOGO_B64_END */"
    )
    nuevo_html = patron.sub(lambda _: reemplazo, html, count=1)
    INDEX_PATH.write_text(nuevo_html, encoding="utf-8")
    return len(nuevo_html)


if __name__ == "__main__":
    tamano = sincronizar_logo()
    print(f"[OK] index.html actualizado con una única copia de logo_pelitos.png ({tamano:,} caracteres).")
