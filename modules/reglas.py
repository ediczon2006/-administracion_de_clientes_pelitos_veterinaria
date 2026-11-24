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


def candidatos(conn, regla: dict, ignorar_estado: bool = False) -> pd.DataFrame:
    if not ignorar_estado and not regla_aplicable(regla):
        return pd.DataFrame()
    if not regla.get("intervalo_dias"):
        return pd.DataFrame()

    dias = int(regla["intervalo_dias"])
    tol = int(regla.get("tolerancia_previa_dias", 0) or 0)
    fecha_limite = (date.today() - timedelta(days=max(0, dias - tol))).isoformat()
    criterio = str(regla.get("criterio_tipo") or "").strip()

    if regla.get("origen") == "atenciones":
        sql = """
            SELECT m.id_mascota, m.hc AS HC, m.nombre AS Mascota,
                   COALESCE(c.nombre, m.propietario_nombre, '—') AS Tutor,
                   COALESCE(c.celular, m.propietario_celular, '—') AS Celular,
                   MAX(a.fecha) AS 'Última Atención',
                   (
                       SELECT a2.tipo_atencion
                       FROM atenciones a2
                       WHERE a2.id_mascota = m.id_mascota AND a2.tipo_atencion LIKE ?
                       ORDER BY a2.fecha DESC, a2.id_atencion DESC
                       LIMIT 1
                   ) AS 'Último Servicio'
            FROM atenciones a
            JOIN mascotas m ON m.id_mascota = a.id_mascota
            LEFT JOIN clientes c ON c.id_cliente = m.id_cliente
            WHERE a.tipo_atencion LIKE ?
            GROUP BY m.id_mascota
            HAVING MAX(a.fecha) <= ?
            ORDER BY MAX(a.fecha) ASC LIMIT 100
        """
        patron = f"%{criterio}%"
        return database.consultar(conn, sql, (patron, patron, fecha_limite))

    if regla.get("origen") == "ventas":
        sql = """
            SELECT COALESCE(m.id_mascota, 0) AS id_mascota,
                   COALESCE(m.hc, v.hc, '—') AS HC,
                   COALESCE(m.nombre, v.mascota, '—') AS Mascota,
                   COALESCE(c.nombre, v.cliente_nombre, '—') AS Tutor,
                   COALESCE(c.celular, m.propietario_celular, '—') AS Celular,
                   MAX(v.fecha) AS 'Última Compra',
                   (
                       SELECT v2.item
                       FROM ventas v2
                       WHERE (
                           (v2.id_mascota IS NOT NULL AND v2.id_mascota = v.id_mascota)
                           OR (v2.id_mascota IS NULL AND v2.id_cliente IS NOT NULL AND v2.id_cliente = v.id_cliente)
                       )
                       AND (v2.categoria LIKE ? OR v2.item LIKE ?)
                       ORDER BY v2.fecha DESC, v2.id_venta DESC
                       LIMIT 1
                   ) AS 'Último Producto/Servicio'
            FROM ventas v
            LEFT JOIN mascotas m ON m.id_mascota = v.id_mascota
            LEFT JOIN clientes c ON c.id_cliente = COALESCE(v.id_cliente, m.id_cliente)
            WHERE (v.categoria LIKE ? OR v.item LIKE ?)
              AND (v.id_mascota IS NOT NULL OR v.id_cliente IS NOT NULL)
            GROUP BY COALESCE(v.id_mascota, -v.id_cliente)
            HAVING MAX(v.fecha) <= ?
            ORDER BY MAX(v.fecha) ASC LIMIT 100
        """
        patron = f"%{criterio}%"
        return database.consultar(conn, sql, (patron, patron, patron, patron, fecha_limite))

    return pd.DataFrame()
