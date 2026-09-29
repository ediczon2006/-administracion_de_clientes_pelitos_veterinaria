"""
app.py - Interfaz Principal Streamlit
====================================
Sistema de Administración de Clientes y Fidelización - Pelitos Veterinaria
Integrado con exportaciones reales de VetPraxis y motor relacional SQLite.
"""
from datetime import date, datetime
import json
from pathlib import Path
import urllib.parse
import pandas as pd
import streamlit as st

from modules import (backup, buscador, config, dashboard, database, demo,
                     ficha, importador, normalizacion, reglas, relaciones,
                     seguimientos, validacion, vetpraxis_extractor)

# ---------------------------------------------------------------- Configuración de Página
st.set_page_config(
    page_title="Pelitos Veterinaria - CRM & Gestión Integral",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0D9488;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-segura {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-revision {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def obtener_conexion():
    """Abre conexión global persistente a la base SQLite."""
    return database.conectar()


conn = obtener_conexion()

# ---------------------------------------------------------------- Barra Lateral (Sidebar)
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1548767797-d8c844163c4c?w=400&q=80", use_container_width=True)
    st.markdown("### 🐾 Pelitos Veterinaria")
    st.caption("Sistema CRM & Gestión VetPraxis")
    
    menu = st.radio(
        "Menú de Navegación",
        [
            "🏠 Inicio",
            "📊 Dashboard & Métricas",
            "🔍 Búsqueda & Ficha 360°",
            "📞 Seguimientos CRM",
            "📥 Importar Reportes",
            "🌐 Integración VetPraxis",
            "⚠️ Calidad de Relaciones",
            "📑 Historial de Cargas",
            "⚙️ Protocolos Clínicos",
            "💾 Copias de Seguridad"
        ],
        index=0
    )
    
    st.markdown("---")
    # Indicador de estado de la base
    n_clientes = database.contar(conn, "clientes")
    n_mascotas = database.contar(conn, "mascotas")
    
    st.markdown(f"**Estado del Sistema:**")
    st.markdown(f"• 👥 **Clientes:** `{n_clientes:,}`")
    st.markdown(f"• 🐶 **Mascotas:** `{n_mascotas:,}`")
    
    if n_clientes == 0:
        st.warning("Base de datos vacía.")
        if st.button("🚀 Cargar Demo Ficticio", use_container_width=True):
            with st.spinner("Cargando datos ficticios de prueba..."):
                res_demo = demo.cargar_demo(conn, forzar=True)
                if res_demo["ok"]:
                    st.success("¡Datos demo cargados con éxito!")
                    st.rerun()
                else:
                    st.error(res_demo["mensaje"])

# ---------------------------------------------------------------- 1. INICIO
if menu == "🏠 Inicio":
    st.markdown('<div class="main-header">🐾 Panel Central - Pelitos Veterinaria</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Gestión de historias clínicas, cartera de clientes y fidelización post-atención.</div>', unsafe_allow_html=True)
    
    if n_clientes == 0 and n_mascotas == 0:
        st.info("💡 **Bienvenido al nuevo CRM de Pelitos Veterinaria.** Actualmente la base de datos se encuentra vacía. Puede importar sus reportes reales de VetPraxis desde la pestaña **'Importar Reportes'** o cargar datos de muestra con el botón en la barra lateral.")
    
    kpis = dashboard.calcular(conn)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Clientes Registrados", f"{kpis[0]['valor']:,}")
    with col2:
        st.metric("Mascotas / Historias", f"{kpis[1]['valor']:,}")
    with col3:
        st.metric("Atenciones Clínicas", f"{kpis[2]['valor']:,}")
    with col4:
        st.metric("Ventas / Comprobantes", f"{kpis[3]['valor']:,}")

    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("Citas en Agenda (VetPraxis)", f"{kpis[4]['valor']:,}")
    with col6:
        st.metric("Seguimientos Activos", f"{kpis[5]['valor']:,}")
    with col7:
        st.metric("Pacientes Reactivados", f"{kpis[6]['valor']:,}")

    st.markdown("---")
    st.subheader("⚡ Accesos Rápidos")
    cq1, cq2, cq3 = st.columns(3)
    with cq1:
        st.markdown("#### 📥 Ingesta VetPraxis")
        st.write("Cargue sus archivos exportados de Clientes, Mascotas, Atenciones o Ventas.")
    with cq2:
        st.markdown("#### 🔍 Búsqueda Rápida 360°")
        st.write("Consulte el expediente integral de un paciente por DNI, Nombre o HC.")
    with cq3:
        st.markdown("#### 📞 Contacto WhatsApp")
        st.write("Genere enlaces directos a WhatsApp para controles preventivos en un clic.")

# ---------------------------------------------------------------- 2. DASHBOARD
elif menu == "📊 Dashboard & Métricas":
    st.markdown('<div class="main-header">📊 Métricas Clínicas & Fidelización</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Indicadores clave de rendimiento clínico y transparencia analítica total.</div>', unsafe_allow_html=True)

    kpis = dashboard.calcular(conn)
    cols = st.columns(4)
    for idx, k in enumerate(kpis[:4]):
        with cols[idx % 4]:
            st.metric(k["nombre"], f"{k['valor']:,}")

    st.markdown("---")
    c_izq, c_der = st.columns(2)
    
    with c_izq:
        st.subheader("🐾 Distribución por Especie")
        df_esp = database.consultar(conn, """
            SELECT COALESCE(especie, 'NO ESPECIFICADO') AS Especie, COUNT(*) AS Total
            FROM mascotas
            GROUP BY especie
            ORDER BY Total DESC
            LIMIT 10
        """)
        if not df_esp.empty:
            st.dataframe(df_esp, use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros de mascotas aún.")

    with c_der:
        st.subheader("📞 Estado del Embudo de Seguimientos")
        df_seg = dashboard.seguimientos_por_estado(conn)
        if not df_seg.empty:
            st.dataframe(df_seg, use_container_width=True, hide_index=True)
        else:
            st.info("Sin seguimientos registrados.")

    st.markdown("---")
    st.subheader("💰 Resumen Financiero de Ventas")
    df_ventas = database.consultar(conn, """
        SELECT 
            COUNT(*) AS 'Comprobantes / Ítems',
            ROUND(SUM(total), 2) AS 'Monto Total Facturado (S/.)',
            ROUND(AVG(total), 2) AS 'Ticket Promedio (S/.)',
            MIN(fecha) AS 'Primera Venta',
            MAX(fecha) AS 'Última Venta'
        FROM ventas
    """)
    st.dataframe(df_ventas, use_container_width=True, hide_index=True)

    with st.expander("🔍 Auditoría de Consultas SQL (Transparencia Total)"):
        for k in kpis:
            st.markdown(f"**{k['nombre']}** ({k['fuente']}):")
            st.code(k["sql_conteo"], language="sql")
            st.caption(k["explicacion"])

# ---------------------------------------------------------------- 3. BÚSQUEDA & FICHA 360°
elif menu == "🔍 Búsqueda & Ficha 360°":
    st.markdown('<div class="main-header">🔍 Expediente Unificado del Paciente (Ficha 360°)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Búsqueda rápida por documento, celular, HC o nombre, con acceso directo a WhatsApp.</div>', unsafe_allow_html=True)

    col_filtro, col_txt = st.columns([1, 2])
    with col_filtro:
        tipo_filtro = st.selectbox("Criterio de Búsqueda", buscador.TIPOS_BUSQUEDA)
    with col_txt:
        termino = st.text_input("Ingrese término a buscar:", placeholder="Ej: 45678912, 987654321, 1001, Firulais...")

    if termino:
        df_resultados = buscador.buscar(conn, termino, tipo_filtro)
        if df_resultados.empty:
            st.warning("No se encontraron coincidencias para el criterio ingresado.")
        else:
            st.success(f"Se encontraron **{len(df_resultados)}** coincidencia(s):")
            
            # Selector de paciente
            opciones = {}
            for _, r in df_resultados.iterrows():
                label = f"🐾 {r['Mascota']} (HC: {r['HC']}) — Tutor: {r['Propietario']} (Cel: {r['Celular']})"
                opciones[label] = int(r["id_mascota"])

            seleccion_label = st.selectbox("Seleccione el paciente para abrir la Ficha 360°:", list(opciones.keys()))
            id_mascota_sel = opciones[seleccion_label]
            
            # Obtener registros completos
            mascota = ficha.obtener_mascota(conn, id_mascota_sel)
            cliente = ficha.obtener_cliente(conn, mascota["id_cliente"]) if mascota["id_cliente"] else None

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🐶 Datos del Paciente")
                st.markdown(f"**Nombre:** `{mascota['nombre']}`")
                st.markdown(f"**N° Historia Clínica:** `{mascota['hc']}`")
                st.markdown(f"**Especie / Raza:** `{mascota['especie'] or '—'}` / `{mascota['raza'] or '—'}`")
                st.markdown(f"**Sexo / Esterilizado:** `{mascota['sexo'] or '—'}` / `{mascota['esterilizacion'] or '—'}`")
                st.markdown(f"**Fecha Nacimiento:** `{mascota['fecha_nacimiento'] or '—'}`")
                st.markdown(f"**Estado de Vínculo:** `{mascota['estado_relacion']}`")

            with c2:
                st.markdown("### 👤 Datos del Propietario / Tutor")
                nombre_tutor = cliente["nombre"] if cliente else mascota["propietario_nombre"]
                doc_tutor = cliente["documento"] if cliente else mascota["propietario_documento"]
                cel_tutor = cliente["celular"] if cliente else mascota["propietario_celular"]
                
                st.markdown(f"**Nombre:** `{nombre_tutor or '—'}`")
                st.markdown(f"**Documento:** `{doc_tutor or '—'}`")
                st.markdown(f"**Teléfono / Celular:** `{cel_tutor or '—'}`")
                
                # Botón WhatsApp
                if cel_tutor:
                    _, wa_link = normalizacion.normalizar_telefono(cel_tutor)
                    if wa_link:
                        msg = f"Hola {nombre_tutor or ''}, le escribimos de Pelitos Veterinaria con relación a su engreído(a) {mascota['nombre']} 🐾."
                        wa_url = f"{wa_link}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 Enviar WhatsApp a {cel_tutor}</a>', unsafe_allow_html=True)
                    else:
                        st.caption("Número no compatible con enlace directo internacional.")

            st.markdown("---")
            tab_atn, tab_vnt, tab_cit, tab_seg = st.tabs([
                "📋 Atenciones Clínicas", "💰 Consumos / Ventas", "📅 Citas / Agenda", "📞 Seguimientos CRM"
            ])

            with tab_atn:
                df_atn = ficha.atenciones_de_mascota(conn, id_mascota_sel)
                if not df_atn.empty:
                    st.dataframe(df_atn, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay atenciones clínicas registradas para esta historia.")

            with tab_vnt:
                df_vnt = ficha.ventas_de_mascota(conn, id_mascota_sel)
                if not df_vnt.empty:
                    st.dataframe(df_vnt, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay registros de compras asociadas a este paciente.")

            with tab_cit:
                df_cit = ficha.citas_de_mascota_o_cliente(conn, id_mascota=id_mascota_sel, id_cliente=mascota["id_cliente"])
                if not df_cit.empty:
                    st.dataframe(df_cit, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay citas registradas en la agenda de VetPraxis.")

            with tab_seg:
                df_seg = seguimientos.listar(conn, id_mascota=id_mascota_sel)
                if not df_seg.empty:
                    st.dataframe(df_seg, use_container_width=True, hide_index=True)
                else:
                    st.info("Sin seguimientos activos para esta mascota.")

                st.markdown("#### ➕ Registrar Nuevo Seguimiento")
                with st.form(f"form_nuevo_seg_{id_mascota_sel}"):
                    c_mot, c_resp = st.columns(2)
                    with c_mot:
                        motivo_nuevo = st.selectbox("Motivo", config.MOTIVOS_SEGUIMIENTO)
                    with c_resp:
                        resp_nuevo = st.selectbox("Responsable", ["Recepción", "Médico Veterinario", "Administración"])
                    
                    obs_nuevo = st.text_area("Observaciones o notas iniciales:")
                    c_act, c_fec = st.columns(2)
                    with c_act:
                        prox_act = st.selectbox("Próxima Acción", config.ACCIONES_SEGUIMIENTO)
                    with c_fec:
                        prox_fec = st.date_input("Fecha Programada", value=date.today())
                    
                    if st.form_submit_button("Guardar Seguimiento"):
                        seguimientos.crear_seguimiento(
                            conn,
                            id_cliente=mascota["id_cliente"],
                            id_mascota=id_mascota_sel,
                            hc=mascota["hc"],
                            motivo=motivo_nuevo,
                            responsable=resp_nuevo,
                            proxima_accion=prox_act,
                            proxima_fecha=prox_fec,
                            observaciones=obs_nuevo
                        )
                        st.success("¡Seguimiento registrado exitosamente!")
                        st.rerun()

# ---------------------------------------------------------------- 4. SEGUIMIENTOS CRM
elif menu == "📞 Seguimientos CRM":
    st.markdown('<div class="main-header">📞 Gestión Operativa de Seguimientos CRM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Embudo de contactos, reactivación de pacientes inactivos y auditoría de llamadas.</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_estados = st.multiselect("Filtrar por Estado", config.ESTADOS_SEGUIMIENTO, default=config.ESTADOS_ABIERTOS)
    with col_f2:
        filtro_resp = st.selectbox("Responsable", ["Todos", "Recepción", "Médico Veterinario", "Administración"])
    with col_f3:
        solo_venc = st.checkbox("Mostrar únicamente casos vencidos")

    resp_param = None if filtro_resp == "Todos" else filtro_resp
    df_lista_seg = seguimientos.listar(conn, estados=filtro_estados, responsable=resp_param, solo_vencidos=solo_venc)

    if df_lista_seg.empty:
        st.info("No se encontraron seguimientos con los filtros seleccionados.")
    else:
        st.markdown(f"**Casos encontrados:** `{len(df_lista_seg)}`")
        st.dataframe(df_lista_seg.drop(columns=["id_cliente", "id_mascota"], errors="ignore"), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔄 Gestionar / Actualizar Estado de un Caso")
        lista_ids = df_lista_seg["ID"].tolist()
        id_sel = st.selectbox("Seleccione el ID de Seguimiento a gestionar:", lista_ids)

        if id_sel:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                nuevo_est = st.selectbox("Nuevo Estado", config.ESTADOS_SEGUIMIENTO)
                usuario_gest = st.text_input("Usuario / Operador", value="Recepción")
                resultado_gest = st.text_input("Resultado de la llamada / mensaje (ej: Confirmó asistencia, No respondió)")
            with col_g2:
                proxima_acc = st.selectbox("Siguiente Acción", config.ACCIONES_SEGUIMIENTO)
                proxima_fec = st.date_input("Fecha Siguiente Gestión", value=date.today())
                nota_gest = st.text_area("Nota detallada:")

            if st.button("💾 Guardar Transición de Estado"):
                seguimientos.cambiar_estado(
                    conn,
                    id_seguimiento=id_sel,
                    nuevo_estado=nuevo_est,
                    usuario=usuario_gest,
                    resultado=resultado_gest,
                    proxima_accion=proxima_acc,
                    proxima_fecha=proxima_fec,
                    nota=nota_gest
                )
                st.success(f"Caso #{id_sel} actualizado correctamente a '{nuevo_est}'.")
                st.rerun()

            st.markdown("#### 📜 Historial de Auditoría del Caso")
            df_hist = seguimientos.historial(conn, id_sel)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- 5. IMPORTAR REPORTES VETPRAXIS
elif menu == "📥 Importar Reportes":
    st.markdown('<div class="main-header">📥 Importador Certificado de Reportes VetPraxis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Compatible con los reportes originales de Clientes, Mascotas, Historias Clínicas, Ventas y Citas.</div>', unsafe_allow_html=True)

    st.markdown("""
    **Formatos aceptados directamente desde VetPraxis:**
    - 👥 **Reporte de Clientes:** `Reporte de Clientes.xlsx`
    - 🐾 **Reporte de Mascotas:** `Reporte de Mascotas.xlsx`
    - 📋 **Reporte de Historias Clínicas:** `Reporte de Historias Clnicas - ....xlsx`
    - 💰 **Reporte de Comprobantes o Ventas:** `Reporte de Comprobantes....xlsx` o `Reporte de ventas por items....xlsx`
    - 📅 **Reporte de Citas / Agenda:** Exportación de `events` o archivo CSV de agenda.
    """)

    archivo = st.file_uploader("Seleccione o arrastre el archivo de VetPraxis (.xlsx, .xls, .csv)", type=["xlsx", "xls", "csv"])

    if archivo is not None:
        contenido = archivo.read()
        nombre_archivo = archivo.name

        # Detección inteligente de tipo
        df_crudo = validacion.leer_archivo(contenido, nombre_archivo)
        tipo_detectado, conf = validacion.detectar_tipo_reporte(df_crudo)

        col_det, col_man = st.columns(2)
        with col_det:
            st.info(f"🔍 **Detección Automática:** `{tipo_detectado.upper()}` (Confianza: `{conf:.1%}`)")
        with col_man:
            tipo_final = st.selectbox(
                "Tipo de Reporte a Aplicar:",
                list(config.REPORTES.keys()),
                index=list(config.REPORTES.keys()).index(tipo_detectado) if tipo_detectado in config.REPORTES else 0
            )

        # Validación previa
        res_val = validacion.validar(contenido, nombre_archivo, tipo_final)
        
        if not res_val.ok:
            st.error("❌ **El archivo no superó la validación estructural:**")
            for err in res_val.errores:
                st.write(f"• {err}")
        else:
            st.success(f"✅ Archivo validado exitosamente. Encabezado en fila {res_val.fila_encabezado}, filas de datos: **{res_val.filas}**.")
            
            if res_val.advertencias:
                with st.expander("⚠️ Advertencias detectadas durante la lectura"):
                    for adv in res_val.advertencias:
                        st.write(f"• {adv}")

            with st.expander("👁️ Vista Previa del Mapeo de Columnas"):
                st.json(res_val.mapeo)
                st.dataframe(res_val.df.head(5), use_container_width=True)

            if st.button("🚀 Iniciar Ingesta & Deduplicación en Base de Datos", type="primary"):
                with st.spinner("Procesando datos y recalculando relaciones relacionales..."):
                    res_imp = importador.importar_archivo(
                        origen=contenido,
                        tipo_manual=tipo_final,
                        nombre_archivo=nombre_archivo,
                        hacer_backup=True
                    )
                    if res_imp["exito"]:
                        st.success(f"🎉 **Importación Exitosa:** {res_imp['filas_insertadas']} registros insertados, {res_imp['filas_actualizadas']} actualizados, {res_imp['duplicados']} duplicados omitidos.")
                    else:
                        st.error(f"Error durante la importación: {res_imp.get('errores')}")

    st.markdown("---")
    st.subheader("📥 Descargar Plantillas Oficiales")
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        if st.button("Descargar Plantilla Clientes"):
            st.download_button("Guardar Clientes CSV", "Código,Documento,Nombres y Apellidos,Celular,Correo,Dirección\n", file_name="plantilla_clientes.csv")
    with c_p2:
        if st.button("Descargar Plantilla Mascotas"):
            st.download_button("Guardar Mascotas CSV", "N° HC,Mascota,Especie,Raza,Sexo,DNI Propietario,Propietario,Celular Propietario\n", file_name="plantilla_mascotas.csv")
    with c_p3:
        if st.button("Descargar Plantilla Atenciones"):
            st.download_button("Guardar Atenciones CSV", "FECHA DE ATENCIÓN,TIPO DE ATENCIÓN,HC,PACIENTE,MOTIVO,DIAGNÓSTICO,TRATAMIENTO\n", file_name="plantilla_atenciones.csv")

# ---------------------------------------------------------------- 6. INTEGRACIÓN VETPRAXIS
elif menu == "🌐 Integración VetPraxis":
    st.markdown('<div class="main-header">🌐 Integración & Extractor de VetPraxis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cómo extraer y sincronizar la agenda de citas desde platform.vetpraxis.app/#/events</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 📌 Explicación Técnica de la URL de VetPraxis
    Cuando navegas a una URL como:
    `https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=%5B%222026-09-22T05:00:00.000Z%22,%222026-09-23T04:59:59.999Z%22%5D;type=;status=pending;client_id=`

    VetPraxis es una aplicación de una sola página (**SPA en Angular**). Los parámetros separados por punto y coma (`;`) son **parámetros de matriz (matrix parameters)** del enrutador de Angular:
    - **`#/events`**: Módulo de calendario y agenda de citas.
    - **`startAtRange`**: Rango de fechas ISO en formato UTC (`%5B%22...%22%5D` es `["2026-09-22T05:00:00.000Z", ...]`).
    - **`status=pending`**: Filtra eventos con estado pendiente.
    - **`page=1` / `sort=start_at`**: Paginación y orden cronológico.
    """)

    st.markdown("---")
    st.subheader("🔍 Analizador de URLs de VetPraxis")
    url_input = st.text_input("Pegue aquí una URL de eventos de VetPraxis:", value="https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=%5B%222026-09-22T05:00:00.000Z%22,%222026-09-23T04:59:59.999Z%22%5D;type=;status=pending;client_id=")
    
    if url_input:
        info_url = vetpraxis_extractor.parsear_url_eventos(url_input)
        if info_url.get("valida"):
            st.success("✅ URL de eventos válida de VetPraxis")
            c_u1, c_u2 = st.columns(2)
            with c_u1:
                st.markdown(f"**Módulo:** `{info_url['modulo']}`")
                st.markdown(f"**Estado Filtrado:** `{info_url['estado']}`")
                st.markdown(f"**Página:** `{info_url['pagina']}`")
            with c_u2:
                st.markdown(f"**Rango de Fechas Detectado:** `{', '.join(info_url['fechas_interpretadas']) if info_url['fechas_interpretadas'] else 'Sin rango'}`")
                st.markdown(f"**Orden:** `{info_url['orden']} ({info_url['direccion']})`")
        else:
            st.warning(info_url.get("error", "URL no reconocida."))

    st.markdown("---")
    st.subheader("🛠️ ¿Cómo extraer los datos sin requerir contraseña?")
    st.markdown("""
    Existen **3 métodos sencillos y seguros** para traer la información de citas a este CRM:
    
    #### Método 1: Exportación Nativa (Recomendado)
    En VetPraxis, dentro del módulo de Agenda o Reportes, haga clic en el botón de **'Exportar'** o icono de Excel/CSV y cargue el archivo resultante en la pestaña **'Importar Reportes'**.
    
    #### Método 2: Pestaña Red (Network) de F12
    1. Presione `F12` en su navegador mientras está en VetPraxis.
    2. Vaya a la pestaña **Network (Red)** y filtre por `Fetch/XHR`.
    3. Al cambiar de fecha o refrescar la agenda, verá una petición a `events` o `appointments`.
    4. Haga clic derecho -> **Copy Response** y péguelo en el campo JSON abajo.

    #### Método 3: Script de Consola JavaScript Automático
    Abra la consola de su navegador (`F12` -> `Console`) en VetPraxis y pegue este script para descargar sus citas en JSON al instante:
    """)

    script_js = vetpraxis_extractor.generar_script_consola_js()
    st.code(script_js, language="javascript")

    st.markdown("---")
    st.subheader("📥 Cargar Citas / Eventos Extraídos en JSON")
    json_input = st.text_area("Pegue el contenido JSON o array de eventos aquí:")
    if st.button("Procesar Eventos JSON"):
        if json_input.strip():
            try:
                datos_json = json.loads(json_input)
                res_ext = vetpraxis_extractor.importar_eventos_extraidos(conn, datos_json)
                if res_ext["ok"]:
                    st.success(f"¡Citas importadas exitosamente! {res_ext['resultado']['insertados']} agregadas.")
                else:
                    st.error(f"Error importando citas: {res_ext.get('error')}")
            except Exception as e:
                st.error(f"Error interpretando JSON: {e}")

# ---------------------------------------------------------------- 7. CALIDAD DE RELACIONES
elif menu == "⚠️ Calidad de Relaciones":
    st.markdown('<div class="main-header">⚠️ Calidad & Auditoría de Relaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitoreo de vínculos entre Mascotas, Tutores, Atenciones y Facturación.</div>', unsafe_allow_html=True)

    df_calidad = dashboard.calidad_relaciones(conn)
    st.dataframe(df_calidad, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🚨 Casos que Requieren Revisión Manual")
    
    df_rev_masc = database.consultar(conn, """
        SELECT id_mascota, hc AS HC, nombre AS Mascota, propietario_nombre AS 'Tutor en Reporte',
               propietario_celular AS Celular, propietario_documento AS DNI, alerta AS Alerta
        FROM mascotas
        WHERE estado_relacion IN ('REQUIERE REVISIÓN', 'SIN COINCIDENCIA')
        LIMIT 50
    """)
    if not df_rev_masc.empty:
        st.dataframe(df_rev_masc, use_container_width=True, hide_index=True)

        st.markdown("#### 🔗 Vincular Paciente a un Cliente Existente Manualmente")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            id_m_asig = st.selectbox("Seleccione ID de Mascota a vincular:", df_rev_masc["id_mascota"].tolist())
        with col_v2:
            clientes_disponibles = database.consultar(conn, "SELECT id_cliente, nombre, documento, celular FROM clientes ORDER BY nombre LIMIT 200")
            opcs_cli = {f"{r['nombre']} (DNI: {r['documento']}, Cel: {r['celular']})": r["id_cliente"] for _, r in clientes_disponibles.iterrows()}
            cli_sel_label = st.selectbox("Asignar al Cliente:", list(opcs_cli.keys()))
            id_c_asig = opcs_cli[cli_sel_label]

        if st.button("Confirmar Vinculación Manual"):
            relaciones.asignar_cliente_a_mascota(conn, id_m_asig, id_c_asig)
            st.success(f"Mascota vinculada exitosamente al cliente.")
            st.rerun()
    else:
        st.success("🎉 Todas las mascotas cuentan con un tutor identificado o relación segura.")

# ---------------------------------------------------------------- 8. HISTORIAL DE CARGAS
elif menu == "📑 Historial de Cargas":
    st.markdown('<div class="main-header">📑 Historial de Cargas & Trazabilidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Auditoría completa de archivos procesados, fechas y firmas criptográficas SHA-256.</div>', unsafe_allow_html=True)

    df_hist = database.consultar(conn, """
        SELECT id_importacion AS ID, tipo_reporte AS Reporte, archivo AS Archivo,
               fecha_importacion AS 'Fecha Importación', registros_leidos AS 'Leídos',
               insertados AS 'Insertados', duplicados AS 'Duplicados',
               hash_archivo AS 'Firma SHA-256'
        FROM importaciones
        ORDER BY id_importacion DESC
    """)
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no se han realizado importaciones de archivos.")

# ---------------------------------------------------------------- 9. PROTOCOLOS CLÍNICOS
elif menu == "⚙️ Protocolos Clínicos":
    st.markdown('<div class="main-header">⚙️ Protocolos Clínicos & Fidelización Preventiva</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Reglas configurables para la generación automatizada de recordatorios preventivos.</div>', unsafe_allow_html=True)

    reglas_cargadas = reglas.cargar_reglas()
    st.json(reglas_cargadas)

# ---------------------------------------------------------------- 10. COPIAS DE SEGURIDAD
elif menu == "💾 Copias de Seguridad":
    st.markdown('<div class="main-header">💾 Copias de Seguridad & Protección de Datos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Respaldos completos en caliente mediante SQLite nativo y restauración segura.</div>', unsafe_allow_html=True)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📦 Generar Nueva Copia de Seguridad Ahora"):
            ruta_bk = backup.crear_backup(conn, motivo="manual")
            st.success(f"Copia creada exitosamente: `{ruta_bk.name}`")
            st.rerun()

    backups = backup.listar_backups()
    if backups:
        st.markdown(f"**Copias de seguridad disponibles:** `{len(backups)}`")
        df_bk = pd.DataFrame([{
            "Archivo": b["nombre"],
            "Fecha": b["fecha"],
            "Tamaño": f"{b['tamano_bytes'] / 1024:.1f} KB"
        } for b in backups])
        st.dataframe(df_bk, use_container_width=True, hide_index=True)
    else:
        st.info("No se han generado copias de seguridad aún.")

    st.markdown("---")
    st.subheader("⚠️ Zona Peligrosa")
    with st.expander("🗑️ Limpiar / Reiniciar Base de Datos"):
        st.error("Esta acción eliminará todos los clientes, historias clínicas, ventas y seguimientos registrados.")
        confirmar = st.text_input("Escriba 'ELIMINAR' para confirmar:")
        if st.button("Ejecutar Limpieza Total"):
            if confirmar == "ELIMINAR":
                demo.limpiar_base_datos(conn)
                st.warning("Base de datos reseteada a 0 registros.")
                st.rerun()
            else:
                st.error("Confirmación incorrecta.")
