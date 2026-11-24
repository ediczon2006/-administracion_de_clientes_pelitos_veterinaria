"""
backup.py - Copias de Seguridad y Respaldo Automático
=====================================================
Garantiza la protección integral de la base SQLite antes de cada operación.
"""
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3

from modules import config


def crear_backup(conn, motivo: str = "manual") -> Path:
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    motivo_seguro = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in (motivo or "manual"))
    nombre = f"backup_pelitos_{marca}_{motivo_seguro}.db"
    destino = config.BACKUP_DIR / nombre

    # Copia transaccional nativa de SQLite (segura incluso en modo WAL)
    respaldo_db = sqlite3.connect(str(destino))
    try:
        with respaldo_db:
            conn.backup(respaldo_db)
    finally:
        respaldo_db.close()

    # Poda de copias antiguas automáticas
    if config.MAX_BACKUPS_AUTOMATICOS > 0 and motivo_seguro.startswith("antes_importar"):
        copias = sorted(config.BACKUP_DIR.glob("backup_pelitos_*_antes_importar*.db"))
        exceso = len(copias) - config.MAX_BACKUPS_AUTOMATICOS
        for c in copias[:max(0, exceso)]:
            c.unlink(missing_ok=True)

    return destino


def listar_backups() -> list[dict]:
    """Lista copias de seguridad disponibles con metadatos estructurados."""
    resultados = []
    for p in sorted(config.BACKUP_DIR.glob("backup_pelitos_*.db"), reverse=True):
        try:
            st_info = p.stat()
            resultados.append({
                "nombre": p.name,
                "ruta": p,
                "fecha": datetime.fromtimestamp(st_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "tamano_bytes": st_info.st_size,
            })
        except OSError:
            continue
    return resultados


def restaurar_backup(conn, ruta_backup: Path | str) -> Path:
    """Restaura una copia de seguridad verificada dentro de BACKUP_DIR."""
    ruta = Path(ruta_backup).resolve()
    backup_root = config.BACKUP_DIR.resolve()
    if backup_root not in ruta.parents or not ruta.exists():
        raise FileNotFoundError(f"Archivo de copia no válido o no encontrado: {ruta_backup}")

    # Guardar copia de seguridad preventiva antes de restaurar
    preventivo = crear_backup(conn, "antes_de_restaurar")
    conn.close()

    # Limpiar archivos WAL/SHM previos para evitar inconsistencias tras sobrescribir
    for sufijo in ("-wal", "-shm"):
        sidecar = Path(f"{config.DB_PATH}{sufijo}")
        sidecar.unlink(missing_ok=True)

    shutil.copy2(ruta, config.DB_PATH)
    return preventivo
