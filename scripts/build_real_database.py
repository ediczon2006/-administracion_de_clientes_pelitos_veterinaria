import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from modules.normalizacion import normalizar_telefono, normalizar_documento



parent = Path(__file__).resolve().parent.parent.parent
cli_path = parent / "Reporte de Clientes.xlsx"
mas_path = parent / "Reporte de Mascotas.xlsx"
his_path = parent / "Reporte de Historias Clnicas - 01.09.2026 al 22.09.2026.xlsx"
com_path = parent / "Reporte de Comprobantes - 23.08.2026 al 22.09.2026.xlsx"
itm_path = parent / "Reporte de ventas por items - 23.08.2026 al 22.09.2026.xlsx"

db = {"clientes": [], "mascotas": [], "atenciones": [], "ventas": [], "seguimientos": [], "citas": []}

# 1. Clientes
if cli_path.exists():
    df_cli = pd.read_excel(cli_path, dtype=str)
    for idx, r in df_cli.iterrows():
        doc = str(r.get("DOCUMENTO") or "").strip()
        if doc == "nan": doc = ""
        nom_raw = str(r.get("NOMBRES Y APELLIDOS") or "").strip()
        if nom_raw == "nan": nom_raw = ""
        if "," in nom_raw:
            parts = nom_raw.split(",")
            nom = f"{parts[1].strip()} {parts[0].strip()}".strip()
        else:
            nom = nom_raw
        cel = str(r.get("TELÉFONOS") or "").strip()
        if cel == "nan": cel = ""
        cel_norm, _ = normalizar_telefono(cel)
        dir_val = str(r.get("DIRECCIÓN") or "").replace("|", "").strip()
        if dir_val == "nan": dir_val = ""
        masc = str(r.get("MASCOTAS") or "").strip()
        if masc == "nan": masc = ""
        
        if nom or doc:
            db["clientes"].append({
                "id": len(db["clientes"]) + 1,
                "documento": doc,
                "nombre": nom,
                "celular": cel_norm or cel,
                "direccion": dir_val,
                "mascotas_resumen": masc
            })

# 2. Mascotas
if mas_path.exists():
    df_mas = pd.read_excel(mas_path, dtype=str)
    for idx, r in df_mas.iterrows():
        hc = str(r.get("N° HISTORIA CLÍNICA") or "").strip()
        if hc == "nan": hc = ""
        nom = str(r.get("NOMBRE") or "").strip()
        if nom == "nan": nom = ""
        esp = str(r.get("ESPECIE") or "").strip()
        if esp == "nan": esp = ""
        raz = str(r.get("RAZA") or "").strip()
        if raz == "nan": raz = ""
        sex = str(r.get("SEXO") or "").strip()
        if sex == "nan": sex = ""
        prop = str(r.get("PROPIETARIO") or "").strip()
        if prop == "nan": prop = ""
        cel = str(r.get("CELULAR DEL PROPIETARIO") or "").strip()
        if cel == "nan": cel = ""
        cel_norm, _ = normalizar_telefono(cel)
        est = str(r.get("ESTERILIZACIÓN") or "").strip()
        if est == "nan": est = ""

        if nom or hc:
            db["mascotas"].append({
                "hc": hc,
                "nombre": nom,
                "especie": esp,
                "raza": raz,
                "sexo": sex,
                "propietario": prop,
                "celular": cel_norm or cel,
                "esterilizado": est
            })

# 3. Atenciones
if his_path.exists():
    df_his = pd.read_excel(his_path, skiprows=3, dtype=str)
    for idx, r in df_his.iterrows():
        fec = str(r.get("FECHA DE ATENCIÓN") or "").strip()
        if fec == "nan": fec = ""
        tip = str(r.get("TIPO DE ATENCIÓN") or "").strip()
        if tip == "nan": tip = ""
        hc = str(r.get("HC") or "").strip()
        if hc == "nan": hc = ""
        pac = str(r.get("PACIENTE") or "").strip()
        if pac == "nan": pac = ""
        dx = str(r.get("DIAGNÓSTICO") or r.get("EXAMEN CLÍNICO EXTENDIDO") or "").replace("\n", " ").strip()
        if dx == "nan": dx = ""
        mot = str(r.get("MOTIVO DE ATENCIÓN") or r.get("ANAMNESIS") or "").replace("\n", " ").strip()
        if mot == "nan": mot = ""
        tx = str(r.get("TRATAMIENTO") or "").replace("\n", " | ").strip()
        if tx == "nan": tx = ""

        if hc or fec:
            db["atenciones"].append({
                "fecha": fec,
                "tipo": tip,
                "hc": hc,
                "paciente": pac,
                "motivo": mot,
                "diagnostico": dx or mot,
                "tratamiento": tx
            })

# 4. Ventas
if itm_path.exists():
    df_itm = pd.read_excel(itm_path, dtype=str)
    for idx, r in df_itm.iterrows():
        fec = str(r.get("FECHA DE EMISIÓN") or "").strip()
        if fec == "nan": fec = ""
        comp = str(r.get("DOCUMENTO") or "").replace("BOLETA DE VENTA ELECTRONICA: ", "").replace("FACTURA ELECTRONICA: ", "").strip()
        if comp == "nan": comp = ""
        cli = str(r.get("CLIENTE") or "").strip()
        if cli == "nan": cli = ""
        mas = str(r.get("MASCOTA") or "").strip()
        if mas == "nan": mas = ""
        hc = str(r.get("Nº HC") or "").strip()
        if hc == "nan": hc = ""
        itm = str(r.get("CONCEPTO") or "Venta General").strip()
        if itm == "nan": itm = "Venta General"
        tot_str = str(r.get("TOTAL") or "0").replace(",", "")
        try: tot = float(tot_str)
        except: tot = 0.0

        db["ventas"].append({
            "fecha": fec,
            "comprobante": comp,
            "cliente": cli,
            "mascota": mas,
            "hc": hc,
            "item": itm,
            "total": tot
        })

# Generar seguimientos automáticos de los casos clínicos reales
for a in db["atenciones"]:
    desc = a["diagnostico"] or a["motivo"] or a["tipo"]
    db["seguimientos"].append({
        "fecha": a["fecha"].split()[0] if a["fecha"] else "2026-09-22",
        "cliente": "",
        "mascota": a["paciente"],
        "hc": a["hc"],
        "motivo": f"Control {a['tipo']}: {desc[:40]}",
        "estado": "Pendiente",
        "nota": f"Tratamiento: {a['tratamiento'][:60]}..." if a["tratamiento"] else "Control post-consulta",
        "celular": ""
    })

# Enlazar
cli_por_cel = {c["celular"]: c for c in db["clientes"] if c.get("celular")}
cli_por_nom = {c["nombre"].lower(): c for c in db["clientes"] if c.get("nombre")}
mas_por_hc = {m["hc"]: m for m in db["mascotas"] if m.get("hc")}

for m in db["mascotas"]:
    c = cli_por_cel.get(m.get("celular")) or cli_por_nom.get((m.get("propietario") or "").lower())
    if c:
        m["id_cliente"] = c["id"]

for s in db["seguimientos"]:
    m = mas_por_hc.get(s.get("hc"))
    if m:
        s["cliente"] = m.get("propietario")
        s["celular"] = m.get("celular")

out_path = Path(__file__).resolve().parent.parent / "data" / "pelitos_datos_reales.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"Éxito: Clientes={len(db['clientes'])}, Mascotas={len(db['mascotas'])}, Atenciones={len(db['atenciones'])}, Ventas={len(db['ventas'])}, Seguimientos={len(db['seguimientos'])}")
