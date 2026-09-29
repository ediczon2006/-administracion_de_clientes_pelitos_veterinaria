"""
database.py - Conexión, Esquema y Consultas Centrales SQLite
=============================================================
Modelo relacional estructurado para unificar datos de VetPraxis y CRM.
"""
from contextlib import contextmanager
import re
import sqlite3
import pandas as pd

from modules import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS importaciones (
    id_importacion    INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_reporte      TEXT NOT NULL,
    archivo           TEXT NOT NULL,
    archivo_guardado  TEXT,
    hash_archivo      TEXT,
    fecha_importacion TEXT NOT NULL,
    registros_leidos  INTEGER DEFAULT 0,
    insertados        INTEGER DEFAULT 0,
    actualizados      INTEGER DEFAULT 0,
    duplicados        INTEGER DEFAULT 0,
    descartados       INTEGER DEFAULT 0,
    observaciones     TEXT
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente        INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_unica       TEXT UNIQUE NOT NULL,
    codigo_origen     TEXT,
    documento         TEXT,
    documento_norm    TEXT,
    tipo_documento    TEXT,
    documento_valido  INTEGER DEFAULT 0,
    nombre            TEXT,
    nombre_norm       TEXT,
    celular           TEXT,
    celular_norm      TEXT,
    email             TEXT,
    direccion         TEXT,
    fecha_registro    TEXT,
    estado_revision   TEXT,
    detalle_revision  TEXT,
    alerta            TEXT,
    id_importacion    INTEGER REFERENCES importaciones(id_importacion),
    fila_excel        INTEGER,
    actualizado_en    TEXT
);
CREATE INDEX IF NOT EXISTS ix_cli_doc ON clientes(documento_norm);
CREATE INDEX IF NOT EXISTS ix_cli_cel ON clientes(celular_norm);
CREATE INDEX IF NOT EXISTS ix_cli_nom ON clientes(nombre_norm);

CREATE TABLE IF NOT EXISTS mascotas (
    id_mascota            INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_unica           TEXT UNIQUE NOT NULL,
    hc                    TEXT,
    hc_norm               TEXT,
    id_cliente            INTEGER REFERENCES clientes(id_cliente),
    nombre                TEXT,
    nombre_norm           TEXT,
    especie               TEXT,
    raza                  TEXT,
    sexo                  TEXT,
    fecha_nacimiento      TEXT,
    esterilizacion        TEXT,
    propietario_documento TEXT,
    propietario_nombre    TEXT,
    propietario_celular   TEXT,
    estado_relacion       TEXT,
    detalle_relacion      TEXT,
    alerta                TEXT,
    id_importacion        INTEGER REFERENCES importaciones(id_importacion),
    fila_excel            INTEGER,
    actualizado_en        TEXT
);
CREATE INDEX IF NOT EXISTS ix_mas_hc ON mascotas(hc_norm);
CREATE INDEX IF NOT EXISTS ix_mas_cli ON mascotas(id_cliente);

CREATE TABLE IF NOT EXISTS atenciones (
    id_atencion       INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_unica       TEXT UNIQUE NOT NULL,
    hc                TEXT,
    hc_norm           TEXT,
    id_mascota        INTEGER REFERENCES mascotas(id_mascota),
    fecha             TEXT,
    fecha_original    TEXT,
    tipo_atencion     TEXT,
    paciente          TEXT,
    motivo            TEXT,
    diagnostico       TEXT,
    tratamiento       TEXT,
    veterinario       TEXT,
    estado_relacion   TEXT,
    detalle_relacion  TEXT,
    id_importacion    INTEGER REFERENCES importaciones(id_importacion),
    fila_excel        INTEGER
);
CREATE INDEX IF NOT EXISTS ix_ate_hc ON atenciones(hc_norm);
CREATE INDEX IF NOT EXISTS ix_ate_mas ON atenciones(id_mascota);

