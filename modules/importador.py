"""
importador.py - Motor de Ingesta, Deduplicación y Trazabilidad
=============================================================
Procesa e inserta los reportes de VetPraxis en SQLite de manera idempotente.
"""
from collections import defaultdict
from datetime import datetime
import hashlib
import re
import pandas as pd

from modules import config, relaciones
from modules.database import transaccion
from modules.normalizacion import (a_texto, normalizar_documento, normalizar_fecha,
                                   normalizar_hc, normalizar_numero, normalizar_telefono, normalizar_texto)


def ahora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_archivo(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def importaciones_previas(conn, huella: str) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT id_importacion, tipo_reporte, archivo, fecha_importacion, insertados "
        "FROM importaciones WHERE hash_archivo = ?", conn, params=(huella,)
    )


def _hash_clave(*partes) -> str:
    return hashlib.sha1("|".join("" if p is None else str(p) for p in partes).encode()).hexdigest()


def nombre_archivo_seguro(nombre: str) -> str:
    base = re.split(r"[\\/]", nombre or "")[-1]
    base = re.sub(r"[^A-Za-z0-9._ -]", "_", base).strip(" .")
    return base[:120] or "archivo"


def _v(fila, campo):
    return a_texto(fila.get(campo)) if campo in fila else None


# ---------------------------------------------------------------- Transformaciones
def _transformar_cliente(fila):
    doc_norm, tipo_doc, doc_ok, _ = normalizar_documento(fila.get("documento"))
    nombre_raw = _v(fila, "nombre") or ""
    # Si viene formato "NOMBRES, APELLIDOS", normalizamos limpiando comas
    if _v(fila, "apellidos"):
        nombre = f"{nombre_raw} {_v(fila, 'apellidos')}".strip()
    else:
        nombre = re.sub(r"\s+", " ", nombre_raw.replace(",", " ")).strip()
        
    cel_norm, _ = normalizar_telefono(fila.get("celular"))
    nombre_norm = normalizar_texto(nombre)
    
    if doc_ok:
        clave = f"DOC:{doc_norm}"
    elif _v(fila, "codigo_origen"):
        clave = f"COD:{_v(fila, 'codigo_origen')}"
    else:
        clave = f"NOM:{nombre_norm}|TEL:{cel_norm or ''}|DOC:{doc_norm or ''}"

    return {
        "clave_unica": clave, "codigo_origen": _v(fila, "codigo_origen"),
        "documento": _v(fila, "documento"), "documento_norm": doc_norm, "tipo_documento": tipo_doc,
        "documento_valido": int(doc_ok), "nombre": nombre, "nombre_norm": nombre_norm,
        "celular": _v(fila, "celular"), "celular_norm": cel_norm, "email": _v(fila, "email"),
        "direccion": _v(fila, "direccion"), "fecha_registro": normalizar_fecha(fila.get("fecha_registro")),
        "fila_excel": int(fila["fila_excel"]),
    }


def _transformar_mascota(fila):
    hc_norm = normalizar_hc(fila.get("hc"))
    return {
        "clave_unica": f"HC:{hc_norm}", "hc": _v(fila, "hc"), "hc_norm": hc_norm,
        "nombre": _v(fila, "nombre"), "nombre_norm": normalizar_texto(fila.get("nombre")),
        "especie": _v(fila, "especie"), "raza": _v(fila, "raza"), "sexo": _v(fila, "sexo"),
        "fecha_nacimiento": normalizar_fecha(fila.get("fecha_nacimiento")),
        "esterilizacion": _v(fila, "esterilizacion"),
        "propietario_documento": _v(fila, "propietario_documento"),
        "propietario_nombre": _v(fila, "propietario_nombre"),
        "propietario_celular": _v(fila, "propietario_celular"),
        "fila_excel": int(fila["fila_excel"]),
    }


def _transformar_atencion(fila):
    return {
        "hc": _v(fila, "hc"), "hc_norm": normalizar_hc(fila.get("hc")),
        "fecha": normalizar_fecha(fila.get("fecha")), "fecha_original": _v(fila, "fecha"),
        "tipo_atencion": _v(fila, "tipo_atencion"), "paciente": _v(fila, "paciente"),
        "motivo": _v(fila, "motivo"), "diagnostico": _v(fila, "diagnostico"),
        "tratamiento": _v(fila, "tratamiento"), "veterinario": _v(fila, "veterinario"),
        "fila_excel": int(fila["fila_excel"]),
    }


def _transformar_venta(fila):
    doc_norm, _, _, _ = normalizar_documento(fila.get("cliente_documento"))
    comprobante = _v(fila, "comprobante")
    categoria = _v(fila, "categoria")
    item = _v(fila, "item")
    if not item:
        # En reporte de comprobantes VetPraxis, usar la descripción o comprobante
        item = f"{categoria or 'Comprobante'} {comprobante or ''}".strip() or "Venta General"

    return {
        "fecha": normalizar_fecha(fila.get("fecha")), "fecha_original": _v(fila, "fecha"),
        "comprobante": comprobante, "cliente_documento": _v(fila, "cliente_documento"),
        "_doc_norm": doc_norm, "cliente_nombre": _v(fila, "cliente_nombre"),
        "hc": _v(fila, "hc"), "hc_norm": normalizar_hc(fila.get("hc")), "mascota": _v(fila, "mascota"),
        "categoria": categoria, "item": item,
        "cantidad": normalizar_numero(fila.get("cantidad")) or 1.0,
        "precio": normalizar_numero(fila.get("precio")) or normalizar_numero(fila.get("total")),
        "total": normalizar_numero(fila.get("total")), "fila_excel": int(fila["fila_excel"]),
    }


