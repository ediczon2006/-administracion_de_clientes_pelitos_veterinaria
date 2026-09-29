"""
demo.py - Datos de Prueba, Demostración y Ejemplos de VetPraxis
==============================================================
Genera datos ficticios para explorar el CRM en la nube o local sin datos reales.
"""
from datetime import datetime
from pathlib import Path
import pandas as pd

from modules import config, database, importador, seguimientos, validacion


def generar_archivos_ficticios_si_faltan():
    config.DIR_EJEMPLOS.mkdir(parents=True, exist_ok=True)
    archivos = [
        "01_reporte_clientes_FICTICIO.xlsx",
        "02_reporte_mascotas_FICTICIO.xlsx",
        "03_reporte_historias_FICTICIO.xlsx",
        "04_reporte_ventas_items_FICTICIO.xlsx",
        "05_ventas_SIN_COLUMNA_TOTAL_FICTICIO.xlsx"
    ]
    if all((config.DIR_EJEMPLOS / a).exists() for a in archivos):
        return

    def _guardar(nombre, titulo, filas, columnas):
        ruta = config.DIR_EJEMPLOS / nombre
        with pd.ExcelWriter(ruta, engine="openpyxl") as w:
            pd.DataFrame([[titulo], ["Generado: DATOS DE DEMOSTRACIÓN"]]).to_excel(w, index=False, header=False)
            pd.DataFrame(filas, columns=columnas).to_excel(w, index=False, startrow=3)

    clientes_cols = ["Código", "Documento", "Nombres y Apellidos", "Celular", "Correo", "Dirección", "Fecha Registro"]
    clientes = [
        ["C001", "45678912", "Ana Torres Quispe", "987 654 321", "ana@ejemplo.pe", "Jr. Ficticio 123", "10/01/2024"],
        ["C002", "40123456", "Luis Ramírez Soto", "962111222", "", "Av. Prueba 456", "15/02/2024"],
        ["C003", 1234567, "Rosa Huamán Díaz", "963-333-444", "", "", "03/03/2024"],
        ["C004", "", "Carlos Mendoza Ruiz", "955 000 111", "", "", "20/03/2024"],
        ["C005", "71234567", "María López Vega", "944222333", "", "", "01/04/2024"],
        ["C006", "72345678", "MARIA LOPEZ VEGA", "944222334", "", "", "02/04/2024"],
        ["C007", "43210987", "Pedro Castillo Neyra", "+51 987 654 321", "", "", "05/05/2024"],
        ["C001", "45678912", "Ana Torres Quispe", "987 654 321", "ana@ejemplo.pe", "Jr. Ficticio 123", "10/01/2024"],
        ["C009", "20456789012", "Agroveterinaria Ficticia SAC", "062512345", "", "", "06/06/2024"],
        ["C010", "46789123", "Jorge Paredes Ríos", "999888777", "", "", "07/07/2024"],
    ]
    _guardar("01_reporte_clientes_FICTICIO.xlsx", "VETPRAXIS - REPORTE DE CLIENTES", clientes, clientes_cols)

    mascotas_cols = ["N° HC", "Mascota", "Especie", "Raza", "Sexo", "Fecha Nacimiento", "Esterilizado",
                     "DNI Propietario", "Propietario", "Celular Propietario"]
    mascotas = [
        ["1001", "Firulais", "Canino", "Mestizo", "Macho", "12/05/2020", "Sí", "45678912", "Ana Torres Quispe", "987654321"],
        ["1002", "Luna", "Felino", "Siamés", "Hembra", "01/08/2021", "Sí", "40123456", "Luis Ramírez Soto", ""],
        ["1003", "Max", "Canino", "Labrador", "Macho", "20/11/2019", "No", "40123456", "Luis Ramírez Soto", ""],
        ["1004", "Michi", "Felino", "Mestizo", "Hembra", "", "No", "1234567", "Rosa Huamán Díaz", ""],
        ["1005", "Rocky", "Canino", "Pitbull", "Macho", "03/02/2022", "No", "", "Carlos Mendoza Ruiz", "955000111"],
        ["1006", "Nala", "Canino", "Shih Tzu", "Hembra", "", "", "", "María López Vega", ""],
        ["1007", "Toby", "Canino", "Poodle", "Macho", "", "", "99999999", "Propietario Desconocido", ""],
        ["1008", "Coco", "Ave", "Loro", "", "", "", "43210987", "Pedro Castillo Neyra", "987654321"],
        ["1009", "Kira", "Canino", "Husky", "Hembra", "15/09/2023", "No", "46789123", "Jorge Paredes Ríos", ""],
        ["001001", "Firulais", "Canino", "Mestizo", "Macho", "12/05/2020", "Sí", "45678912", "Ana Torres Quispe", "987654321"],
        ["1002", "Lucas", "Canino", "", "Macho", "", "", "40123456", "Luis Ramírez Soto", ""],
    ]
    _guardar("02_reporte_mascotas_FICTICIO.xlsx", "VETPRAXIS - REPORTE DE MASCOTAS", mascotas, mascotas_cols)

    hc_cols = ["Fecha", "N° Historia Clínica", "Paciente", "Tipo de Atención", "Motivo", "Diagnóstico", "Tratamiento", "Veterinario"]
    historias = [
        [datetime(2025, 1, 10), "1001", "Firulais", "Consulta", "Decaimiento", "Gastroenteritis leve", "Hidratación + Probióticos", "Dr. Pérez"],
        ["15/03/2025", "1001", "Firulais", "Vacuna", "Refuerzo anual", "", "Vacuna Óctuple Canina", "Dra. Gómez"],
        ["20/06/2025", "1001", "Firulais", "Consulta", "Control de piel", "Dermatitis alérgica", "Shampoo medicado + Meloxicam", "Dr. Pérez"],
        ["05/02/2025", "1002", "Luna", "Consulta", "Vómitos", "Gastritis aguda", "Omeprazol + Dieta blanda", "Dra. Gómez"],
        ["07/02/2025", "1002", "Luna", "Control", "Evolución", "Favorable", "Alta médica", "Dra. Gómez"],
        ["11/04/2025", "1003", "Max", "Cirugía", "Esterilización", "Procedimiento electivo", "Antibioticoterapia profiláctica", "Dr. Pérez"],
        ["01/05/2025", "1004", "Michifu", "Consulta", "Piel", "Ectoparásitos", "Antiparasitario externo", "Dr. Pérez"],
        ["02/05/2025", "1005", "Rocky", "Consulta", "Cojera", "Esguince leve", "Reposo + AINEs", "Dra. Gómez"],
    ]
    _guardar("03_reporte_historias_FICTICIO.xlsx", "VETPRAXIS - HISTORIAS CLÍNICAS", historias, hc_cols)

    ventas_cols = ["Fecha", "Comprobante", "DNI Cliente", "Cliente", "N° HC", "Mascota", "Categoría",
                   "Producto/Servicio", "Cantidad", "Precio Unitario", "Total"]
    ventas = [
        ["10/01/2025", "B001-100", "45678912", "Ana Torres Quispe", "1001", "Firulais", "Servicios", "Consulta general", 1, 50, 50],
        ["15/03/2025", "B001-120", "45678912", "Ana Torres Quispe", "1001", "Firulais", "Farmacia", "Antiparasitario Nexgard", 1, 35, 35],
        ["15/03/2025", "B001-120", "45678912", "Ana Torres Quispe", "1001", "Firulais", "Servicios", "Baño medicado y corte", 1, 40, 40],
        ["05/02/2025", "B001-110", "40123456", "Luis Ramírez Soto", "1002", "Luna", "Servicios", "Consulta médica", 1, 50, 50],
        ["06/02/2025", "B001-111", "40123456", "Luis Ramírez Soto", "", "", "Petshop", "Alimento ProPlan 3kg", 2, 45, 90],
        ["11/04/2025", "F001-020", "45678912", "Ana Torres Quispe", "1003", "Max", "Servicios", "Cirugía Ovariohisterectomía", 1, 300, 300],
        ["12/04/2025", "B001-130", "", "María López Vega", "", "", "Petshop", "Juguete mordedor", 1, 15, 15],
    ]
    _guardar("04_reporte_ventas_items_FICTICIO.xlsx", "VETPRAXIS - VENTAS POR ÍTEMS", ventas, ventas_cols)
    _guardar("05_ventas_SIN_COLUMNA_TOTAL_FICTICIO.xlsx", "VETPRAXIS - VENTAS POR ÍTEMS",
             [r[:-1] for r in ventas[:3]], ventas_cols[:-1])


