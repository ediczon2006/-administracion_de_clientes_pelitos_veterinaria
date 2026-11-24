"""
relaciones.py - Motor de Vinculación y Coincidencias 360°
=========================================================
Relaciona automáticamente clientes, mascotas, atenciones, ventas y citas.
"""
from collections import defaultdict
from datetime import datetime

from modules import config
from modules.database import transaccion
from modules.normalizacion import normalizar_documento, normalizar_telefono, normalizar_texto

_COL_ID_POR_TABLA = {
    "mascotas": "id_mascota",
    "atenciones": "id_atencion",
    "ventas": "id_venta",
    "citas": "id_cita",
}


def recalcular(conn) -> dict:
    """Recalcula relaciones automáticas preservando asignaciones manuales (con índices en memoria)."""
    resultados = {"mascotas": {}, "atenciones": {}, "ventas": {}, "citas": {}, "clientes": {}}

    # Precargar índices de clientes en memoria (elimina consultas N+1)
    cli_por_doc = {}
    cli_por_cel = defaultdict(list)
    cli_por_nom = defaultdict(list)
    for c in conn.execute("SELECT id_cliente, nombre, documento_norm, celular_norm, nombre_norm FROM clientes").fetchall():
        info = (c["id_cliente"], c["nombre"])
        if c["documento_norm"]:
            cli_por_doc[c["documento_norm"]] = info
        if c["celular_norm"]:
            cli_por_cel[c["celular_norm"]].append(info)
        if c["nombre_norm"]:
            cli_por_nom[c["nombre_norm"]].append(info)

    with transaccion(conn):
        # 1. Mascotas -> Clientes
        mascotas_updates = []
        mas_por_hc = {}
        for m in conn.execute("""
            SELECT id_mascota, hc_norm, nombre, nombre_norm, propietario_documento,
                   propietario_nombre, propietario_celular, id_cliente, estado_relacion
            FROM mascotas
        """).fetchall():
            if m["estado_relacion"] == config.MANUAL:
                if m["hc_norm"]:
                    mas_por_hc[m["hc_norm"]] = (m["id_mascota"], m["id_cliente"], m["nombre"])
                continue

            id_m = m["id_mascota"]
            doc_raw = m["propietario_documento"]
            nom_raw = m["propietario_nombre"]
            cel_raw = m["propietario_celular"]

            cliente = None
            estado = config.SIN
            detalle = "Sin datos de propietario en el reporte de mascotas."

            if doc_raw:
                doc_norm, _, valido, _ = normalizar_documento(doc_raw)
                if valido and doc_norm in cli_por_doc:
                    cid, cnom = cli_por_doc[doc_norm]
                    cliente = cid
                    estado = config.SEGURA
                    detalle = f"Coincidencia exacta por documento {doc_norm} ({cnom})."

            if not cliente and cel_raw:
                cel_norm, valido = normalizar_telefono(cel_raw)
                if valido:
                    candidatos = cli_por_cel.get(cel_norm, [])
                    if len(candidatos) == 1:
                        cliente = candidatos[0][0]
                        estado = config.SEGURA
                        detalle = f"Coincidencia exacta por teléfono {cel_norm} ({candidatos[0][1]})."
                    elif len(candidatos) > 1:
                        estado = config.REVISION
                        detalle = f"Teléfono {cel_norm} compartido por {len(candidatos)} clientes."

            if not cliente and nom_raw:
                nom_norm = normalizar_texto(nom_raw)
                candidatos = cli_por_nom.get(nom_norm, [])
                if len(candidatos) == 1:
                    cliente = candidatos[0][0]
                    estado = config.PROBABLE
                    detalle = f"Coincidencia por nombre completo '{nom_raw}'."
                elif len(candidatos) > 1:
                    estado = config.REVISION
                    detalle = f"Nombre '{nom_raw}' coincide con {len(candidatos)} clientes homónimos."

            mascotas_updates.append((cliente, estado, detalle, id_m))
            if m["hc_norm"]:
                mas_por_hc[m["hc_norm"]] = (id_m, cliente, m["nombre"])
            resultados["mascotas"][estado] = resultados["mascotas"].get(estado, 0) + 1

        if mascotas_updates:
            conn.executemany(
                "UPDATE mascotas SET id_cliente = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_mascota = ?",
                mascotas_updates,
            )

        # 2. Atenciones -> Mascotas
        atenciones_updates = []
        for a in conn.execute("SELECT id_atencion, hc_norm, paciente, estado_relacion FROM atenciones").fetchall():
            if a["estado_relacion"] == config.MANUAL:
                continue
            id_a = a["id_atencion"]
            hc = a["hc_norm"]
            mascota = None
            estado = config.SIN
            detalle = "Sin número de historia clínica válido."

            if hc:
                m_info = mas_por_hc.get(hc)
                if m_info:
                    mascota = m_info[0]
                    estado = config.SEGURA
                    detalle = f"Vinculado a paciente '{m_info[2]}' por HC {hc}."
                else:
                    estado = config.REVISION
                    detalle = f"Historia Clínica {hc} no encontrada en padrón de mascotas."

            atenciones_updates.append((mascota, estado, detalle, id_a))
            resultados["atenciones"][estado] = resultados["atenciones"].get(estado, 0) + 1

        if atenciones_updates:
            conn.executemany(
                "UPDATE atenciones SET id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_atencion = ?",
                atenciones_updates,
            )

        # 3. Ventas -> Clientes y Mascotas
        ventas_updates = []
        for v in conn.execute(
            "SELECT id_venta, cliente_documento, cliente_nombre, hc_norm, estado_relacion FROM ventas"
        ).fetchall():
            if v["estado_relacion"] == config.MANUAL:
                continue
            id_v = v["id_venta"]
            doc = v["cliente_documento"]
            nom = v["cliente_nombre"]
            hc = v["hc_norm"]

            id_cli, id_mas = None, None
            estado = config.SIN
            detalle = "Sin datos de cliente o paciente."

            if hc and hc in mas_por_hc:
                id_mas, id_cli, m_nom = mas_por_hc[hc]
                estado = config.SEGURA
                detalle = f"Vinculado por HC {hc} (Paciente: {m_nom})."

            if not id_cli and doc:
                doc_norm, _, valido, _ = normalizar_documento(doc)
                if valido and doc_norm in cli_por_doc:
                    id_cli, cnom = cli_por_doc[doc_norm]
                    estado = config.SEGURA if not id_mas else estado
                    detalle = f"Vinculado a cliente {cnom} por doc {doc_norm}."

            if not id_cli and nom:
                nom_norm = normalizar_texto(nom)
                candidatos = cli_por_nom.get(nom_norm, [])
                if len(candidatos) == 1:
                    id_cli = candidatos[0][0]
                    if not id_mas:
                        estado = config.PROBABLE
                        detalle = f"Vinculado a cliente {candidatos[0][1]} por nombre."
                elif len(candidatos) > 1 and not id_mas:
                    estado = config.REVISION
                    detalle = f"Nombre '{nom}' coincide con {len(candidatos)} clientes homónimos."

            ventas_updates.append((id_cli, id_mas, estado, detalle, id_v))
            resultados["ventas"][estado] = resultados["ventas"].get(estado, 0) + 1

        if ventas_updates:
            conn.executemany(
                "UPDATE ventas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_venta = ?",
                ventas_updates,
            )

        # 4. Citas -> Clientes y Mascotas
        citas_updates = []
        for c in conn.execute(
            "SELECT id_cita, cliente_documento, celular, hc_norm, estado_relacion FROM citas"
        ).fetchall():
            if c["estado_relacion"] == config.MANUAL:
                continue
            id_c = c["id_cita"]
            hc = c["hc_norm"]
            doc = c["cliente_documento"]
            cel = c["celular"]

            id_cli, id_mas = None, None
            estado = config.SIN
            detalle = "Sin datos vinculables."

            if hc and hc in mas_por_hc:
                id_mas, id_cli, m_nom = mas_por_hc[hc]
                estado = config.SEGURA
                detalle = f"Cita vinculada por HC {hc} a paciente {m_nom}."

            if not id_cli and doc:
                doc_norm, _, valido, _ = normalizar_documento(doc)
                if valido and doc_norm in cli_por_doc:
                    id_cli = cli_por_doc[doc_norm][0]
                    estado = config.SEGURA
                    detalle = f"Vinculada a cliente por documento {doc_norm}."

            if not id_cli and cel:
                cel_norm, valido = normalizar_telefono(cel)
                if valido:
                    candidatos = cli_por_cel.get(cel_norm, [])
                    if len(candidatos) == 1:
                        id_cli = candidatos[0][0]
                        estado = config.PROBABLE if not id_mas else estado
                        detalle = f"Vinculada por teléfono {cel_norm}."
                    elif len(candidatos) > 1 and not id_mas:
                        estado = config.REVISION
                        detalle = f"Teléfono {cel_norm} compartido por {len(candidatos)} clientes."

            citas_updates.append((id_cli, id_mas, estado, detalle, id_c))
            resultados["citas"][estado] = resultados["citas"].get(estado, 0) + 1

        if citas_updates:
            conn.executemany(
                "UPDATE citas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_cita = ?",
                citas_updates,
            )

    return resultados