def _transformar_cita(fila):
    return {
        "fecha": normalizar_fecha(fila.get("fecha")), "fecha_original": _v(fila, "fecha"),
        "cliente_nombre": _v(fila, "cliente_nombre"),
        "cliente_documento": _v(fila, "cliente_documento"),
        "celular": _v(fila, "celular"),
        "paciente": _v(fila, "paciente"),
        "hc": _v(fila, "hc"), "hc_norm": normalizar_hc(fila.get("hc")),
        "tipo_evento": _v(fila, "tipo_evento") or "Cita Médica",
        "estado": _v(fila, "estado") or "Pendiente",
        "veterinario": _v(fila, "veterinario"),
        "motivo": _v(fila, "motivo"),
        "fila_excel": int(fila["fila_excel"]),
    }


CAMPOS_IDENTIDAD = {"clave_unica", "fila_excel", "hc", "hc_norm", "documento", "documento_norm"}


def _upsert(conn, tabla, id_col, registro, id_imp, resumen):
    existente = conn.execute(f"SELECT * FROM {tabla} WHERE clave_unica = ?", (registro["clave_unica"],)).fetchone()
    if existente is None:
        registro.update({"id_importacion": id_imp, "actualizado_en": ahora()})
        cols = ", ".join(registro)
        conn.execute(f"INSERT INTO {tabla} ({cols}) VALUES ({', '.join('?' * len(registro))})",
                     tuple(registro.values()))
        resumen["insertados"] += 1
        return

    if existente["nombre_norm"] and registro["nombre_norm"] and existente["nombre_norm"] != registro["nombre_norm"]:
        detalle = (f"{registro['clave_unica']} repetida con otro nombre: "
                   f"'{existente['nombre']}' vs '{registro['nombre']}' (fila {registro['fila_excel']}).")
        if detalle not in (existente["alerta"] or ""):
            nueva = f"{existente['alerta']} | {detalle}" if existente["alerta"] else detalle
            conn.execute(f"UPDATE {tabla} SET alerta = ? WHERE {id_col} = ?", (nueva, existente[id_col]))
        resumen["revision"] += 1
        return

    cambios = {k: v for k, v in registro.items()
               if k not in CAMPOS_IDENTIDAD and v not in (None, "") and existente[k] != v}
    if not cambios:
        resumen["duplicados"] += 1
        return
    cambios["actualizado_en"] = ahora()
    sets = ", ".join(f"{k} = ?" for k in cambios)
    conn.execute(f"UPDATE {tabla} SET {sets} WHERE {id_col} = ?", (*cambios.values(), existente[id_col]))
    resumen["actualizados"] += 1


def _insertar_eventos(conn, tabla, registros, campos_clave, id_imp, resumen):
    repeticiones = defaultdict(int)
    for reg in registros:
        base = tuple(normalizar_texto(reg.get(c)) if isinstance(reg.get(c), str) else reg.get(c)
                     for c in campos_clave)
        repeticiones[base] += 1
        reg["clave_unica"] = _hash_clave(tabla, *base, repeticiones[base])
        reg["id_importacion"] = id_imp
        fila_db = {k: v for k, v in reg.items() if not k.startswith("_")}
        cols = ", ".join(fila_db)
        cur = conn.execute(f"INSERT OR IGNORE INTO {tabla} ({cols}) VALUES ({', '.join('?' * len(fila_db))})",
                           tuple(fila_db.values()))
        if cur.rowcount == 1:
            resumen["insertados"] += 1
        else:
            resumen["duplicados"] += 1


