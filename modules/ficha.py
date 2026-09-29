"""
ficha.py - Consultas de la Ficha Integral 360° del Paciente y Cliente
=====================================================================
Extrae el expediente unificado: datos clínicos, consumos, citas y seguimientos.
"""
import pandas as pd
from modules import database


def obtener_mascota(conn, id_mascota: int):
    if not id_mascota:
        return None
    return conn.execute("SELECT * FROM mascotas WHERE id_mascota = ?", (id_mascota,)).fetchone()


def obtener_cliente(conn, id_cliente: int):
    if not id_cliente:
        return None
    return conn.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,)).fetchone()


def mascotas_del_cliente(conn, id_cliente: int) -> pd.DataFrame:
    return database.consultar(
        conn,
        "SELECT id_mascota, hc AS HC, nombre AS Mascota, especie AS Especie, raza AS Raza, "
        "sexo AS Sexo, esterilizacion AS Esterilizado, estado_relacion AS Estado "
        "FROM mascotas WHERE id_cliente = ? ORDER BY nombre",
        (id_cliente,)
    )


def atenciones_de_mascota(conn, id_mascota: int) -> pd.DataFrame:
    return database.consultar(
        conn,
        "SELECT fecha AS Fecha, tipo_atencion AS 'Tipo de Atención', motivo AS Motivo, "
        "diagnostico AS 'Diagnóstico', tratamiento AS 'Tratamiento', veterinario AS Veterinario "
        "FROM atenciones WHERE id_mascota = ? ORDER BY fecha DESC",
        (id_mascota,)
    )


def ventas_de_mascota(conn, id_mascota: int) -> pd.DataFrame:
    return database.consultar(
        conn,
        "SELECT fecha AS Fecha, comprobante AS Comprobante, item AS 'Ítem / Concepto', "
        "categoria AS 'Categoría', cantidad AS Cantidad, precio AS 'Precio Unitario', "
        "total AS Total FROM ventas WHERE id_mascota = ? ORDER BY fecha DESC",
        (id_mascota,)
    )


def ventas_cliente_sin_mascota(conn, id_cliente: int) -> pd.DataFrame:
    return database.consultar(
        conn,
        "SELECT fecha AS Fecha, comprobante AS Comprobante, item AS 'Ítem / Concepto', "
        "categoria AS 'Categoría', cantidad AS Cantidad, precio AS 'Precio Unitario', "
        "total AS Total FROM ventas WHERE id_cliente = ? AND id_mascota IS NULL ORDER BY fecha DESC",
        (id_cliente,)
    )


def citas_de_mascota_o_cliente(conn, id_mascota=None, id_cliente=None) -> pd.DataFrame:
    return database.consultar(
        conn,
        "SELECT fecha AS Fecha, tipo_evento AS 'Tipo de Cita', estado AS Estado, "
        "veterinario AS Profesional, motivo AS 'Detalles / Notas' "
        "FROM citas WHERE (id_mascota = ? AND ? IS NOT NULL) OR (id_cliente = ? AND ? IS NOT NULL) "
        "ORDER BY fecha DESC",
        (id_mascota, id_mascota, id_cliente, id_cliente)
    )