def asignar_manual(conn, tabla: str, id_registro: int, responsable: str, id_cliente=None, id_mascota=None):
    if tabla not in _COL_ID_POR_TABLA:
        raise ValueError(f"Tabla no permitida para asignación manual: {tabla}")
    ahora_txt = datetime.now().strftime("%Y-%m-%d %H:%M")
    detalle = f"Asignación manual confirmada por {responsable or 'Manual'} el {ahora_txt}."

    with transaccion(conn):
        if tabla == "mascotas":
            conn.execute(
                "UPDATE mascotas SET id_cliente = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_mascota = ?",
                (id_cliente, config.MANUAL, detalle, id_registro),
            )
        elif tabla == "atenciones":
            conn.execute(
                "UPDATE atenciones SET id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_atencion = ?",
                (id_mascota, config.MANUAL, detalle, id_registro),
            )
        elif tabla == "ventas":
            conn.execute(
                "UPDATE ventas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_venta = ?",
                (id_cliente, id_mascota, config.MANUAL, detalle, id_registro),
            )
        elif tabla == "citas":
            conn.execute(
                "UPDATE citas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_cita = ?",
                (id_cliente, id_mascota, config.MANUAL, detalle, id_registro),
            )


def asignar_cliente_a_mascota(conn, id_mascota: int, id_cliente: int, responsable: str = "Manual"):
    """Atajo seguro para vincular una mascota con un cliente existente."""
    asignar_manual(conn, "mascotas", id_mascota, responsable=responsable, id_cliente=id_cliente)


def deshacer_manual(conn, tabla: str, id_registro: int):
    if tabla not in _COL_ID_POR_TABLA:
        raise ValueError(f"Tabla no permitida: {tabla}")
    col_id = _COL_ID_POR_TABLA[tabla]

    with transaccion(conn):
        if tabla == "mascotas":
            conn.execute(
                f"UPDATE mascotas SET id_cliente = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                (config.SIN, id_registro),
            )
        elif tabla == "atenciones":
            conn.execute(
                f"UPDATE atenciones SET id_mascota = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                (config.SIN, id_registro),
            )
        elif tabla == "ventas":
            conn.execute(
                f"UPDATE ventas SET id_cliente = NULL, id_mascota = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                (config.SIN, id_registro),
            )
        elif tabla == "citas":
            conn.execute(
                f"UPDATE citas SET id_cliente = NULL, id_mascota = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                (config.SIN, id_registro),
            )
    recalcular(conn)
