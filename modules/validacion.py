"""
validacion.py - Validación estructural previa a la importación
==============================================================
Verifica encabezados, tipos de archivo y presencia de campos críticos.
"""
from dataclasses import dataclass, field
from io import BytesIO
import pandas as pd

from modules import config
from modules.normalizacion import es_vacio, normalizar_encabezado


from pathlib import Path


@dataclass
class ResultadoValidacion:
    ok: bool = False
    errores: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)
    filas: int = 0
    fila_encabezado: int = 0
    mapeo: dict = field(default_factory=dict)
    columnas_no_usadas: list = field(default_factory=list)
    df: pd.DataFrame = None
    filas_descartadas: pd.DataFrame = None


def leer_archivo(contenido: bytes, nombre_archivo: str) -> pd.DataFrame:
    nombre = nombre_archivo.lower()
    if nombre.endswith(".csv"):
        for codificacion in ("utf-8-sig", "latin-1", "utf-8"):
            try:
                return pd.read_csv(
                    BytesIO(contenido), header=None, dtype=object,
                    sep=None, engine="python", encoding=codificacion
                )
            except Exception:
                continue
    motor = "xlrd" if nombre.endswith(".xls") else "openpyxl"
    return pd.read_excel(BytesIO(contenido), header=None, dtype=object, engine=motor)


def leer_archivo_robusto(origen, nombre_archivo: str = None) -> tuple:
    """Lee un archivo desde ruta (str/Path) o bytes y devuelve (df_crudo, mejor_fila)."""
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

    df_crudo = leer_archivo(contenido, nombre)
    df_crudo = df_crudo.dropna(how="all").dropna(axis=1, how="all")
    return df_crudo, 0


def detectar_tipo_reporte(df_crudo: pd.DataFrame) -> tuple:
    """
    Detecta automáticamente qué tipo de reporte de VetPraxis corresponde el DataFrame.
    Retorna (tipo_detectado, confianza).
    """
    if df_crudo is None or df_crudo.empty:
        return "desconocido", 0.0

    mejor_tipo = "desconocido"
    max_confianza = 0.0

    filas_a_evaluar = min(15, len(df_crudo))

    # Analizar títulos o palabras clave en las primeras filas
    texto_primeras_filas = " ".join(
        str(v).lower() for f in range(min(4, len(df_crudo))) for v in df_crudo.iloc[f].values if not es_vacio(v)
    )

    puntos_distintivos = {
        "historias": ["tipo_atencion", "diagnostico", "tratamiento", "motivo"],
        "ventas": ["total", "precio", "comprobante", "item", "cantidad"],
        "mascotas": ["especie", "raza", "sexo", "esterilizacion"],
        "clientes": ["documento", "celular", "direccion"],
        "citas": ["tipo_evento", "motivo_cita", "estado", "fecha"]
    }

    for tipo, definicion in config.REPORTES.items():
        cols_def = definicion["columnas"]
        total_cols = len(cols_def)
        requeridas = [c for c, r in cols_def.items() if r["requerida"]]
        distintivos = puntos_distintivos.get(tipo, [])

        for f_idx in range(filas_a_evaluar):
            fila_vals = [str(x).strip() for x in df_crudo.iloc[f_idx].values if not es_vacio(x)]
            mapeo = mapear_columnas(fila_vals, tipo)
            
            if not mapeo:
                continue

            num_req_coincidentes = sum(1 for c in requeridas if c in mapeo)
            conf_req = num_req_coincidentes / max(1, len(requeridas))
            conf_total = len(mapeo) / max(1, total_cols)

            confianza = (conf_req * 0.5) + (conf_total * 0.3)

            # Bonus por campos distintivos únicos del tipo
            num_dist = sum(1 for c in distintivos if c in mapeo)
            confianza += (num_dist / max(1, len(distintivos))) * 0.25

            # Penalización si es clientes pero detecta HC
            if tipo == "clientes" and "hc" in [normalizar_encabezado(x) for x in fila_vals]:
                confianza -= 0.4

            # Bonus por palabras clave en el encabezado o título
            if tipo == "historias" and any(k in texto_primeras_filas for k in ["historia", "clinica", "atencion"]):
                confianza += 0.2
            elif tipo == "ventas" and any(k in texto_primeras_filas for k in ["comprobante", "venta", "boleta", "factura"]):
                confianza += 0.2
            elif tipo == "mascotas" and "mascota" in texto_primeras_filas:
                confianza += 0.15
            elif tipo == "clientes" and "cliente" in texto_primeras_filas and "mascota" not in texto_primeras_filas:
                confianza += 0.2
            elif tipo == "citas" and any(k in texto_primeras_filas for k in ["cita", "evento", "agenda", "event"]):
                confianza += 0.2

            if confianza > max_confianza:
                max_confianza = confianza
                mejor_tipo = tipo

    return mejor_tipo, min(1.0, max_confianza)