def importar(conn, tipo: str, df: pd.DataFrame, nombre_archivo: str, contenido: bytes,
             descartados: int = 0, hacer_backup: bool = True) -> dict:
    if hacer_backup:
        from modules.backup import crear_backup
        crear_backup(conn, motivo=f"antes_importar_{tipo}")

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    huella = hash_archivo(contenido)
    ruta_original = config.DATA_ORIGINALES / f"{marca}_{tipo}_{nombre_archivo_seguro(nombre_archivo)}"
    ruta_original.write_bytes(contenido)

    resumen = {"leidos": len(df), "insertados": 0, "actualizados": 0, "duplicados": 0,
               "revision": 0, "descartados": descartados}
    filas = df.to_dict("records")

    with transaccion(conn):
        cur = conn.execute(
            "INSERT INTO importaciones (tipo_reporte, archivo, archivo_guardado, hash_archivo, "
            "fecha_importacion, registros_leidos) VALUES (?,?,?,?,?,?)",
            (tipo, nombre_archivo, ruta_original.name, huella, ahora(), len(df)))
        id_imp = cur.lastrowid

        if tipo == "clientes":
            registros = [_transformar_cliente(f) for f in filas]
            repeticiones = defaultdict(int)
            for reg in registros:
                if reg["clave_unica"].startswith("NOM:"):
                    repeticiones[reg["clave_unica"]] += 1
                    reg["clave_unica"] += f"|#{repeticiones[reg['clave_unica']]}"
            for reg in registros:
                _upsert(conn, "clientes", "id_cliente", reg, id_imp, resumen)
        elif tipo == "mascotas":
            registros = [_transformar_mascota(f) for f in filas]
            for reg in registros:
                _upsert(conn, "mascotas", "id_mascota", reg, id_imp, resumen)
        elif tipo == "historias":
            registros = [_transformar_atencion(f) for f in filas]
            _insertar_eventos(conn, "atenciones", registros,
                              ["hc_norm", "fecha", "tipo_atencion", "motivo", "diagnostico", "tratamiento"],
                              id_imp, resumen)
        elif tipo == "ventas":
            registros = [_transformar_venta(f) for f in filas]
            _insertar_eventos(conn, "ventas", registros,
                              ["fecha", "comprobante", "_doc_norm", "hc_norm", "item", "cantidad", "precio", "total"],
                              id_imp, resumen)
        elif tipo == "citas":
            registros = [_transformar_cita(f) for f in filas]
            _insertar_eventos(conn, "citas", registros,
                              ["fecha", "cliente_documento", "celular", "hc_norm", "tipo_evento"],
                              id_imp, resumen)
        else:
            raise ValueError(f"Tipo no soportado: {tipo}")

        obs = f"Leídos: {len(df)} | Insertados: {resumen['insertados']} | Duplicados: {resumen['duplicados']}"
        conn.execute("UPDATE importaciones SET insertados=?, actualizados=?, duplicados=?, descartados=?, "
                     "observaciones=? WHERE id_importacion=?",
                     (resumen["insertados"], resumen["actualizados"], resumen["duplicados"], descartados, obs, id_imp))

    # Guardar CSV normalizado
    pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in registros]).to_csv(
        config.DATA_PROCESADOS / f"{marca}_{tipo}_normalizado.csv", index=False, encoding="utf-8-sig")

    resumen["relaciones"] = relaciones.recalcular(conn)
    resumen["id_importacion"] = id_imp
    return resumen


def importar_archivo(origen, tipo_manual: str = None, nombre_archivo: str = None,
                     db_path: str = None, hacer_backup: bool = True) -> dict:
    """
    Función de alto nivel para importar un archivo de VetPraxis desde ruta o buffer.
    Valida, detecta automáticamente el tipo si no se especificó, e inserta en la BD.
    """
    from pathlib import Path
    from modules.database import get_db
    from modules.validacion import validar, leer_archivo, detectar_tipo_reporte

    if isinstance(origen, (str, Path)):
        p = Path(origen)
        contenido = p.read_bytes()
        nombre = nombre_archivo or p.name
    elif hasattr(origen, "read"):
        contenido = origen.read()
        nombre = nombre_archivo or getattr(origen, "name", "archivo.xlsx")
    else:
        contenido = bytes(origen)
        nombre = nombre_archivo or "archivo.xlsx"

    tipo = tipo_manual
    if not tipo or tipo == "auto":
        try:
            df_crudo = leer_archivo(contenido, nombre)
            tipo_detectado, conf = detectar_tipo_reporte(df_crudo)
            if conf >= 0.35:
                tipo = tipo_detectado
            else:
                return {
                    "exito": False,
                    "errores": [f"No se pudo determinar el tipo de reporte con certeza ({tipo_detectado}, confianza {conf:.1%}). Especifique el tipo manualmente."],
                    "advertencias": []
                }
        except Exception as e:
            return {"exito": False, "errores": [f"Error leyendo archivo: {e}"], "advertencias": []}

    res_val = validar(contenido, nombre, tipo)
    if not res_val.ok:
        return {
            "exito": False,
            "tipo": tipo,
            "errores": res_val.errores,
            "advertencias": res_val.advertencias,
            "filas_leidas": res_val.filas,
            "filas_insertadas": 0
        }

    descartados = len(res_val.filas_descartadas) if res_val.filas_descartadas is not None else 0

    with get_db(db_path) as conn:
        resumen = importar(
            conn=conn,
            tipo=tipo,
            df=res_val.df,
            nombre_archivo=nombre,
            contenido=contenido,
            descartados=descartados,
            hacer_backup=hacer_backup
        )

    return {
        "exito": True,
        "tipo": tipo,
        "errores": [],
        "advertencias": res_val.advertencias,
        "filas_leidas": resumen["leidos"],
        "filas_insertadas": resumen["insertados"],
        "filas_actualizadas": resumen["actualizados"],
        "duplicados": resumen["duplicados"],
        "descartados": resumen["descartados"],
        "relaciones": resumen.get("relaciones", {})
    }

