# 🐾 Pelitos Veterinaria - Sistema CRM & Gestión Integral VetPraxis

Sistema profesional de fidelización, administración de historias clínicas y seguimiento post-atención médica para **Pelitos Veterinaria**, diseñado para operar tanto en local como en la nube (Streamlit Community Cloud / Docker) sin dependencias externas complejas.

---

## 🚀 Despliegue en la Nube (Streamlit Cloud)
El proyecto está completamente preparado para ser compartido mediante GitHub:
1. Conecte su repositorio: `https://github.com/ediczon2006/administracion_de_clientes_pelitos_veterinaria`
2. En [Streamlit Community Cloud](https://share.streamlit.io), seleccione:
   - **Repository:** `ediczon2006/administracion_de_clientes_pelitos_veterinaria`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. ¡Listo! La aplicación detecta automáticamente entornos de solo lectura y gestiona los respaldos de forma segura.

---

## 💻 Ejecución Local en Windows
1. Haga doble clic en el archivo **`iniciar_crm.bat`**
2. O ejecute desde la terminal:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📑 Soporte Certificado de Reportes VetPraxis
El sistema reconoce automáticamente (100% de precisión) los formatos reales exportados de VetPraxis:
1. **Clientes (`Reporte de Clientes.xlsx`):** Normaliza DNI/RUC/CE, teléfonos peruanos (+51) y nombres en formato `"APELLIDOS, NOMBRES"`.
2. **Mascotas (`Reporte de Mascotas.xlsx`):** Historias clínicas (HC), especies, razas, sexo, esterilización y datos del tutor.
3. **Historias Clínicas (`Reporte de Historias Clnicas - ....xlsx`):** Ignora metadatos en las filas iniciales y captura atenciones, diagnósticos y tratamientos.
4. **Ventas y Facturación:** Soporta tanto el **Reporte de Comprobantes** (`Reporte de Comprobantes....xlsx`) como el **Reporte de Ventas por Ítem** (`Reporte de ventas por items....xlsx`).
5. **Citas y Agenda:** Importa agendas y eventos extraídos.

---

## 🌐 Extracción de Datos de VetPraxis Events URL
Para URLs como:
`https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=%5B%222026-09-22T05:00:00.000Z%22,%222026-09-23T04:59:59.999Z%22%5D;type=;status=pending;client_id=`

- **Estructura Angular:** Los parámetros separados por punto y coma (`;`) son matrix parameters de Angular (`startAtRange`, `status`, etc.).
- **Cómo extraer citas:**
  1. **Directo en VetPraxis:** Botón "Exportar" a Excel/CSV.
  2. **Consola F12:** Ejecute el script provisto en la sección **"Integración VetPraxis"** del CRM para descargar un JSON estructurado con sus citas.
  3. Pegue el JSON en el CRM para consolidar las citas en su expediente 360°.

---

## 🧪 Pruebas Automatizadas
Para ejecutar la suite de pruebas con los reportes reales:
```bash
pytest tests/test_vetpraxis_real.py -v
```
