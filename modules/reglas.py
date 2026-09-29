"""
reglas.py - Protocolos Médicos Preventivos y Fidelización
=========================================================
Estructura transparente donde cada protocolo preventivo requiere aprobación
médica veterinaria antes de generar tareas operativas.
"""
from datetime import date, timedelta
import json
import pandas as pd
from modules import config, database


def cargar_reglas() -> list:
    if not config.REGLAS_PATH.exists():
        return []
    try:
        return json.loads(config.REGLAS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def regla_aplicable(r: dict) -> bool:
    return bool(r.get("activa") and r.get("intervalo_dias") and r.get("aprobado_por"))


def candidatos(conn, regla: dict) -> pd.DataFrame:
    if not regla_aplicable(regla):
        return pd.DataFrame()

    dias = regla["intervalo_dias"]
    tol = regla.get("tolerancia_previa_dias", 0)
    fecha_limite = (date.today() - timedelta(days=dias - tol)).isoformat()

    if regla["origen"] == "atenciones":
        sql = """
            SELECT m.id_mascota, m.hc AS HC, m.nombre AS Mascota,
                   COALESCE(c.nombre, m.propietario_nombre, '—') AS Tutor,
                   COALESCE(c.celular, m.propietario_celular, '—') AS Celular,
                   MAX(a.fecha) AS 'Última Atención',
                   a.tipo_atencion AS 'Último Servicio'
            FROM atenciones a
            JOIN mascotas m ON m.id_mascota = a.id_mascota
            LEFT JOIN clientes c ON c.id_cliente = m.id_cliente
            WHERE a.tipo_atencion LIKE ?
            GROUP BY m.id_mascota
            HAVING MAX(a.fecha) <= ?
            ORDER BY MAX(a.fecha) ASC LIMIT 100
        """
        return database.consultar(conn, sql, (f"%{regla['criterio_tipo']}%", fecha_limite))

    return pd.DataFrame()