def _buscar_campo(encabezados_norm: list, alias: list, usados: set):
    for a in alias:
        a_norm = normalizar_encabezado(a)
        for i, enc in enumerate(encabezados_norm):
            if i not in usados and enc == a_norm:
                return i
    return None


def mapear_columnas(encabezados: list, tipo: str):
    definicion = config.REPORTES[tipo]["columnas"]
    encabezados_norm = [normalizar_encabezado(e) for e in encabezados]
    mapeo, usados = {}, set()
    for campo, reglas in definicion.items():
        idx = _buscar_campo(encabezados_norm, reglas["alias"], usados)
        if idx is not None:
            mapeo[campo] = idx
            usados.add(idx)
    return mapeo



def detectar_fila_encabezado(df_crudo: pd.DataFrame, tipo: str) -> int:
    limite = min(config.REPORTES[tipo]["filas_encabezado_max"], len(df_crudo))
    mejor_fila, mejor_puntaje = 0, -1
    for i in range(limite):
        puntaje = len(mapear_columnas(list(df_crudo.iloc[i].values), tipo))
        if puntaje > mejor_puntaje:
            mejor_fila, mejor_puntaje = i, puntaje
    return mejor_fila


def validar(contenido: bytes, nombre_archivo: str, tipo: str) -> ResultadoValidacion:
    r = ResultadoValidacion()
    if tipo not in config.REPORTES:
        r.errores.append(f"Tipo de reporte '{tipo}' no reconocido por el sistema.")
        return r

    definicion = config.REPORTES[tipo]

    try:
        crudo = leer_archivo(contenido, nombre_archivo)
    except Exception as e:
        r.errores.append(f"Error al leer el archivo ({e}). Verifique que sea Excel (.xlsx/.xls) o CSV válido.")
        return r

    crudo = crudo.dropna(how="all").dropna(axis=1, how="all")
    if crudo.empty:
        r.errores.append("El archivo seleccionado está vacío.")
        return r

    fila = detectar_fila_encabezado(crudo, tipo)
    encabezados = [str(x).strip() if not es_vacio(x) else f"(sin nombre {i+1})"
                   for i, x in enumerate(crudo.iloc[fila].values)]
    r.fila_encabezado = int(crudo.index[fila]) + 1
    mapeo_idx = mapear_columnas(encabezados, tipo)
    r.mapeo = {campo: encabezados[i] for campo, i in mapeo_idx.items()}
    r.columnas_no_usadas = [e for i, e in enumerate(encabezados) if i not in mapeo_idx.values()]

    for campo, reglas in definicion["columnas"].items():
        if reglas["requerida"] and campo not in mapeo_idx:
            r.errores.append(f"Columna requerida faltante: '{campo}' (esperaba una columna similar a {reglas['alias'][:3]}).")

    for grupo in definicion["al_menos_una"]:
        if not any(c in mapeo_idx for c in grupo):
            r.errores.append("El archivo debe contener al menos una de estas columnas de identificación: " + ", ".join(grupo))

    if r.errores:
        return r

    datos = crudo.iloc[fila + 1:]
    df = pd.DataFrame({campo: datos.iloc[:, i].values for campo, i in mapeo_idx.items()})
    df["fila_excel"] = [int(i) + 1 for i in datos.index]

    campos = list(mapeo_idx.keys())
    vacias = df[campos].apply(lambda f_: all(es_vacio(v) for v in f_), axis=1)
    df = df[~vacias].reset_index(drop=True)

    r.filas = len(df)
    if r.filas == 0:
        r.errores.append("Se detectó el encabezado pero no hay filas con datos en el archivo.")
        return r

    mascara_descartar = pd.Series(False, index=df.index)
    for campo, reglas in definicion["columnas"].items():
        if campo not in df.columns:
            continue
        vacios = df[campo].apply(es_vacio)
        n = int(vacios.sum())
        if n == 0:
            continue
        if reglas["critica"]:
            filas_txt = ", ".join(str(x) for x in df.loc[vacios, "fila_excel"].head(8))
            r.advertencias.append(f"{n} fila(s) omitidas por campo crítico vacío en '{r.mapeo[campo]}' (filas: {filas_txt}).")
            mascara_descartar |= vacios
        elif reglas["requerida"]:
            r.advertencias.append(f"{n} fila(s) con '{r.mapeo[campo]}' vacío se importarán para revisión.")

    r.filas_descartadas = df[mascara_descartar].copy()
    r.df = df[~mascara_descartar].reset_index(drop=True)
    if r.df.empty:
        r.errores.append("Todas las filas del archivo tenían campos obligatorios críticos vacíos.")
        return r

    r.ok = True
    return r
