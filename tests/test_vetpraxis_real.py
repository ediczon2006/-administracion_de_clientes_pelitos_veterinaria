from pathlib import Path
import pytest

from modules import config
from modules.database import get_db, init_db
from modules.validacion import detectar_tipo_reporte, leer_archivo_robusto
from modules.importador import importar_archivo

PARENT_DIR = Path(__file__).resolve().parent.parent.parent
ARCHIVOS_REALES = {
    "clientes": PARENT_DIR / "Reporte de Clientes.xlsx",
    "mascotas": PARENT_DIR / "Reporte de Mascotas.xlsx",
    "historias": PARENT_DIR / "Reporte de Historias Clnicas - 01.09.2026 al 22.09.2026.xlsx",
    "comprobantes": PARENT_DIR / "Reporte de Comprobantes - 23.08.2026 al 22.09.2026.xlsx",
    "ventas_items": PARENT_DIR / "Reporte de ventas por items - 23.08.2026 al 22.09.2026.xlsx",
}


@pytest.fixture(scope="module")
def setup_test_env(tmp_path_factory):
    """Aísla BD, originales, procesados y backups para no contaminar carpetas de producción."""
    base_tmp = tmp_path_factory.mktemp("vetpraxis_real_env")
    orig_dir = base_tmp / "originales"
    proc_dir = base_tmp / "procesados"
    bk_dir = base_tmp / "backup"
    for d in (orig_dir, proc_dir, bk_dir):
        d.mkdir(parents=True, exist_ok=True)

    prev = (config.DATA_ORIGINALES, config.DATA_PROCESADOS, config.BACKUP_DIR)
    config.DATA_ORIGINALES = orig_dir
    config.DATA_PROCESADOS = proc_dir
    config.BACKUP_DIR = bk_dir

    test_db = base_tmp / "test_pelitos.db"
    init_db(str(test_db))
    try:
        yield str(test_db)
    finally:
        config.DATA_ORIGINALES, config.DATA_PROCESADOS, config.BACKUP_DIR = prev


def test_deteccion_archivos_reales():
    for key, path in ARCHIVOS_REALES.items():
        if not path.exists():
            pytest.skip(f"Archivo real no encontrado: {path}")

        df, _ = leer_archivo_robusto(str(path))
        assert not df.empty, f"DF vacío para {key}"

        tipo_detectado, conf = detectar_tipo_reporte(df)
        assert conf > 0.35, f"Baja confianza en detección para {key}: {conf} ({tipo_detectado})"


def test_importacion_secuencial_reales(setup_test_env):
    db_path = setup_test_env
    if not any(p.exists() for p in ARCHIVOS_REALES.values()):
        pytest.skip("Archivos reales externos no disponibles en este entorno.")

    for key, tipo in (
        ("clientes", "clientes"),
        ("mascotas", "mascotas"),
        ("historias", "historias"),
        ("comprobantes", "ventas"),
        ("ventas_items", "ventas"),
    ):
        path = ARCHIVOS_REALES[key]
        if path.exists():
            res = importar_archivo(str(path), tipo_manual=tipo, db_path=db_path, hacer_backup=False)
            assert res["exito"], f"Error importando {key}: {res.get('errores')}"
            assert res["filas_insertadas"] > 0

    with get_db(db_path) as conn:
        cli_count = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        mas_count = conn.execute("SELECT COUNT(*) FROM mascotas").fetchone()[0]
        assert cli_count > 0
        assert mas_count > 0
