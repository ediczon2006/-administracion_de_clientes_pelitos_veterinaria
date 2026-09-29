"""
relaciones.py - Motor de Vinculación y Coincidencias 360°
=========================================================
Relaciona automáticamente clientes, mascotas, atenciones, ventas y citas.
"""
import pandas as pd
from modules import config
from modules.normalizacion import normalizar_texto


def recalcular(conn) -> dict:
    """Recalcula las relaciones automáticas preservando las asignaciones manuales."""
    resultados = {"mascotas": {}, "atenciones": {}, "ventas": {}, "citas": {}, "clientes": {}}

    # 1. Mascotas -> Clientes
    cur = conn.execute("""
        SELECT id_mascota, hc_norm, nombre_norm, propietario_documento,
               propietario_nombre, propietario_celular, estado_relacion
        FROM mascotas
    """)
    for m in cur.fetchall():
        if m["estado_relacion"] == config.MANUAL:
            continue

        id_m = m["id_mascota"]
        doc_raw = m["propietario_documento"]
        nom_raw = m["propietario_nombre"]
        cel_raw = m["propietario_celular"]

        cliente = None
        estado = config.SIN
        detalle = "Sin datos de propietario en el reporte de mascotas."

        if doc_raw:
            from modules.normalizacion import normalizar_documento
            doc_norm, _, valido, _ = normalizar_documento(doc_raw)
            if valido:
                c = conn.execute("SELECT id_cliente, nombre FROM clientes WHERE documento_norm = ?", (doc_norm,)).fetchone()
                if c:
                    cliente = c["id_cliente"]
                    estado = config.SEGURA
                    detalle = f"Coincidencia exacta por documento {doc_norm} ({c['nombre']})."

        if not cliente and cel_raw:
            from modules.normalizacion import normalizar_telefono
            cel_norm, valido = normalizar_telefono(cel_raw)
            if valido:
                candidatos = conn.execute("SELECT id_cliente, nombre FROM clientes WHERE celular_norm = ?", (cel_norm,)).fetchall()
                if len(candidatos) == 1:
                    cliente = candidatos[0]["id_cliente"]
                    estado = config.SEGURA
                    detalle = f"Coincidencia exacta por teléfono {cel_norm} ({candidatos[0]['nombre']})."
                elif len(candidatos) > 1:
                    estado = config.REVISION
                    detalle = f"Teléfono {cel_norm} compartido por {len(candidatos)} clientes."

        if not cliente and nom_raw:
            nom_norm = normalizar_texto(nom_raw)
            candidatos = conn.execute("SELECT id_cliente, nombre FROM clientes WHERE nombre_norm = ?", (nom_norm,)).fetchall()
            if len(candidatos) == 1:
                cliente = candidatos[0]["id_cliente"]
                estado = config.PROBABLE
                detalle = f"Coincidencia por nombre completo '{nom_raw}'."
            elif len(candidatos) > 1:
                estado = config.REVISION
                detalle = f"Nombre '{nom_raw}' coincide con {len(candidatos)} clientes homónimos."

        conn.execute("""
            UPDATE mascotas SET id_cliente = ?, estado_relacion = ?, detalle_relacion = ?
            WHERE id_mascota = ?
        """, (cliente, estado, detalle, id_m))
        resultados["mascotas"][estado] = resultados["mascotas"].get(estado, 0) + 1

    # 2. Atenciones -> Mascotas
    cur = conn.execute("SELECT id_atencion, hc_norm, paciente, estado_relacion FROM atenciones")
    for a in cur.fetchall():
        if a["estado_relacion"] == config.MANUAL:
            continue
        id_a = a["id_atencion"]
        hc = a["hc_norm"]
        mascota = None
        estado = config.SIN
        detalle = "Sin número de historia clínica válido."

        if hc:
            m = conn.execute("SELECT id_mascota, nombre FROM mascotas WHERE hc_norm = ?", (hc,)).fetchone()
            if m:
                mascota = m["id_mascota"]
                estado = config.SEGURA
                detalle = f"Vinculado a paciente '{m['nombre']}' por HC {hc}."
            else:
                estado = config.REVISION
                detalle = f"Historia Clínica {hc} no encontrada en padrón de mascotas."

        conn.execute("""
            UPDATE atenciones SET id_mascota = ?, estado_relacion = ?, detalle_relacion = ?
            WHERE id_atencion = ?
        """, (mascota, estado, detalle, id_a))
        resultados["atenciones"][estado] = resultados["atenciones"].get(estado, 0) + 1

    # 3. Ventas -> Clientes y Mascotas
    cur = conn.execute("""
        SELECT id_venta, cliente_documento, cliente_nombre, hc_norm, estado_relacion
        FROM ventas
    """)
    for v in cur.fetchall():
        if v["estado_relacion"] == config.MANUAL:
            continue
        id_v = v["id_venta"]
        doc = v["cliente_documento"]
        nom = v["cliente_nombre"]
        hc = v["hc_norm"]

        id_cli, id_mas = None, None
        estado = config.SIN
        detalle = "Sin datos de cliente o paciente."

        if hc:
            m = conn.execute("SELECT id_mascota, id_cliente, nombre FROM mascotas WHERE hc_norm = ?", (hc,)).fetchone()
            if m:
                id_mas = m["id_mascota"]
                id_cli = m["id_cliente"]
                estado = config.SEGURA
                detalle = f"Vinculado por HC {hc} (Paciente: {m['nombre']})."

        if not id_cli and doc:
            from modules.normalizacion import normalizar_documento
            doc_norm, _, valido, _ = normalizar_documento(doc)
            if valido:
                c = conn.execute("SELECT id_cliente, nombre FROM clientes WHERE documento_norm = ?", (doc_norm,)).fetchone()
                if c:
                    id_cli = c["id_cliente"]
                    estado = config.SEGURA if not id_mas else estado
                    detalle = f"Vinculado a cliente {c['nombre']} por doc {doc_norm}."

        if not id_cli and nom:
            nom_norm = normalizar_texto(nom)
            c = conn.execute("SELECT id_cliente, nombre FROM clientes WHERE nombre_norm = ?", (nom_norm,)).fetchone()
            if c:
                id_cli = c["id_cliente"]
                estado = config.PROBABLE
                detalle = f"Vinculado a cliente {c['nombre']} por nombre."

        conn.execute("""
            UPDATE ventas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ?
            WHERE id_venta = ?
        """, (id_cli, id_mas, estado, detalle, id_v))
        resultados["ventas"][estado] = resultados["ventas"].get(estado, 0) + 1

    # 4. Citas -> Clientes y Mascotas
    cur = conn.execute("SELECT id_cita, cliente_documento, celular, hc_norm, estado_relacion FROM citas")
    for c in cur.fetchall():
        if c["estado_relacion"] == config.MANUAL:
            continue
        id_c = c["id_cita"]
        hc = c["hc_norm"]
        doc = c["cliente_documento"]
        cel = c["celular"]

        id_cli, id_mas = None, None
        estado = config.SIN
        detalle = "Sin datos vinculables."

        if hc:
            m = conn.execute("SELECT id_mascota, id_cliente, nombre FROM mascotas WHERE hc_norm = ?", (hc,)).fetchone()
            if m:
                id_mas = m["id_mascota"]
                id_cli = m["id_cliente"]
                estado = config.SEGURA
                detalle = f"Cita vinculada por HC {hc} a paciente {m['nombre']}."

        if not id_cli and doc:
            from modules.normalizacion import normalizar_documento
            doc_norm, _, valido, _ = normalizar_documento(doc)
            if valido:
                cl = conn.execute("SELECT id_cliente FROM clientes WHERE documento_norm = ?", (doc_norm,)).fetchone()
                if cl:
                    id_cli = cl["id_cliente"]
                    estado = config.SEGURA
                    detalle = f"Vinculada a cliente por documento {doc_norm}."

        if not id_cli and cel:
            from modules.normalizacion import normalizar_telefono
            cel_norm, valido = normalizar_telefono(cel)
            if valido:
                cl = conn.execute("SELECT id_cliente FROM clientes WHERE celular_norm = ?", (cel_norm,)).fetchone()
                if cl:
                    id_cli = cl["id_cliente"]
                    estado = config.PROBABLE
                    detalle = f"Vinculada por teléfono {cel_norm}."

        conn.execute("""
            UPDATE citas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ?
            WHERE id_cita = ?
        """, (id_cli, id_mas, estado, detalle, id_c))
        resultados["citas"][estado] = resultados["citas"].get(estado, 0) + 1

    conn.commit()
    return resultados


