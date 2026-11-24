"""
vetpraxis_extractor.py - Módulo de Integración y Extracción de VetPraxis
========================================================================
Herramientas para extraer, interpretar y sincronizar datos de la plataforma VetPraxis,
especialmente el módulo de Agenda y Citas (platform.vetpraxis.app/#/events).
"""
from datetime import datetime
import json
import urllib.parse
import pandas as pd

from modules import importador, validacion


def parsear_url_eventos(url: str) -> dict:
    """
    Interpreta los matrix parameters de la URL de VetPraxis:
    Ejemplo: https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=[...];status=pending
    """
    parametros = {}
    if not url or "#/events" not in url:
        return {"valida": False, "error": "La URL no corresponde a la sección de eventos (#/events) de VetPraxis."}

    fragmento = url.split("#/events")[-1]
    partes = fragmento.split(";")
    for p in partes:
        if "=" in p:
            k, v = p.split("=", 1)
            v_deco = urllib.parse.unquote(v)
            parametros[k.strip()] = v_deco.strip()

    rango_fechas = parametros.get("startAtRange")
    fechas_legibles = []
    if rango_fechas:
        try:
            fechas_json = json.loads(rango_fechas)
            if isinstance(fechas_json, list):
                for f in fechas_json:
                    dt = datetime.fromisoformat(str(f).replace("Z", "+00:00"))
                    fechas_legibles.append(dt.strftime("%d/%m/%Y %H:%M"))
        except Exception:
            pass

    return {
        "valida": True,
        "modulo": "events (Agenda / Citas)",
        "estado": parametros.get("status", "todos") or "todos",
        "orden": parametros.get("sort", "start_at") or "start_at",
        "direccion": parametros.get("direction", "desc") or "desc",
        "pagina": parametros.get("page", "1") or "1",
        "rango_fechas_raw": rango_fechas,
        "fechas_interpretadas": fechas_legibles,
        "parametros": parametros,
    }


def generar_script_consola_js() -> str:
    """
    Genera un snippet JavaScript para ejecutar en la consola del navegador (F12)
    mientras está conectado a platform.vetpraxis.app/#/events.
    Extrae las filas visibles de la agenda y descarga un archivo JSON compatible con este CRM.
    """
    return """
// === EXTRACTOR AUTOMÁTICO DE CITAS VETPRAXIS (JSON) ===
// Abre la consola (F12) en https://platform.vetpraxis.app/#/events y pega este código:
(() => {
    const eventos = [];
    const filas = document.querySelectorAll('table tbody tr, .event-item, .appointment-card');

    filas.forEach(f => {
        const celdas = Array.from(f.querySelectorAll('td, .cell')).map(c => c.innerText.trim());
        if (celdas.length >= 3) {
            eventos.push({
                fecha: celdas[0] || '',
                cliente: celdas[1] || '',
                paciente: celdas[2] || '',
                tipo: celdas[3] || 'Cita',
                estado: celdas[4] || 'Pendiente',
                veterinario: celdas[5] || '',
                motivo: celdas.slice(6).join(' | ')
            });
        }
    });

    if (eventos.length === 0) {
        console.warn('No se detectaron filas de eventos en la vista actual. Use el Método 1 (Exportar) o Método 2 (Network -> Copy Response).');
        return;
    }

    const blob = new Blob([JSON.stringify(eventos, null, 2)], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `citas_vetpraxis_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    console.log(`✅ ${eventos.length} citas exportadas en JSON.`);
})();
""".strip()


def importar_citas_json(conn, datos_json: list | dict) -> dict:
    """
    Importa una lista de eventos recibidos vía JSON (por ejemplo desde una respuesta de red o API).
    Acepta: lista de objetos, un diccionario con clave 'data'/'events'/'items', o un objeto individual.
    """
    if isinstance(datos_json, dict):
        for clave in ("data", "events", "items", "results"):
            if clave in datos_json and isinstance(datos_json[clave], list):
                datos_json = datos_json[clave]
                break
        else:
            datos_json = [datos_json]

    if not isinstance(datos_json, list) or not datos_json:
        return {"ok": False, "errores": ["El JSON no contiene una lista válida de eventos o está vacío."]}

    filas = []
    for item in datos_json:
        if not isinstance(item, dict):
            continue
        cliente_obj = item.get("client") if isinstance(item.get("client"), dict) else {}
        paciente_obj = item.get("patient") if isinstance(item.get("patient"), dict) else {}
        doctor_obj = item.get("doctor") if isinstance(item.get("doctor"), dict) else {}

        filas.append({
            "fecha": item.get("start_at") or item.get("fecha") or item.get("start"),
            "cliente_nombre": (
                item.get("client_name") or item.get("cliente") or item.get("owner")
                or cliente_obj.get("name") or cliente_obj.get("full_name")
            ),
            "cliente_documento": (
                item.get("client_document") or item.get("documento")
                or cliente_obj.get("document") or cliente_obj.get("dni")
            ),
            "celular": (
                item.get("client_phone") or item.get("telefono") or item.get("celular")
                or cliente_obj.get("phone") or cliente_obj.get("mobile")
            ),
            "paciente": (
                item.get("patient_name") or item.get("mascota") or item.get("paciente")
                or paciente_obj.get("name")
            ),
            "hc": (
                item.get("hc") or item.get("patient_hc")
                or paciente_obj.get("hc") or paciente_obj.get("medical_record")
            ),
            "tipo_evento": item.get("type") or item.get("tipo") or "Cita",
            "estado": item.get("status") or item.get("estado") or "Pendiente",
            "veterinario": (
                (item.get("doctor") if isinstance(item.get("doctor"), str) else None)
                or item.get("veterinario") or doctor_obj.get("name")
            ),
            "motivo": item.get("notes") or item.get("motivo") or item.get("description"),
        })

    if not filas:
        return {"ok": False, "errores": ["Ningún elemento del JSON tiene formato de evento válido."]}

    df = pd.DataFrame(filas)
    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    res_val = validacion.validar(csv_bytes, "citas_vetpraxis.csv", "citas")
    if not res_val.ok:
        return {"ok": False, "errores": res_val.errores}

    res_imp = importador.importar(conn, "citas", res_val.df, "citas_vetpraxis.csv", csv_bytes)
    return {"ok": True, "resumen": res_imp}