def listar_archivos_ficticios():
    generar_archivos_ficticios_si_faltan()
    res = []
    for p in sorted(config.DIR_EJEMPLOS.glob("*.xlsx")):
        res.append((p.name, p, p.read_bytes()))
    return res


def cargar_demo(conn, forzar=False) -> dict:
    generar_archivos_ficticios_si_faltan()
    if database.contar(conn, "clientes") > 0 and not forzar:
        return {"ok": False, "mensaje": "La base ya contiene clientes registrados. Use forzar si desea recargar."}

    reportes = [
        ("clientes", "01_reporte_clientes_FICTICIO.xlsx"),
        ("mascotas", "02_reporte_mascotas_FICTICIO.xlsx"),
        ("historias", "03_reporte_historias_FICTICIO.xlsx"),
        ("ventas", "04_reporte_ventas_items_FICTICIO.xlsx")
    ]

    resumenes = {}
    for tipo, nombre in reportes:
        ruta = config.DIR_EJEMPLOS / nombre
        contenido = ruta.read_bytes()
        r = validacion.validar(contenido, nombre, tipo)
        if not r.ok:
            return {"ok": False, "mensaje": f"Error validando {nombre}: {r.errores}"}
        resumenes[tipo] = importador.importar(conn, tipo, r.df, nombre, contenido, len(r.filas_descartadas) if r.filas_descartadas is not None else 0)

    # Crear seguimientos de muestra
    try:
        m1 = conn.execute("SELECT * FROM mascotas WHERE hc_norm='1001'").fetchone()
        if m1:
            s1 = seguimientos.crear_seguimiento(
                conn, m1["id_cliente"], m1["id_mascota"], m1["hc"],
                "Reactivación de Paciente", "Recepción", "Contactado",
                "Tutor confirmó interés en control anual de vacunas",
                proxima_accion="Volver a llamar", observaciones="Paciente demo activo"
            )
            seguimientos.cambiar_estado(conn, s1, "Cita generada", "Recepción", "Agendado para el próximo sábado")

        m2 = conn.execute("SELECT * FROM mascotas WHERE hc_norm='1002'").fetchone()
        if m2:
            seguimientos.crear_seguimiento(
                conn, m2["id_cliente"], m2["id_mascota"], m2["hc"],
                "Control Post-Atención", "Médico Veterinario", "Pendiente",
                proxima_accion="Enviar WhatsApp", observaciones="Revisar evolución de gastritis"
            )
    except Exception:
        pass

    return {"ok": True, "mensaje": "Datos de demostración cargados exitosamente.", "detalles": resumenes}


def limpiar_base_datos(conn):
    with database.transaccion(conn):
        conn.execute("DELETE FROM seguimiento_historial")
        conn.execute("DELETE FROM seguimientos")
        conn.execute("DELETE FROM citas")
        conn.execute("DELETE FROM ventas")
        conn.execute("DELETE FROM atenciones")
        conn.execute("DELETE FROM mascotas")
        conn.execute("DELETE FROM clientes")
        conn.execute("DELETE FROM importaciones")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('clientes', 'mascotas', 'atenciones', 'ventas', 'citas', 'seguimientos', 'seguimiento_historial', 'importaciones')")
