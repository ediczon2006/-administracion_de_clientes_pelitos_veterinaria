"""
config.py - CONFIGURACIÓN CENTRAL DE PELITOS CRM INTELLIGENCE
=============================================================
Definición de rutas, catálogos, sinónimos y columnas de exportación de VetPraxis.
"""
from pathlib import Path
import tempfile

# ---------------------------------------------------------------------------
# 1. RUTAS Y DIRECTORIOS (Resilientes para Local, Docker y Streamlit Cloud)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

def _es_escribible(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        prueba = p / ".write_test"
        prueba.touch()
        prueba.unlink()
        return True
    except (OSError, PermissionError):
        return False

# Si la raíz del proyecto es de solo lectura (como en ciertos servidores cloud), usamos tempfile
_raiz_datos = BASE_DIR if _es_escribible(BASE_DIR / "database") else Path(tempfile.gettempdir()) / "pelitos_crm"

DATA_ORIGINALES = _raiz_datos / "data" / "originales"
DATA_PROCESADOS = _raiz_datos / "data" / "procesados"
DB_DIR = _raiz_datos / "database"
DB_PATH = DB_DIR / "pelitos_crm.db"
BACKUP_DIR = _raiz_datos / "backup"
REGLAS_PATH = BASE_DIR / "data" / "reglas_clinicas.json"
DIR_EJEMPLOS = BASE_DIR / "data" / "ejemplos_ficticios"

for _carpeta in (DATA_ORIGINALES, DATA_PROCESADOS, DB_DIR, BACKUP_DIR, DIR_EJEMPLOS):
    _carpeta.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 2. DEFINICIÓN DE REPORTES Y COLUMNAS DE VETPRAXIS
# ---------------------------------------------------------------------------
ALIAS_HC = [
    "hc", "n hc", "nro hc", "historia clinica", "n historia clinica",
    "nro historia clinica", "numero historia clinica", "historia", "cod hc", "n expediente"
]

REPORTES = {
    "clientes": {
        "titulo": "Reporte de Clientes",
        "columnas": {
            "codigo_origen": {
                "alias": ["codigo", "cod", "codigo cliente", "id cliente", "cod cliente", "codigo tutor", "id tutor", "origen"],
                "requerida": False, "critica": False
            },
            "documento": {
                "alias": ["documento", "dni", "nro documento", "n documento", "numero documento", "num documento",
                          "doc", "dni ruc", "ruc dni", "nro doc", "documento identidad", "doc identidad", "ruc",
                          "ce", "carnet de extranjeria", "pasaporte", "numero de documento de identidad"],
                "requerida": True, "critica": False
            },
            "nombre": {
                "alias": ["cliente", "nombre", "nombres", "nombre cliente", "propietario", "razon social",
                          "nombres y apellidos", "apellidos y nombres", "nombre completo", "tutor", "nombre tutor",
                          "tutores", "denominacion"],
                "requerida": True, "critica": True
            },
            "apellidos": {
                "alias": ["apellidos", "apellido"],
                "requerida": False, "critica": False
            },
            "celular": {
                "alias": ["celular", "telefono", "telefonos", "movil", "tel", "celular 1", "telefono 1",
                          "nro celular", "whatsapp", "celular whatsapp", "telefono movil", "telefono tutor",
                          "celular tutor", "telefonos tutor", "celulares"],
                "requerida": True, "critica": False
            },
            "email": {
                "alias": ["email", "correo", "e mail", "correo electronico", "correo tutor", "email tutor"],
                "requerida": False, "critica": False
            },
            "direccion": {
                "alias": ["direccion", "domicilio", "direccion cliente", "direccion tutor", "zona"],
                "requerida": False, "critica": False
            },
            "fecha_registro": {
                "alias": ["fecha registro", "fecha de registro", "fecha alta", "registrado", "fecha creacion", "fecha de creacion"],
                "requerida": False, "critica": False
            },
        },
        "al_menos_una": [],
        "filas_encabezado_max": 15,
    },
    "mascotas": {
        "titulo": "Reporte de Mascotas",
        "columnas": {
            "hc": {"alias": ALIAS_HC, "requerida": True, "critica": True},
            "nombre": {"alias": ["mascota", "paciente", "nombre mascota", "nombre paciente", "nombre"], "requerida": True, "critica": True},
            "especie": {"alias": ["especie", "tipo animal", "tipo de mascota"], "requerida": False, "critica": False},
            "raza": {"alias": ["raza"], "requerida": False, "critica": False},
            "sexo": {"alias": ["sexo", "genero"], "requerida": False, "critica": False},
            "fecha_nacimiento": {"alias": ["fecha nacimiento", "fecha de nacimiento", "nacimiento", "f nacimiento", "f nac"], "requerida": False, "critica": False},
            "esterilizacion": {"alias": ["esterilizado", "esterilizada", "esterilizacion", "castrado", "castrada"], "requerida": False, "critica": False},
            "propietario_documento": {"alias": ["documento propietario", "dni propietario", "documento", "dni", "doc propietario", "documento cliente", "dni cliente", "documento tutor", "dni tutor", "doc tutor", "numero de documento de identidad"], "requerida": False, "critica": False},
            "propietario_nombre": {"alias": ["propietario", "cliente", "dueno", "nombre propietario", "nombre cliente", "tutor", "nombre tutor", "denominacion"], "requerida": False, "critica": False},
            "propietario_celular": {"alias": ["celular", "telefono", "telefonos", "celular propietario", "celular del propietario", "telefono propietario", "telefono del propietario", "movil", "celular tutor", "telefono tutor", "whatsapp tutor"], "requerida": False, "critica": False},
        },
        "al_menos_una": [["propietario_documento", "propietario_celular", "propietario_nombre"]],
        "filas_encabezado_max": 15,
    },
    "historias": {
        "titulo": "Reporte de Historias Clínicas (Atenciones)",
        "columnas": {
            "hc": {"alias": ALIAS_HC, "requerida": True, "critica": True},
            "fecha": {"alias": ["fecha", "fecha atencion", "fecha de atencion", "f atencion", "fecha consulta"], "requerida": True, "critica": True},
            "tipo_atencion": {"alias": ["tipo atencion", "tipo de atencion", "tipo", "servicio", "atencion", "motivo atencion"], "requerida": True, "critica": False},
            "paciente": {"alias": ["paciente", "mascota", "nombre mascota"], "requerida": False, "critica": False},
            "motivo": {"alias": ["motivo", "motivo atencion", "motivo de atencion", "motivo consulta", "motivo de consulta", "anamnesis", "sintomas", "consulta"], "requerida": False, "critica": False},
            "diagnostico": {"alias": ["diagnostico", "diagnosticos", "dx", "examen clinico", "examen clinico extendido", "diagnostico presuntivo", "diagnostico definitivo"], "requerida": False, "critica": False},
            "tratamiento": {"alias": ["tratamiento", "tratamientos", "indicaciones", "plan terapeutico", "receta", "medicacion"], "requerida": False, "critica": False},
            "veterinario": {"alias": ["veterinario", "medico", "atendido por", "doctor", "profesional", "medico veterinario"], "requerida": False, "critica": False},
        },
        "al_menos_una": [],
        "filas_encabezado_max": 15,
    },
    "ventas": {
        "titulo": "Reporte de Ventas e Ingresos (Por Ítems o Comprobantes)",
        "columnas": {
            "fecha": {"alias": ["fecha", "fecha emision", "fecha de emision", "fecha venta", "fecha de contabilizacion"], "requerida": True, "critica": True},
            "comprobante": {"alias": ["comprobante", "nro comprobante", "n comprobante", "documento venta", "serie numero", "serie y numero", "boleta factura", "ticket", "factura", "boleta", "codigo de comprobante", "codigo comprobante", "serie", "numero"], "requerida": False, "critica": False},
            "cliente_documento": {"alias": ["documento cliente", "dni cliente", "documento", "dni", "ruc dni", "nro documento", "doc tutor", "dni tutor", "numero de documento de identidad", "numero documento de identidad", "doc identidad"], "requerida": False, "critica": False},
            "cliente_nombre": {"alias": ["cliente", "nombre cliente", "razon social", "propietario", "tutor", "nombre tutor", "denominacion"], "requerida": False, "critica": False},
            "hc": {"alias": ALIAS_HC, "requerida": False, "critica": False},
            "mascota": {"alias": ["mascota", "paciente"], "requerida": False, "critica": False},
            "categoria": {"alias": ["categoria", "familia", "linea", "grupo", "rubro", "tipo"], "requerida": False, "critica": False},
            "item": {"alias": ["item", "producto", "producto servicio", "descripcion", "producto o servicio", "articulo", "concepto", "servicio"], "requerida": False, "critica": False},
            "cantidad": {"alias": ["cantidad", "cant"], "requerida": False, "critica": False},
            "precio": {"alias": ["precio", "precio unitario", "p unitario", "pu", "valor unitario", "costo"], "requerida": False, "critica": False},
            "total": {"alias": ["total", "importe", "subtotal", "monto", "importe total", "total venta", "pagado"], "requerida": True, "critica": False},
        },
        "al_menos_una": [["cliente_documento", "cliente_nombre", "hc"]],
        "filas_encabezado_max": 15,
    },
    "citas": {
        "titulo": "Reporte de Citas / Agenda (VetPraxis Events)",
        "columnas": {
            "fecha": {"alias": ["fecha", "fecha inicio", "start at", "inicio", "fecha cita"], "requerida": True, "critica": True},
            "cliente_nombre": {"alias": ["cliente", "propietario", "tutor", "nombre tutor", "denominacion"], "requerida": False, "critica": False},
            "cliente_documento": {"alias": ["documento", "dni", "numero de documento de identidad"], "requerida": False, "critica": False},
            "celular": {"alias": ["celular", "telefono", "telefonos"], "requerida": False, "critica": False},
            "paciente": {"alias": ["paciente", "mascota"], "requerida": False, "critica": False},
            "hc": {"alias": ALIAS_HC, "requerida": False, "critica": False},
            "tipo_evento": {"alias": ["tipo", "tipo evento", "servicio", "tipo de cita"], "requerida": False, "critica": False},
            "estado": {"alias": ["estado", "status"], "requerida": False, "critica": False},
            "veterinario": {"alias": ["veterinario", "profesional", "doctor"], "requerida": False, "critica": False},
            "motivo": {"alias": ["motivo", "observaciones", "notas", "descripcion"], "requerida": False, "critica": False},
        },
        "al_menos_una": [["cliente_nombre", "paciente", "hc"]],
        "filas_encabezado_max": 15,
    }
}

# ---------------------------------------------------------------------------
# 3. CRM Y SEGUIMIENTOS OPERATIVOS
# ---------------------------------------------------------------------------
ESTADOS_SEGUIMIENTO = [
    "Pendiente", "Contactado", "Respondió", "No respondió", "Cita generada",
    "Asistió", "Reactivado", "No interesado", "Número incorrecto", "Cerrado",
]
ESTADOS_ABIERTOS = ["Pendiente", "Contactado", "Respondió", "No respondió", "Cita generada"]

MOTIVOS_SEGUIMIENTO = [
    "Reactivación de Paciente", "Control Post-Atención", "Recordatorio Vacunación",
    "Control Antiparasitario", "Estética y Baño", "Chequeo Preventivo", "Cita Agendada", "Otro"
]
PROXIMAS_ACCIONES = ["Volver a llamar", "Enviar WhatsApp", "Confirmar cita", "Revisar evolución", "Cerrar caso", "Ninguna"]
RESPONSABLES = ["Recepción", "Administración", "Médico Veterinario", "Gerencia"]

CRITERIO_REACTIVADO = "Pacientes o tutores contactados que han vuelto a atenderse o han generado cita en los últimos 30 días."

# ---------------------------------------------------------------------------
# 4. NORMALIZACIÓN
# ---------------------------------------------------------------------------
COMPLETAR_DNI_7_DIGITOS = True
QUITAR_CEROS_HC_NUMERICA = True
CODIGO_PAIS = "51"
MAX_BACKUPS_AUTOMATICOS = 30
VALORES_VACIOS = {"", "-", "--", "nan", "none", "null", "n/a", "na", "s/n", "sin dato", "no registra", "."}

# Clasificación de relaciones
SEGURA = "COINCIDENCIA SEGURA"
PROBABLE = "COINCIDENCIA PROBABLE"
REVISION = "REQUIERE REVISIÓN"
SIN = "SIN COINCIDENCIA"
MANUAL = "SEGURA (MANUAL)"