CREATE TABLE IF NOT EXISTS ventas (
    id_venta          INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_unica       TEXT UNIQUE NOT NULL,
    fecha             TEXT,
    fecha_original    TEXT,
    comprobante       TEXT,
    id_cliente        INTEGER REFERENCES clientes(id_cliente),
    cliente_documento TEXT,
    cliente_nombre    TEXT,
    hc                TEXT,
    hc_norm           TEXT,
    id_mascota        INTEGER REFERENCES mascotas(id_mascota),
    mascota           TEXT,
    categoria         TEXT,
    item              TEXT,
    cantidad          REAL,
    precio            REAL,
    total             REAL,
    estado_relacion   TEXT,
    detalle_relacion  TEXT,
    id_importacion    INTEGER REFERENCES importaciones(id_importacion),
    fila_excel        INTEGER
);
CREATE INDEX IF NOT EXISTS ix_ven_hc ON ventas(hc_norm);
CREATE INDEX IF NOT EXISTS ix_ven_mas ON ventas(id_mascota);
CREATE INDEX IF NOT EXISTS ix_ven_cli ON ventas(id_cliente);

CREATE TABLE IF NOT EXISTS citas (
    id_cita           INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_unica       TEXT UNIQUE NOT NULL,
    fecha             TEXT,
    fecha_original    TEXT,
    id_cliente        INTEGER REFERENCES clientes(id_cliente),
    cliente_nombre    TEXT,
    cliente_documento TEXT,
    celular           TEXT,
    id_mascota        INTEGER REFERENCES mascotas(id_mascota),
    paciente          TEXT,
    hc                TEXT,
    hc_norm           TEXT,
    tipo_evento       TEXT,
    estado            TEXT,
    veterinario       TEXT,
    motivo            TEXT,
    estado_relacion   TEXT,
    detalle_relacion  TEXT,
    id_importacion    INTEGER REFERENCES importaciones(id_importacion),
    fila_excel        INTEGER
);
CREATE INDEX IF NOT EXISTS ix_cit_hc ON citas(hc_norm);
CREATE INDEX IF NOT EXISTS ix_cit_cli ON citas(id_cliente);

CREATE TABLE IF NOT EXISTS seguimientos (
    id_seguimiento    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente        INTEGER REFERENCES clientes(id_cliente),
    id_mascota        INTEGER REFERENCES mascotas(id_mascota),
    hc                TEXT,
    motivo            TEXT NOT NULL,
    fecha             TEXT NOT NULL,
    responsable       TEXT,
    estado            TEXT NOT NULL,
    resultado         TEXT,
    proxima_accion    TEXT,
    proxima_fecha     TEXT,
    observaciones     TEXT,
    creado_en         TEXT,
    actualizado_en    TEXT
);

CREATE TABLE IF NOT EXISTS seguimiento_historial (
    id_historial      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_seguimiento    INTEGER NOT NULL REFERENCES seguimientos(id_seguimiento),
    fecha_hora        TEXT NOT NULL,
    estado_anterior   TEXT,
    estado_nuevo      TEXT NOT NULL,
    resultado         TEXT,
    usuario           TEXT,
    nota              TEXT
);
"""

TABLAS_VALIDAS = {
    "importaciones", "clientes", "mascotas", "atenciones", "ventas",
    "citas", "seguimientos", "seguimiento_historial"
}


def conectar(ruta=None) -> sqlite3.Connection:
    """Abre o crea la base SQLite con soporte concurrente y funciones nativas."""
    conn = sqlite3.connect(str(ruta or config.DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    
    from modules.normalizacion import normalizar_texto
    conn.create_function("NORM", 1, normalizar_texto)
    conn.create_function("DIGITOS", 1, lambda v: re.sub(r"\D", "", str(v)) if v is not None else None)
    conn.executescript(ESQUEMA)
    return conn


def init_db(ruta=None):
    """Inicializa la base de datos asegurando esquema e índices."""
    conn = conectar(ruta)
    conn.close()
    return True


@contextmanager
def get_db(ruta=None):
    """Context manager para obtener y cerrar conexión SQLite con commit automático."""
    conn = conectar(ruta)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def transaccion(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def consultar(conn, sql: str, params=()) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def contar(conn, tabla: str, where: str = "", params=()) -> int:
    if tabla not in TABLAS_VALIDAS:
        raise ValueError(f"Tabla no autorizada: {tabla}")
    if where:
        return conn.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {where}", params).fetchone()[0]
    return conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]

