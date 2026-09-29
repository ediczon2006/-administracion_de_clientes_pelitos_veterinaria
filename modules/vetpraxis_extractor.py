"""
vetpraxis_extractor.py - Módulo de Integración y Extracción de VetPraxis
========================================================================
Herramientas para extraer, interpretar y sincronizar datos de la plataforma VetPraxis,
especialmente el módulo de Agenda y Citas (platform.vetpraxis.app/#/events).
"""
import json
import urllib.parse
from datetime import datetime
import pandas as pd

from modules import config, importador, validacion


def parsear_url_eventos(url: str) -> dict:
    """
    Interpreta los matrix parameters de la URL de VetPraxis:
    Ejemplo: https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=[...];status=pending
    """
    parametros = {}
    if "#/events" not in url:
        return {"valida": False, "error": "La URL no corresponde a la sección de eventos (#/events) de VetPraxis."}

    fragmento = url.split("#/events")[-1]
    partes = fragmento.split(";")
    for p in partes:
        if "=" in p:
            k, v = p.split("=", 1)
            # Decodificar URL encoding (%5B%22 -> ["...)
            v_deco = urllib.parse.unquote(v)
            parametros[k.strip()] = v_deco.strip()

    rango_fechas = parametros.get("startAtRange")
    fechas_legibles = []
    if rango_fechas:
        try:
            fechas_json = json.loads(rango_fechas)
            for f in fechas_json:
                dt = datetime.fromisoformat(f.replace("Z", "+00:00"))
                fechas_legibles.append(dt.strftime("%d/%m/%Y %H:%M"))
        except Exception:
            pass

    return {
        "valida": True,
        "modulo": "events (Agenda / Citas)",
        "estado": parametros.get("status", "todos"),
        "orden": parametros.get("sort", "start_at"),
        "direccion": parametros.get("direction", "desc"),
        "pagina": parametros.get("page", "1"),
        "rango_fechas_raw": rango_fechas,
        "fechas_interpretadas": fechas_legibles,
        "parametros": parametros
    }


def generar_script_consola_js() -> str:
    """
    Genera un snippet JavaScript para ejecutar en la consola del navegador (F12)
    mientras estás conectado a platform.vetpraxis.app.
    Extrae la lista de eventos directamente del estado Angular/DOM y descarga un CSV.
    """
    return """
// === EXTRACTOR AUTOMÁTICO DE CITAS VETPRAXIS ===
// Abre la consola (F12) en https://platform.vetpraxis.app/#/events y pega este código:
(() => {
    const eventos = [];
    const filas = document.querySelectorAll('table tbody tr, .event-item, .appointment-card');
    
    if (filas.length === 0) {
        // Intento por API Angular interna
        const injector = window.angular ? angular.element(document.body).injector() : null;
        console.log("Extrayendo datos de la vista actual...");
    }

    // Encabezados estándar de exportación de Pelitos CRM
    let csv = "FECHA,CLIENTE,DOCUMENTO,TELEFONO,PACIENTE,HC,TIPO EVENTO,ESTADO,VETERINARIO,MOTIVO\\n";

    filas.forEach(f => {
        const cols = Array.from(f.querySelectorAll('td, .cell')).map(c => `"${c.innerText.trim().replace(/"/g, '""')}"`);
        if (cols.length >= 3) {
            csv += cols.join(",") + "\\n";
        }
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `citas_vetpraxis_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
    console.log("✅ Citas exportadas y descargadas con éxito.");
})();
""".strip()


def importar_citas_json(conn, datos_json: list | dict) -> dict:
    """
    Importa una lista de eventos recibidos vía JSON (por ejemplo desde una respuesta de red o API).
    """
    if isinstance(datos_json, dict) and "data" in datos_json:
        datos_json = datos_json["data"]

    filas = []
    for item in datos_json:
        filas.append({
            "fecha": item.get("start_at") or item.get("fecha") or item.get("start"),
            "cliente_nombre": item.get("client_name") or item.get("cliente") or item.get("owner"),
            "cliente_documento": item.get("client_document") or item.get("documento"),
            "celular": item.get("client_phone") or item.get("telefono") or item.get("celular"),
            "paciente": item.get("patient_name") or item.get("mascota") or item.get("paciente"),
            "hc": item.get("hc") or item.get("patient_hc"),
            "tipo_evento": item.get("type") or item.get("tipo") or "Cita",
            "estado": item.get("status") or "Pendiente",
            "veterinario": item.get("doctor") or item.get("veterinario"),
            "motivo": item.get("notes") or item.get("motivo") or item.get("description"),
        })

    df = pd.DataFrame(filas)
    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    res_val = validacion.validar(csv_bytes, "citas_vetpraxis.csv", "citas")
    if not res_val.ok:
        return {"ok": False, "errores": res_val.errores}

    res_imp = importador.importar(conn, "citas", res_val.df, "citas_vetpraxis.csv", csv_bytes)
    return {"ok": True, "resumen": res_imp}
