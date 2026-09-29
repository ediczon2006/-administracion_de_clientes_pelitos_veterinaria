"""
parse_pasted_data.py - Parsea el texto pegado de VetPraxis y genera JSON estructurado
"""
import csv
import io
import json
import re
from pathlib import Path

def parse_multi_section_csv(text: str):
    lines = text.strip().splitlines()
    
    # Dividir en secciones según encabezados conocidos
    sections = {}
    current_section = None
    current_lines = []

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        if line_clean.startswith("FECHA DE REGISTRO,NOMBRES Y APELLIDOS"):
            if current_section:
                sections[current_section] = current_lines
            current_section = "clientes"
            current_lines = [line]
        elif line_clean.startswith("FECHA DE EMISIÓN,FECHA DE CONTABILIZACIÓN"):
            if current_section:
                sections[current_section] = current_lines
            current_section = "comprobantes"
            current_lines = [line]
        elif "REPORTE DE HISTORIAS CLÍNICAS" in line_clean or line_clean.startswith("FECHA DE ATENCIÓN,TIPO DE ATENCIÓN"):
            if current_section:
                sections[current_section] = current_lines
            current_section = "historias"
            current_lines = [line]
        elif line_clean.startswith("FECHA DE EMISIÓN,DOCUMENTO,VENDEDOR"):
            if current_section:
                sections[current_section] = current_lines
            current_section = "ventas_items"
            current_lines = [line]
        elif line_clean.startswith("FECHA DE REGISTRO,N° HISTORIA CLÍNICA") or line_clean.startswith("FECHA DE REGISTRO,Nº HISTORIA CLÍNICA"):
            if current_section:
                sections[current_section] = current_lines
            current_section = "mascotas"
            current_lines = [line]
        else:
            if current_section:
                current_lines.append(line)

    if current_section:
        sections[current_section] = current_lines

    return sections

def clean_phone(val):
    if not val:
        return ""
    digits = re.sub(r"\D", "", str(val))
    if len(digits) >= 9:
        if digits.startswith("51") and len(digits) == 11:
            return digits[2:]
        return digits[:9]
    return digits

def clean_name(val):
    if not val:
        return ""
    s = str(val).strip()
    if "," in s:
        parts = s.split(",")
        return f"{parts[1].strip()} {parts[0].strip()}".strip()
    return re.sub(r"\s+", " ", s)

