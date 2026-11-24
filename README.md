# 🐾 Pelitos Veterinaria - Sistema CRM & Gestión Integral VetPraxis

Sistema profesional de fidelización, administración de historias clínicas y seguimiento post-atención médica para **Pelitos Veterinaria**, diseñado para operar tanto en local como en la nube (Streamlit Community Cloud / Docker) sin dependencias externas complejas.

---

## 🔐 Seguridad y Autenticación Obligatoria
El acceso al panel CRM protege todos los datos clínicos y administrativos mediante contraseñas hasheadas (**PBKDF2-HMAC-SHA256**) y roles (`admin` / `operador`).

1. **Genere su hash de contraseña seguro** (nunca guarde contraseñas en texto plano ni las suba a Git):
   ```bash
   python -m modules.auth
   ```
2. **En local:** cree `.streamlit/secrets.toml` usando como plantilla `.streamlit/secrets.toml.example` (este archivo está excluido en `.gitignore`).
3. **En Streamlit Community Cloud:** pegue el mismo bloque `[auth.users.<usuario>]` en **Settings → Secrets**.
4. **En Docker:** pase las variables de entorno `PELITOS_ADMIN_USER` y `PELITOS_ADMIN_PASSWORD_HASH` (y opcionalmente `PELITOS_OPERATOR_USER` / `PELITOS_OPERATOR_PASSWORD_HASH`).

---

## 🚀 Despliegue en la Nube (Streamlit Cloud)
1. Conecte su repositorio en [Streamlit Community Cloud](https://share.streamlit.io).
2. Seleccione:
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Configure sus credenciales en **Settings → Secrets** según `.streamlit/secrets.toml.example`.
4. La aplicación detecta automáticamente entornos de solo lectura y gestiona respaldos de forma segura.

---

## 💻 Ejecución Local en Windows
1. Instale dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.streamlit/secrets.toml` (ver sección de Seguridad).
3. Haga doble clic en **`iniciar_crm.bat`** o ejecute:
   ```bash
   streamlit run app.py
   ```

---

## 📑 Soporte Certificado de Reportes VetPraxis
El sistema reconoce automáticamente los formatos exportados de VetPraxis:
1. **Clientes (`Reporte de Clientes.xlsx`):** Normaliza DNI/RUC/CE, teléfonos peruanos (+51) y nombres en formato `"APELLIDOS, NOMBRES"`.
2. **Mascotas (`Reporte de Mascotas.xlsx`):** Historias clínicas (HC), especies, razas, sexo, esterilización y datos del tutor.
3. **Historias Clínicas (`Reporte de Historias Clnicas - ....xlsx`):** Ignora metadatos en las filas iniciales y captura atenciones, diagnósticos y tratamientos.
4. **Ventas y Facturación:** Soporta tanto el **Reporte de Comprobantes** como el **Reporte de Ventas por Ítem**.
5. **Citas y Agenda:** Importa agendas en Excel/CSV o JSON extraído desde VetPraxis.

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
Instale dependencias de desarrollo y ejecute la suite de pruebas:
```bash
pip install -r requirements-dev.txt
pytest -v
```
