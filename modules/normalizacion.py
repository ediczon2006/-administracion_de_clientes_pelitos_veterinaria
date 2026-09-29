"""
normalizacion.py - Funciones especializadas de estandarización y limpieza
========================================================================
Convierte formatos heterogéneos de VetPraxis a representaciones canónicas.
"""
from datetime import datetime, timedelta
import re
import unicodedata
import urllib.parse
import pandas as pd

from modules import config


def es_vacio(valor) -> bool:
    if valor is None:
        return True
    try:
        if pd.isna(valor):
            return True
    except (TypeError, ValueError):
        pass
    return str(valor).strip().lower() in config.VALORES_VACIOS


def a_texto(valor):
    if es_vacio(valor):
        return None
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    texto = str(valor).strip()
    texto = re.sub(r"\s+", " ", texto)
    if re.fullmatch(r"\d+\.0", texto):
        texto = texto[:-2]
    return texto or None


def quitar_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def normalizar_texto(valor):
    """Limpia nombres para comparación: MAYÚSCULAS, sin tildes, sin signos."""
    texto = a_texto(valor)
    if texto is None:
        return None
    texto = quitar_tildes(texto).upper()
    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto or None


def normalizar_encabezado(valor) -> str:
    """Normaliza nombres de columnas en archivos."""
    texto = a_texto(valor) or ""
    texto = texto.replace("º", "").replace("°", "").replace("#", "")
    texto = quitar_tildes(texto).lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return texto.strip()


def normalizar_documento(valor):
    """Devuelve (documento_norm, tipo, valido, observacion)."""
    texto = a_texto(valor)
    if texto is None:
        return None, None, False, "vacío"
    limpio = re.sub(r"[^0-9A-Za-z]", "", texto).upper()
    if limpio.isdigit():
        if len(limpio) == 8:
            return limpio, "DNI", True, ""
        if len(limpio) == 11:
            return limpio, "RUC", True, ""
        if len(limpio) == 7 and config.COMPLETAR_DNI_7_DIGITOS:
            return "0" + limpio, "DNI", True, "se completó cero inicial (eliminado por Excel)"
        if 9 <= len(limpio) <= 12:
            return limpio, "CE", True, "posible carné de extranjería"
        return limpio, None, False, f"longitud no estándar ({len(limpio)} dígitos)"
    if 6 <= len(limpio) <= 12 and re.search(r"\d", limpio):
        return limpio, "CE/PAS", True, "documento alfanumérico"
    return limpio or None, None, False, "formato no reconocido"


def normalizar_telefono(valor):
    """Extrae teléfono peruano limpio. Si hay múltiples, toma el primero."""
    texto = a_texto(valor)
    if texto is None:
        return None, False
    primero = re.split(r"[/;,|\-]|\sy\s", texto)[0].strip()
    digitos = re.sub(r"\D", "", primero)
    if digitos.startswith("00"):
        digitos = digitos[2:]
    if digitos.startswith(config.CODIGO_PAIS) and len(digitos) == 9 + len(config.CODIGO_PAIS):
        digitos = digitos[len(config.CODIGO_PAIS):]
    if len(digitos) == 9 and digitos.startswith("9"):
        return digitos, True
    if 6 <= len(digitos) <= 9:
        return digitos, True
    return (digitos or None), False


def es_celular(telefono_norm) -> bool:
    return bool(telefono_norm) and len(telefono_norm) == 9 and telefono_norm.startswith("9")


def link_whatsapp(telefono, mensaje="") -> str | None:
    tel_norm, valido = normalizar_telefono(telefono)
    if not valido or not es_celular(tel_norm):
        return None
    url = f"https://wa.me/{config.CODIGO_PAIS}{tel_norm}"
    if mensaje and mensaje.strip():
        url += f"?text={urllib.parse.quote(mensaje.strip())}"
    return url


def normalizar_hc(valor):
    texto = a_texto(valor)
    if texto is None:
        return None
    limpio = re.sub(r"[\s\-_.]", "", texto).upper()
    if limpio.isdigit() and config.QUITAR_CEROS_HC_NUMERICA:
        limpio = limpio.lstrip("0") or "0"
    return limpio or None


def normalizar_fecha(valor):
    """Normaliza fechas variadas (YYYY-MM-DD, DD-MM-YY, con hora 12h/24h) a ISO 'YYYY-MM-DD'."""
    if es_vacio(valor):
        return None
    if isinstance(valor, (datetime, pd.Timestamp)):
        return valor.strftime("%Y-%m-%d")
    if isinstance(valor, (int, float)) and 20000 < float(valor) < 80000:
        return (datetime(1899, 12, 30) + timedelta(days=float(valor))).strftime("%Y-%m-%d")
    
    texto = str(valor).strip()
    # Si viene formato ISO "2026-09-09 10:58:13"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", texto):
        fecha = pd.to_datetime(texto[:19], errors="coerce")
    else:
        # Formatos latinos DD-MM-YY o DD/MM/YYYY con hora y AM/PM
        fecha = pd.to_datetime(texto, dayfirst=True, errors="coerce")
        
    if pd.isna(fecha):
        return None
    return fecha.strftime("%Y-%m-%d")


def normalizar_numero(valor):
    if es_vacio(valor):
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = re.sub(r"[^0-9,.\-]", "", str(valor))
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif texto.count(",") == 1 and len(texto.split(",")[1]) <= 2:
        texto = texto.replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")
    else:
        texto = texto.replace(",", "")
    try:
        return float(texto)
    except ValueError:
        return None