def process_sections(sections):
    db = {
        "clientes": [],
        "mascotas": [],
        "atenciones": [],
        "ventas": [],
        "seguimientos": [],
        "citas": []
    }

    # 1. Clientes
    if "clientes" in sections:
        csv_text = "\n".join(sections["clientes"])
        reader = csv.DictReader(io.StringIO(csv_text))
        seen_docs = set()
        for idx, row in enumerate(reader):
            doc = str(row.get("DOCUMENTO") or "").strip()
            nom = clean_name(row.get("NOMBRES Y APELLIDOS") or "")
            cel = clean_phone(row.get("TELÉFONOS") or "")
            dir_cli = str(row.get("DIRECCIÓN") or "").replace("|", "").strip()
            mascotas_raw = str(row.get("MASCOTAS") or "").strip()

            key = (doc, nom)
            if key not in seen_docs and (nom or doc):
                seen_docs.add(key)
                db["clientes"].append({
                    "id": len(db["clientes"]) + 1,
                    "documento": doc,
                    "nombre": nom,
                    "celular": cel,
                    "direccion": dir_cli,
                    "mascotas_resumen": mascotas_raw
                })

    # 2. Mascotas
    if "mascotas" in sections:
        csv_text = "\n".join(sections["mascotas"])
        reader = csv.DictReader(io.StringIO(csv_text))
        seen_hc = set()
        for row in reader:
            hc = str(row.get("N° HISTORIA CLÍNICA") or row.get("Nº HISTORIA CLÍNICA") or "").strip()
            nom = str(row.get("NOMBRE") or "").strip()
            esp = str(row.get("ESPECIE") or "").strip()
            raz = str(row.get("RAZA") or "").strip()
            sex = str(row.get("SEXO") or "").strip()
            nac = str(row.get("FECHA DE NACIMIENTO") or "").strip()
            prop = clean_name(row.get("PROPIETARIO") or "")
            cel = clean_phone(row.get("CELULAR DEL PROPIETARIO") or "")
            est = str(row.get("ESTERILIZACIÓN") or "").strip()

            if hc and hc not in seen_hc:
                seen_hc.add(hc)
                db["mascotas"].append({
                    "hc": hc,
                    "nombre": nom,
                    "especie": esp,
                    "raza": raz,
                    "sexo": sex,
                    "nacimiento": nac,
                    "propietario": prop,
                    "celular": cel,
                    "esterilizado": est
                })

    # 3. Historias Clínicas (Atenciones)
    if "historias" in sections:
        raw_lines = sections["historias"]
        # Buscar la fila de encabezado que contiene 'FECHA DE ATENCIÓN'
        header_idx = 0
        for i, l in enumerate(raw_lines):
            if "FECHA DE ATENCIÓN" in l:
                header_idx = i
                break
        csv_text = "\n".join(raw_lines[header_idx:])
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            fec = str(row.get("FECHA DE ATENCIÓN") or "").strip()
            tipo = str(row.get("TIPO DE ATENCIÓN") or "").strip()
            hc = str(row.get("HC") or "").strip()
            pac = str(row.get("PACIENTE") or "").strip()
            dx = str(row.get("DIAGNÓSTICO") or "").replace("\n", " ").strip()
            mot = str(row.get("MOTIVO DE ATENCIÓN") or row.get("ANAMNESIS") or "").replace("\n", " ").strip()
            tx = str(row.get("TRATAMIENTO") or "").replace("\n", " | ").strip()

            if hc or fec:
                db["atenciones"].append({
                    "fecha": fec,
                    "tipo": tipo,
                    "hc": hc,
                    "paciente": pac,
                    "motivo": mot,
                    "diagnostico": dx or mot,
                    "tratamiento": tx
                })

    # 4. Ventas por ítems o Comprobantes
    if "ventas_items" in sections:
        csv_text = "\n".join(sections["ventas_items"])
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            fec = str(row.get("FECHA DE EMISIÓN") or "").strip()
            doc_comp = str(row.get("DOCUMENTO") or "").replace("BOLETA DE VENTA ELECTRONICA: ", "").replace("FACTURA ELECTRONICA: ", "").strip()
            cli = clean_name(row.get("CLIENTE") or "")
            mas = str(row.get("MASCOTA") or "").strip()
            hc = str(row.get("Nº HC") or "").strip()
            concepto = str(row.get("CONCEPTO") or "Venta General").strip()
            tot = float(re.sub(r"[^0-9.]", "", str(row.get("TOTAL") or "0")) or 0)

            db["ventas"].append({
                "fecha": fec,
                "comprobante": doc_comp,
                "cliente": cli,
                "mascota": mas,
                "hc": hc,
                "item": concepto,
                "total": tot
            })
    elif "comprobantes" in sections:
        csv_text = "\n".join(sections["comprobantes"])
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            fec = str(row.get("FECHA DE EMISIÓN") or "").strip()
            comp = f"{row.get('SERIE')}-{row.get('NÚMERO')}".strip()
            cli = clean_name(row.get("DENOMINACIÓN") or "")
            tot = float(re.sub(r"[^0-9.]", "", str(row.get("TOTAL") or "0")) or 0)
            db["ventas"].append({
                "fecha": fec,
                "comprobante": comp,
                "cliente": cli,
                "item": "Venta General",
                "total": tot
            })

    # Generar algunos seguimientos automáticos de muestra a partir de las atenciones
    for atn in db["atenciones"][:8]:
        if atn.get("diagnostico") or atn.get("tipo") == "Vacuna":
            db["seguimientos"].push = db["seguimientos"].append({
                "fecha": atn["fecha"].split()[0] if atn["fecha"] else "2026-09-22",
                "cliente": "",  # Se vinculará por HC
                "mascota": atn["paciente"],
                "hc": atn["hc"],
                "motivo": f"Control post {atn['tipo']}: {atn['diagnostico'][:40]}..." if atn['diagnostico'] else f"Control de {atn['tipo']}",
                "estado": "Pendiente",
                "nota": "Control programado según historia clínica",
                "celular": ""
            })

    # Enlazar celulares y clientes a mascotas y atenciones
    cli_por_cel = {c["celular"]: c for c in db["clientes"] if c.get("celular")}
    cli_por_nom = {c["nombre"].lower(): c for c in db["clientes"] if c.get("nombre")}
    mas_por_hc = {m["hc"]: m for m in db["mascotas"] if m.get("hc")}

    for m in db["mascotas"]:
        # Buscar cliente
        c = cli_por_cel.get(m.get("celular")) or cli_por_nom.get((m.get("propietario") or "").lower())
        if c:
            m["id_cliente"] = c["id"]
            if not m.get("celular"):
                m["celular"] = c.get("celular")

    for s in db["seguimientos"]:
        m = mas_por_hc.get(s.get("hc"))
        if m:
            s["cliente"] = m.get("propietario")
            s["celular"] = m.get("celular")

    return db
