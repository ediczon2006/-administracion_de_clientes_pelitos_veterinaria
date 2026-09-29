import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.database import init_db, conectar
from modules.importador import importar_archivo

init_db()

parent = BASE_DIR.parent
archivos = [
    ("clientes", parent / "Reporte de Clientes.xlsx"),
    ("mascotas", parent / "Reporte de Mascotas.xlsx"),
    ("historias", parent / "Reporte de Historias Clnicas - 01.09.2026 al 22.09.2026.xlsx"),
    ("ventas", parent / "Reporte de Comprobantes - 23.08.2026 al 22.09.2026.xlsx"),
    ("ventas", parent / "Reporte de ventas por items - 23.08.2026 al 22.09.2026.xlsx"),
]

for tipo, path in archivos:
    if path.exists():
        res = importar_archivo(str(path), tipo_manual=tipo, hacer_backup=False)
        print(f"{tipo.capitalize()}: {res['filas_insertadas']} insertados desde {path.name}")

conn = conectar()
print("\nTotales finales en pelitos_crm.db:")
print("Clientes:", conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0])
print("Mascotas:", conn.execute("SELECT COUNT(*) FROM mascotas").fetchone()[0])
print("Atenciones:", conn.execute("SELECT COUNT(*) FROM atenciones").fetchone()[0])
print("Ventas:", conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0])
