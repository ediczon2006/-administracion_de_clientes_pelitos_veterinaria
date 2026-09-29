"""
dashboard.py - Panel de Control Ejecutivo, KPIs y Auditoría Transparente
========================================================================
Cálculo de métricas de calidad de datos, fidelización y consultas SQL auditables.
"""
import pandas as pd
from modules import config, database


def calcular(conn) -> list:
    abiertos = ",".join(f"'{e}'" for e in config.ESTADOS_ABIERTOS)
    return [
        {
            "id": "kpi_clientes", "grupo": "datos", "nombre": "Clientes Registrados",
            "valor": database.contar(conn, "clientes"), "fuente": "Tabla 'clientes'",
            "explicacion": "Total de clientes importados en el padrón.",
            "sql_conteo": "SELECT COUNT(*) FROM clientes",
            "sql_detalle": "SELECT id_cliente, documento, nombre, celular, direccion FROM clientes ORDER BY nombre"
        },
        {
            "id": "kpi_mascotas", "grupo": "datos", "nombre": "Pacientes / Mascotas",
            "valor": database.contar(conn, "mascotas"), "fuente": "Tabla 'mascotas'",
            "explicacion": "Total de historias clínicas registradas en el sistema.",
            "sql_conteo": "SELECT COUNT(*) FROM mascotas",
            "sql_detalle": "SELECT hc, nombre, especie, raza, propietario_nombre FROM mascotas ORDER BY nombre"
        },
        {
            "id": "kpi_atenciones", "grupo": "datos", "nombre": "Atenciones Clínicas",
            "valor": database.contar(conn, "atenciones"), "fuente": "Tabla 'atenciones'",
            "explicacion": "Consultas, vacunas, controles y cirugías realizadas.",
            "sql_conteo": "SELECT COUNT(*) FROM atenciones",
            "sql_detalle": "SELECT fecha, hc, paciente, tipo_atencion, diagnostico FROM atenciones ORDER BY fecha DESC"
        },
        {
            "id": "kpi_ventas", "grupo": "datos", "nombre": "Registros de Venta",
            "valor": database.contar(conn, "ventas"), "fuente": "Tabla 'ventas'",
            "explicacion": "Comprobantes y líneas de venta registradas.",
            "sql_conteo": "SELECT COUNT(*) FROM ventas",
            "sql_detalle": "SELECT fecha, comprobante, item, total, cliente_nombre FROM ventas ORDER BY fecha DESC"
        },
        {
            "id": "kpi_citas", "grupo": "datos", "nombre": "Citas en Agenda (VetPraxis)",
            "valor": database.contar(conn, "citas"), "fuente": "Tabla 'citas'",
            "explicacion": "Citas y eventos sincronizados de la agenda de VetPraxis.",
            "sql_conteo": "SELECT COUNT(*) FROM citas",
            "sql_detalle": "SELECT fecha, cliente_nombre, paciente, tipo_evento, estado FROM citas ORDER BY fecha DESC"
        },
        {
            "id": "kpi_seg_abiertos", "grupo": "seguimiento", "nombre": "Seguimientos Activos",
            "valor": database.contar(conn, "seguimientos", f"estado IN ({abiertos})"),
            "fuente": "Tabla 'seguimientos'",
            "explicacion": f"Casos pendientes o en gestión activa ({', '.join(config.ESTADOS_ABIERTOS)}).",
            "sql_conteo": f"SELECT COUNT(*) FROM seguimientos WHERE estado IN ({abiertos})",
            "sql_detalle": f"SELECT id_seguimiento, fecha, motivo, estado, responsable FROM seguimientos WHERE estado IN ({abiertos})"
        },
        {
            "id": "kpi_seg_reactivados", "grupo": "seguimiento", "nombre": "Pacientes Reactivados",
            "valor": database.contar(conn, "seguimientos", "estado = 'Reactivado'"),
            "fuente": "Tabla 'seguimientos'",
            "explicacion": config.CRITERIO_REACTIVADO,
            "sql_conteo": "SELECT COUNT(*) FROM seguimientos WHERE estado = 'Reactivado'",
            "sql_detalle": "SELECT id_seguimiento, fecha, motivo, resultado, responsable FROM seguimientos WHERE estado = 'Reactivado'"
        },
    ]


def por_grupo(indicadores: list, grupo: str) -> list:
    return [i for i in indicadores if i["grupo"] == grupo]


def detalle(conn, ind: dict) -> pd.DataFrame:
    return database.consultar(conn, ind["sql_detalle"])


def calidad_relaciones(conn) -> pd.DataFrame:
    return database.consultar(conn, """
        SELECT 
            'Mascotas con Dueño' AS Entidad,
            SUM(CASE WHEN estado_relacion IN ('COINCIDENCIA SEGURA', 'SEGURA (MANUAL)') THEN 1 ELSE 0 END) AS Seguras,
            SUM(CASE WHEN estado_relacion = 'COINCIDENCIA PROBABLE' THEN 1 ELSE 0 END) AS Probables,
            SUM(CASE WHEN estado_relacion IN ('REQUIERE REVISIÓN', 'SIN COINCIDENCIA') THEN 1 ELSE 0 END) AS Pendientes,
            COUNT(*) AS Total
        FROM mascotas
        UNION ALL
        SELECT 
            'Atenciones Clínicas',
            SUM(CASE WHEN estado_relacion IN ('COINCIDENCIA SEGURA', 'SEGURA (MANUAL)') THEN 1 ELSE 0 END),
            SUM(CASE WHEN estado_relacion = 'COINCIDENCIA PROBABLE' THEN 1 ELSE 0 END),
            SUM(CASE WHEN estado_relacion IN ('REQUIERE REVISIÓN', 'SIN COINCIDENCIA') THEN 1 ELSE 0 END),
            COUNT(*)
        FROM atenciones
        UNION ALL
        SELECT 
            'Ventas y Facturación',
            SUM(CASE WHEN estado_relacion IN ('COINCIDENCIA SEGURA', 'SEGURA (MANUAL)') THEN 1 ELSE 0 END),
            SUM(CASE WHEN estado_relacion = 'COINCIDENCIA PROBABLE' THEN 1 ELSE 0 END),
            SUM(CASE WHEN estado_relacion IN ('REQUIERE REVISIÓN', 'SIN COINCIDENCIA') THEN 1 ELSE 0 END),
            COUNT(*)
        FROM ventas
    """)


def seguimientos_por_estado(conn) -> pd.DataFrame:
    return database.consultar(conn, """
        SELECT estado AS Estado, COUNT(*) AS Cantidad
        FROM seguimientos
        GROUP BY estado
        ORDER BY Cantidad DESC
    """)
