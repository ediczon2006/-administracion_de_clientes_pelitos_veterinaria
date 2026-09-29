"""
seguimientos.py - CRM de Fidelización, Contactos y Seguimientos Preventivos
===========================================================================
Gestiona tareas de contacto, llamadas, citas y auditoría de transiciones.
"""
from datetime import date, datetime
import pandas as pd
from modules import config, database


def ahora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def crear_seguimiento(conn, id_cliente, id_mascota, hc, motivo, responsable,
                      estado="Pendiente", resultado="", proxima_accion="Ninguna",
                      proxima_fecha=None, observaciones="") -> int:
    if motivo not in config.MOTIVOS_SEGUIMIENTO:
        raise ValueError(f"Motivo no válido: {motivo}")
    if estado not in config.ESTADOS_SEGUIMIENTO:
        raise ValueError(f"Estado no válido: {estado}")

    with database.transaccion(conn):
        cur = conn.execute("""
            INSERT INTO seguimientos (
                id_cliente, id_mascota, hc, motivo, fecha, responsable,
                estado, resultado, proxima_accion, proxima_fecha, observaciones,
                creado_en, actualizado_en
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_cliente, id_mascota, hc, motivo, date.today().isoformat(),
            responsable, estado, resultado, proxima_accion,
            str(proxima_fecha) if proxima_fecha else None, observaciones,
            ahora(), ahora()
        ))
        id_seg = cur.lastrowid
        conn.execute("""
            INSERT INTO seguimiento_historial (
                id_seguimiento, fecha_hora, estado_anterior, estado_nuevo,
                resultado, usuario, nota
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_seg, ahora(), None, estado, resultado, responsable, "Registro inicial del caso."))
        return id_seg


def cambiar_estado(conn, id_seguimiento: int, nuevo_estado: str, usuario: str,
                   resultado: str = "", proxima_accion: str = None,
                   proxima_fecha=None, nota: str = ""):
    if nuevo_estado not in config.ESTADOS_SEGUIMIENTO:
        raise ValueError(f"Estado no válido: {nuevo_estado}")

    actual = conn.execute("SELECT estado FROM seguimientos WHERE id_seguimiento = ?", (id_seguimiento,)).fetchone()
    if not actual:
        raise ValueError(f"Seguimiento #{id_seguimiento} no existe.")

    anterior = actual["estado"]
    with database.transaccion(conn):
        updates = ["estado = ?", "actualizado_en = ?"]
        params = [nuevo_estado, ahora()]
        if resultado:
            updates.append("resultado = ?")
            params.append(resultado)
        if proxima_accion:
            updates.append("proxima_accion = ?")
            params.append(proxima_accion)
        if proxima_fecha is not None:
            updates.append("proxima_fecha = ?")
            params.append(str(proxima_fecha) if proxima_fecha else None)

        params.append(id_seguimiento)
        conn.execute(f"UPDATE seguimientos SET {', '.join(updates)} WHERE id_seguimiento = ?", tuple(params))
        conn.execute("""
            INSERT INTO seguimiento_historial (
                id_seguimiento, fecha_hora, estado_anterior, estado_nuevo,
                resultado, usuario, nota
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_seguimiento, ahora(), anterior, nuevo_estado, resultado, usuario, nota))


def listar(conn, estados=None, responsable=None, solo_vencidos=False, id_mascota=None, id_cliente=None) -> pd.DataFrame:
    clausulas, params = [], []
    if estados:
        ph = ",".join("?" * len(estados))
        clausulas.append(f"s.estado IN ({ph})")
        params.extend(estados)
    if responsable:
        clausulas.append("s.responsable = ?")
        params.append(responsable)
    if solo_vencidos:
        clausulas.append("s.proxima_fecha < ? AND s.estado IN ('" + "','".join(config.ESTADOS_ABIERTOS) + "')")
        params.append(date.today().isoformat())
    if id_mascota:
        clausulas.append("s.id_mascota = ?")
        params.append(id_mascota)
    if id_cliente:
        clausulas.append("s.id_cliente = ?")
        params.append(id_cliente)

    where = f"WHERE {' AND '.join(clausulas)}" if clausulas else ""
    sql = f"""
        SELECT 
            s.id_seguimiento AS ID,
            s.fecha AS 'Fecha Registro',
            s.motivo AS Motivo,
            s.estado AS Estado,
            s.responsable AS Responsable,
            COALESCE(c.nombre, '—') AS Cliente,
            COALESCE(c.celular, m.propietario_celular, '—') AS Celular,
            COALESCE(m.nombre, '—') AS Mascota,
            COALESCE(s.hc, m.hc, '—') AS HC,
            s.proxima_accion AS 'Próxima Acción',
            s.proxima_fecha AS 'Próxima Fecha',
            s.resultado AS 'Última Gestión',
            s.id_cliente,
            s.id_mascota
        FROM seguimientos s
        LEFT JOIN clientes c ON c.id_cliente = s.id_cliente
        LEFT JOIN mascotas m ON m.id_mascota = s.id_mascota
        {where}
        ORDER BY s.proxima_fecha ASC NULLS LAST, s.id_seguimiento DESC
    """
    return database.consultar(conn, sql, params)


def historial(conn, id_seguimiento: int) -> pd.DataFrame:
    return database.consultar(
        conn,
        "SELECT fecha_hora AS 'Fecha y Hora', estado_anterior AS 'Estado Previo', "
        "estado_nuevo AS 'Estado Nuevo', resultado AS 'Detalle / Gestión', usuario AS Responsable, nota AS Nota "
        "FROM seguimiento_historial WHERE id_seguimiento = ? ORDER BY id_historial DESC",
        (id_seguimiento,)
    )
