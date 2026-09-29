"""
backup.py - Copias de Seguridad y Respaldo Automático
=====================================================
Garantiza la protección integral de la base SQLite antes de cada operación.
"""
from datetime import datetime
import shutil
import sqlite3
from pathlib import Path
from modules import config


def crear_backup(conn, motivo: str = "manual") -> Path:
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"backup_pelitos_{marca}_{motivo}.db"
    destino = config.BACKUP_DIR / nombre

    # Copia transaccional nativa de SQLite
    respaldo_db = sqlite3.connect(str(destino))
    with respaldo_db:
        conn.backup(respaldo_db)
    respaldo_db.close()

    # Poda de copias antiguas automáticas
    if config.MAX_BACKUPS_AUTOMATICOS > 0 and motivo.startswith("antes_importar"):
        copias = sorted(config.BACKUP_DIR.glob("backup_pelitos_*_antes_importar*.db"))
        exceso = len(copias) - config.MAX_BACKUPS_AUTOMATICOS
        for c in copias[:max(0, exceso)]:
            c.unlink(missing_ok=True)

    return destino


def listar_backups() -> list:
    return sorted(config.BACKUP_DIR.glob("backup_pelitos_*.db"), reverse=True)


def restaurar_backup(conn, ruta_backup: Path):
    if not ruta_backup.exists():
        raise FileNotFoundError(f"Archivo de copia no encontrado: {ruta_backup}")
    # Guardar copia de seguridad preventiva antes de restaurar
    crear_backup(conn, "antes_de_restaurar")
    conn.close()
    shutil.copy2(ruta_backup, config.DB_PATH)
