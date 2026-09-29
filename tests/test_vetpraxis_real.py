import os
import pytest
from pathlib import Path
from modules.database import get_db, init_db
from modules.validacion import detectar_tipo_reporte, validar, leer_archivo_robusto
from modules.importador import importar_archivo
from modules.buscador import buscar

PARENT_DIR = Path(__file__).resolve().parent.parent.parent
ARCHIVOS_REALES = {
    "clientes": PARENT_DIR / "Reporte de Clientes.xlsx",
    "mascotas": PARENT_DIR / "Reporte de Mascotas.xlsx",
    "historias": PARENT_DIR / "Reporte de Historias Clnicas - 01.09.2026 al 22.09.2026.xlsx",
    "comprobantes": PARENT_DIR / "Reporte de Comprobantes - 23.08.2026 al 22.09.2026.xlsx",
    "ventas_items": PARENT_DIR / "Reporte de ventas por items - 23.08.2026 al 22.09.2026.xlsx",
}

@pytest.fixture(scope="session")
def setup_test_db(tmp_path_factory):
    test_db = tmp_path_factory.mktemp("db") / "test_pelitos.db"
    init_db(str(test_db))
    return str(test_db)

def test_deteccion_archivos_reales():
    for key, path in ARCHIVOS_REALES.items():
        if not path.exists():
            pytest.skip(f"Archivo real no encontrado: {path}")
        
        df, header_row = leer_archivo_robusto(str(path))
        assert not df.empty, f"DF vacío para {key}"
        
        tipo_detectado, conf = detectar_tipo_reporte(df)
        print(f"\n[Test] {key}: Detectado={tipo_detectado}, Confianza={conf:.2f}, Filas={len(df)}")
        assert conf > 0.35, f"Baja confianza en detección para {key}: {conf}"

def test_importacion_secuencial_reales(setup_test_db):
    db_path = setup_test_db
    
    # 1. Importar Clientes
    path_cli = ARCHIVOS_REALES["clientes"]
    if path_cli.exists():
        res = importar_archivo(str(path_cli), tipo_manual="clientes", db_path=db_path)
        assert res["exito"], f"Error importando clientes: {res.get('errores')}"
        assert res["filas_insertadas"] > 0
        print(f"\nClientes importados: {res['filas_insertadas']}")

    # 2. Importar Mascotas
    path_mas = ARCHIVOS_REALES["mascotas"]
    if path_mas.exists():
        res = importar_archivo(str(path_mas), tipo_manual="mascotas", db_path=db_path)
        assert res["exito"], f"Error importando mascotas: {res.get('errores')}"
        assert res["filas_insertadas"] > 0
        print(f"Mascotas importadas: {res['filas_insertadas']}")

    # 3. Importar Historias
    path_his = ARCHIVOS_REALES["historias"]
    if path_his.exists():
        res = importar_archivo(str(path_his), tipo_manual="historias", db_path=db_path)
        assert res["exito"], f"Error importando historias: {res.get('errores')}"
        assert res["filas_insertadas"] > 0
        print(f"Historias importadas: {res['filas_insertadas']}")

    # 4. Importar Comprobantes (Ventas)
    path_com = ARCHIVOS_REALES["comprobantes"]
    if path_com.exists():
        res = importar_archivo(str(path_com), tipo_manual="ventas", db_path=db_path)
        assert res["exito"], f"Error importando comprobantes: {res.get('errores')}"
        assert res["filas_insertadas"] > 0
        print(f"Comprobantes importados: {res['filas_insertadas']}")

    # 4b. Importar Ventas por Items
    path_itm = ARCHIVOS_REALES["ventas_items"]
    if path_itm.exists():
        res = importar_archivo(str(path_itm), tipo_manual="ventas", db_path=db_path)
        assert res["exito"], f"Error importando items de ventas: {res.get('errores')}"
        assert res["filas_insertadas"] > 0
        print(f"Items de venta importados: {res['filas_insertadas']}")

    # 5. Probar búsqueda

    with get_db(db_path) as conn:
        cli_count = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        mas_count = conn.execute("SELECT COUNT(*) FROM mascotas").fetchone()[0]
        atn_count = conn.execute("SELECT COUNT(*) FROM atenciones").fetchone()[0]
        vnt_count = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
        
        print(f"\nTotales en BD de prueba: Clientes={cli_count}, Mascotas={mas_count}, Atenciones={atn_count}, Ventas={vnt_count}")
        assert cli_count > 0
        assert mas_count > 0
