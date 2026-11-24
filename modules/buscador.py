"""
buscador.py - Motor de Búsqueda Instantánea Multi-Criterio
===========================================================
Permite localizar pacientes o clientes por documento, teléfono, nombre o HC.
"""
import pandas as pd
from modules import database
from modules.normalizacion import normalizar_documento, normalizar_hc, normalizar_telefono, normalizar_texto

TIPOS_BUSQUEDA = [
    "Todos los campos (Inteligente)",
    "Documento de Identidad (DNI/RUC)",
    "Teléfono / Celular",
    "Historia Clínica (HC)",
    "Nombre del Propietario / Tutor",
    "Nombre de la Mascota / Paciente"
]


def buscar(conn, texto: str, tipo_filtro: str = "Todos los campos (Inteligente)") -> pd.DataFrame:
    if not texto or not texto.strip():
        return pd.DataFrame()

    texto_limpio = texto.strip()
    norm_txt = normalizar_texto(texto_limpio) or ""
    doc_norm, _, _, _ = normalizar_documento(texto_limpio)
    cel_norm, _ = normalizar_telefono(texto_limpio)
    hc_norm = normalizar_hc(texto_limpio)

    clausulas, params = [], []

    if tipo_filtro == "Documento de Identidad (DNI/RUC)":
        clausulas.append("(c.documento_norm = ? OR m.propietario_documento = ? OR DIGITOS(m.propietario_documento) = ?)")
        params.extend([doc_norm or texto_limpio, texto_limpio, doc_norm or texto_limpio])
    elif tipo_filtro == "Teléfono / Celular":
        clausulas.append("(c.celular_norm LIKE ? OR m.propietario_celular LIKE ? OR DIGITOS(m.propietario_celular) LIKE ?)")
        params.extend([f"%{cel_norm or texto_limpio}%", f"%{texto_limpio}%", f"%{cel_norm or texto_limpio}%"])
    elif tipo_filtro == "Historia Clínica (HC)":
        clausulas.append("(m.hc_norm = ? OR m.hc = ?)")
        params.extend([hc_norm or texto_limpio, texto_limpio])
    elif tipo_filtro == "Nombre del Propietario / Tutor":
        clausulas.append("(c.nombre_norm LIKE ? OR NORM(m.propietario_nombre) LIKE ? OR m.propietario_nombre LIKE ?)")
        params.extend([f"%{norm_txt}%", f"%{norm_txt}%", f"%{texto_limpio}%"])
    elif tipo_filtro == "Nombre de la Mascota / Paciente":
        clausulas.append("m.nombre_norm LIKE ?")
        params.append(f"%{norm_txt}%")
    else:  # Todos los campos (incluye campos propietario_* para mascotas sin vínculo aún)
        c = []
        if doc_norm:
            c.append("c.documento_norm = ? OR m.propietario_documento = ? OR DIGITOS(m.propietario_documento) = ?")
            params.extend([doc_norm, texto_limpio, doc_norm])
        if cel_norm:
            c.append("c.celular_norm LIKE ? OR m.propietario_celular LIKE ? OR DIGITOS(m.propietario_celular) LIKE ?")
            params.extend([f"%{cel_norm}%", f"%{texto_limpio}%", f"%{cel_norm}%"])
        if hc_norm:
            c.append("m.hc_norm = ? OR m.hc = ?")
            params.extend([hc_norm, texto_limpio])
        if norm_txt:
            c.append("c.nombre_norm LIKE ? OR m.nombre_norm LIKE ? OR NORM(m.propietario_nombre) LIKE ?")
            params.extend([f"%{norm_txt}%", f"%{norm_txt}%", f"%{norm_txt}%"])
        clausulas.append("(" + " OR ".join(c) + ")" if c else "1=0")

    sql = f"""
        SELECT
            m.id_mascota,
            m.hc AS HC,
            m.nombre AS Paciente,
            m.especie AS Especie,
            m.raza AS Raza,
            COALESCE(c.nombre, m.propietario_nombre, '—') AS Tutor,
            COALESCE(c.documento, m.propietario_documento, '—') AS Documento,
            COALESCE(c.celular, m.propietario_celular, '—') AS Celular,
            m.estado_relacion AS Estado,
            c.id_cliente
        FROM mascotas m
        LEFT JOIN clientes c ON c.id_cliente = m.id_cliente
        WHERE {' AND '.join(clausulas)}
        ORDER BY m.nombre ASC LIMIT 100
    """
    return database.consultar(conn, sql, params)


def buscar_clientes_sin_mascota(conn, texto: str) -> pd.DataFrame:
    """Localiza clientes registrados que aún no tienen mascotas vinculadas."""
    if not texto or not texto.strip():
        return pd.DataFrame()

    texto_limpio = texto.strip()
    norm_txt = normalizar_texto(texto_limpio) or ""
    doc_norm, _, _, _ = normalizar_documento(texto_limpio)
    cel_norm, _ = normalizar_telefono(texto_limpio)

    condiciones, params = [], []
    if doc_norm:
        condiciones.append("c.documento_norm = ?")
        params.append(doc_norm)
    if cel_norm:
        condiciones.append("c.celular_norm LIKE ?")
        params.append(f"%{cel_norm}%")
    if norm_txt:
        condiciones.append("c.nombre_norm LIKE ?")
        params.append(f"%{norm_txt}%")
    if not condiciones:
        return pd.DataFrame()

    sql = f"""
        SELECT
            c.id_cliente,
            COALESCE(c.documento, '—') AS Documento,
            COALESCE(c.nombre, '—') AS Cliente,
            COALESCE(c.celular, '—') AS Celular,
            COALESCE(c.email, '—') AS Correo,
            COALESCE(c.direccion, '—') AS Dirección
        FROM clientes c
        LEFT JOIN mascotas m ON m.id_cliente = c.id_cliente
        WHERE m.id_mascota IS NULL AND ({' OR '.join(condiciones)})
        ORDER BY c.nombre ASC
        LIMIT 50
    """
    return database.consultar(conn, sql, params)