def asignar_manual(conn, tabla: str, id_registro: int, responsable: str, id_cliente=None, id_mascota=None):
    from datetime import datetime
    ahora_txt = datetime.now().strftime("%Y-%m-%d %H:%M")
    detalle = f"Asignación manual confirmada por {responsable} el {ahora_txt}."

    if tabla == "mascotas":
        conn.execute("UPDATE mascotas SET id_cliente = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_mascota = ?",
                     (id_cliente, config.MANUAL, detalle, id_registro))
    elif tabla == "atenciones":
        conn.execute("UPDATE atenciones SET id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_atencion = ?",
                     (id_mascota, config.MANUAL, detalle, id_registro))
    elif tabla == "ventas":
        conn.execute("UPDATE ventas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_venta = ?",
                     (id_cliente, id_mascota, config.MANUAL, detalle, id_registro))
    elif tabla == "citas":
        conn.execute("UPDATE citas SET id_cliente = ?, id_mascota = ?, estado_relacion = ?, detalle_relacion = ? WHERE id_cita = ?",
                     (id_cliente, id_mascota, config.MANUAL, detalle, id_registro))
    conn.commit()


def deshacer_manual(conn, tabla: str, id_registro: int):
    col_id = f"id_{tabla[:-1]}" if tabla != "citas" else "id_cita"
    if tabla == "mascotas":
        conn.execute(f"UPDATE mascotas SET id_cliente = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                     (config.SIN, id_registro))
    elif tabla == "atenciones":
        conn.execute(f"UPDATE atenciones SET id_mascota = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                     (config.SIN, id_registro))
    elif tabla == "ventas":
        conn.execute(f"UPDATE ventas SET id_cliente = NULL, id_mascota = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                     (config.SIN, id_registro))
    elif tabla == "citas":
        conn.execute(f"UPDATE citas SET id_cliente = NULL, id_mascota = NULL, estado_relacion = ?, detalle_relacion = 'Restaurado a automático' WHERE {col_id} = ?",
                     (config.SIN, id_registro))
    conn.commit()
    recalcular(conn)
