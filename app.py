"""
app.py - Interfaz Principal Streamlit
====================================
Sistema de Administración de Clientes y Fidelización - Pelitos Veterinaria
Integrado con exportaciones reales de VetPraxis y motor relacional SQLite.
"""
from datetime import date
import html
import json
import urllib.parse

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from modules import (
    auth,
    backup,
    buscador,
    config,
    dashboard,
    database,
    demo,
    ficha,
    importador,
    normalizacion,
    reglas,
    relaciones,
    seguimientos,
    validacion,
    vetpraxis_extractor,
)

# ---------------------------------------------------------------- Configuración de Página
st.set_page_config(
    page_title="Pelitos Veterinaria - CRM & Gestión Integral",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados (preservando paleta oficial)
st.markdown(
    """
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0D9488;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #475569;
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
        background-color: #15803D;
        color: #FFFFFF !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .whatsapp-btn:hover {
        background-color: #166534;
    }
    .canal-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px;
        height: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def inicializar_esquema_bd():
    """Inicializa esquema SQLite una sola vez por proceso."""
    return database.init_db()


# ---------------------------------------------------------------- Control de Acceso
usuario_actual = auth.requerir_autenticacion(st)
if not usuario_actual:
    st.stop()

rol_actual = usuario_actual.get("rol", "operador")
nombre_usuario = usuario_actual.get("nombre", usuario_actual.get("usuario", "Operador"))

inicializar_esquema_bd()

MENUS_COMPLETOS = [
    "📁 Pelitos Docs (Biblioteca Empresarial)",
    "🏠 Inicio",
    "📊 Dashboard & Métricas",
    "🔍 Búsqueda & Ficha 360°",
    "📞 Seguimientos CRM",
    "📥 Importar Reportes",
    "🌐 Integración VetPraxis",
    "⚠️ Calidad de Relaciones",
    "📑 Historial de Cargas",
    "⚙️ Protocolos Clínicos",
    "💾 Copias de Seguridad",
]
menus_permitidos = [m for m in MENUS_COMPLETOS if auth.puede_acceder_seccion(rol_actual, m)]

# Mostrar notificación diferida si hubo una acción con st.rerun()
if st.session_state.get("flash_success"):
    st.toast(st.session_state.pop("flash_success"), icon="✅")

# Conexión SQLite segura por ejecución (WAL + cierre automático)
with database.get_db(inicializar=False) as conn:
    # ---------------------------------------------------------------- Barra Lateral (Sidebar)
    with st.sidebar:
        logo_local = config.BASE_DIR / "assets" / "logo_pelitos.png"
        if logo_local.exists():
            st.image(str(logo_local), use_container_width=True)
        st.markdown("### 🐾 Pelitos Veterinaria")
        st.caption("Sistema CRM & Gestión VetPraxis")

        if usuario_actual.get("modo_dev"):
            st.warning("Modo desarrollo local sin credenciales (`PELITOS_LOCAL_DEV_NO_AUTH=1`).")

        st.caption(f"👤 **{nombre_usuario}** (`{rol_actual.upper()}`)")
        if not usuario_actual.get("modo_dev"):
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                auth.cerrar_sesion(st)
                st.rerun()

        menu = st.radio(
            "Menú de Navegación",
            menus_permitidos,
            index=0,
        )

        st.markdown("---")
        n_clientes = database.contar(conn, "clientes")
        n_mascotas = database.contar(conn, "mascotas")

        st.markdown("**Estado del Sistema:**")
        st.markdown(f"• 👥 **Clientes:** `{n_clientes:,}`")
        st.markdown(f"• 🐶 **Mascotas:** `{n_mascotas:,}`")

        if n_clientes == 0:
            st.warning("Base de datos vacía.")
            if st.button("🚀 Cargar Demo Ficticio", use_container_width=True):
                with st.spinner("Cargando datos ficticios de prueba..."):
                    res_demo = demo.cargar_demo(conn, forzar=True)
                    if res_demo["ok"]:
                        st.session_state["flash_success"] = "¡Datos demo cargados con éxito!"
                        st.rerun()
                    else:
                        st.error(res_demo["mensaje"])

    # ---------------------------------------------------------------- 0. PELITOS DOCS
    if menu == "📁 Pelitos Docs (Biblioteca Empresarial)":
        html_file = config.BASE_DIR / "index.html"
        if html_file.exists():
            html_content = html_file.read_text(encoding="utf-8")
            components.html(html_content, height=940, scrolling=True)
        else:
            st.error("No se encontró el archivo index.html de Pelitos Docs.")

    # ---------------------------------------------------------------- 1. INICIO
    elif menu == "🏠 Inicio":
        st.markdown('<div class="main-header">🐾 Panel Central - Pelitos Veterinaria</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Gestión de historias clínicas, cartera de clientes y fidelización post-atención.</div>',
            unsafe_allow_html=True,
        )

        if n_clientes == 0 and n_mascotas == 0:
            st.info(
                "💡 **Bienvenido al CRM de Pelitos Veterinaria.** Actualmente la base de datos se encuentra vacía. "
                "Puede importar sus reportes reales de VetPraxis desde la pestaña **'Importar Reportes'** "
                "o cargar datos de muestra con el botón en la barra lateral."
            )

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
            st.write("Cargue sus archivos exportados de Clientes, Mascotas, Atenciones o Ventas desde el menú **Importar Reportes**.")
        with cq2:
            st.markdown("#### 🔍 Búsqueda Rápida 360°")
            st.write("Consulte el expediente integral de un paciente por DNI, Nombre o HC desde **Búsqueda & Ficha 360°**.")
        with cq3:
            st.markdown("#### 📞 Contacto WhatsApp")
            st.write("Genere enlaces directos a WhatsApp para controles preventivos en un clic.")

        if config.CANALES_ATENCION:
            st.markdown("---")
            st.subheader("📲 Canales Oficiales de Atención WhatsApp")
            cols_canales = st.columns(len(config.CANALES_ATENCION))
            for col_c, canal in zip(cols_canales, config.CANALES_ATENCION):
                with col_c:
                    wa_canal = f"https://wa.me/{canal['telefono_raw']}?text={urllib.parse.quote(canal['mensaje_wa'])}"
                    titulo_esc = html.escape(canal["titulo"])
                    cat_esc = html.escape(canal["categoria"])
                    desc_esc = html.escape(canal["descripcion"])
                    tel_esc = html.escape(canal["telefono"])
                    st.markdown(
                        f"""
                        <div class="canal-card">
                            <div style="font-size:0.75rem;font-weight:700;color:#475569;">{cat_esc}</div>
                            <div style="font-size:1.05rem;font-weight:700;color:#0F172A;margin:4px 0;">{titulo_esc}</div>
                            <p style="font-size:0.85rem;color:#475569;margin-bottom:10px;">{desc_esc}</p>
                            <a href="{wa_canal}" target="_blank" rel="noopener noreferrer" class="whatsapp-btn">
                                💬 {tel_esc}
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # ---------------------------------------------------------------- 2. DASHBOARD
    elif menu == "📊 Dashboard & Métricas":
        st.markdown('<div class="main-header">📊 Métricas Clínicas & Fidelización</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Indicadores clave de rendimiento clínico y transparencia analítica total.</div>',
            unsafe_allow_html=True,
        )

        kpis = dashboard.calcular(conn)
        cols = st.columns(4)
        for idx, k in enumerate(kpis[:4]):
            with cols[idx % 4]:
                st.metric(k["nombre"], f"{k['valor']:,}")

        st.markdown("---")
        c_izq, c_der = st.columns(2)

        with c_izq:
            st.subheader("🐾 Distribución por Especie")
            df_esp = database.consultar(
                conn,
                """
                SELECT COALESCE(especie, 'NO ESPECIFICADO') AS Especie, COUNT(*) AS Total
                FROM mascotas
                GROUP BY especie
                ORDER BY Total DESC
                LIMIT 10
                """,
            )
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
        st.caption(
            "Nota: si se importan simultáneamente el Reporte de Comprobantes y el Reporte de Ventas por Ítems "
            "para el mismo periodo, los totales agregados podrían incluir ambos orígenes."
        )
        df_ventas = database.consultar(
            conn,
            """
            SELECT
                COUNT(*) AS 'Comprobantes / Ítems',
                ROUND(COALESCE(SUM(total), 0), 2) AS 'Monto Total Facturado (S/.)',
                ROUND(COALESCE(AVG(total), 0), 2) AS 'Ticket Promedio (S/.)',
                COALESCE(MIN(fecha), '—') AS 'Primera Venta',
                COALESCE(MAX(fecha), '—') AS 'Última Venta'
            FROM ventas
            """,
        )
        st.dataframe(df_ventas, use_container_width=True, hide_index=True)

        with st.expander("🔍 Auditoría de Consultas SQL (Transparencia Total)"):
            for k in kpis:
                st.markdown(f"**{k['nombre']}** ({k['fuente']}):")
                st.code(k["sql_conteo"], language="sql")
                st.caption(k["explicacion"])

    # ---------------------------------------------------------------- 3. BÚSQUEDA & FICHA 360°
    elif menu == "🔍 Búsqueda & Ficha 360°":
        st.markdown('<div class="main-header">🔍 Expediente Unificado del Paciente (Ficha 360°)</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Búsqueda rápida por documento, celular, HC o nombre, con acceso directo a WhatsApp.</div>',
            unsafe_allow_html=True,
        )

        col_filtro, col_txt = st.columns([1, 2])
        with col_filtro:
            tipo_filtro = st.selectbox("Criterio de Búsqueda", buscador.TIPOS_BUSQUEDA)
        with col_txt:
            termino = st.text_input("Ingrese término a buscar:", placeholder="Ej: DNI, celular, HC o nombre...")

        if termino:
            df_resultados = buscador.buscar(conn, termino, tipo_filtro)
            df_clientes_sin_m = buscador.buscar_clientes_sin_mascota(conn, termino)

            if df_resultados.empty and df_clientes_sin_m.empty:
                st.warning("No se encontraron coincidencias para el criterio ingresado.")
            else:
                if not df_resultados.empty:
                    st.success(f"Se encontraron **{len(df_resultados)}** paciente(s):")

                    etiquetas_por_id = {}
                    ids_ordenados = []
                    for _, r in df_resultados.iterrows():
                        mid = int(r["id_mascota"])
                        ids_ordenados.append(mid)
                        etiquetas_por_id[mid] = (
                            f"🐾 {r['Paciente']} (HC: {r['HC'] or '—'}) — "
                            f"Tutor: {r['Tutor']} (Cel: {r['Celular']}) [ID #{mid}]"
                        )

                    id_mascota_sel = st.selectbox(
                        "Seleccione el paciente para abrir la Ficha 360°:",
                        ids_ordenados,
                        format_func=lambda mid: etiquetas_por_id[mid],
                    )

                    mascota = ficha.obtener_mascota(conn, id_mascota_sel)
                    if mascota is None:
                        st.error("No se pudo recuperar el expediente de la mascota seleccionada.")
                    else:
                        cliente = ficha.obtener_cliente(conn, mascota["id_cliente"]) if mascota["id_cliente"] else None

                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("### 🐶 Datos del Paciente")
                            st.markdown(f"**Nombre:** `{mascota['nombre'] or '—'}`")
                            st.markdown(f"**N° Historia Clínica:** `{mascota['hc'] or '—'}`")
                            st.markdown(f"**Especie / Raza:** `{mascota['especie'] or '—'}` / `{mascota['raza'] or '—'}`")
                            st.markdown(f"**Sexo / Esterilizado:** `{mascota['sexo'] or '—'}` / `{mascota['esterilizacion'] or '—'}`")
                            st.markdown(f"**Fecha Nacimiento:** `{mascota['fecha_nacimiento'] or '—'}`")
                            st.markdown(f"**Estado de Vínculo:** `{mascota['estado_relacion'] or '—'}`")

                        with c2:
                            st.markdown("### 👤 Datos del Propietario / Tutor")
                            nombre_tutor = cliente["nombre"] if cliente else mascota["propietario_nombre"]
                            doc_tutor = cliente["documento"] if cliente else mascota["propietario_documento"]
                            cel_tutor = cliente["celular"] if cliente else mascota["propietario_celular"]

                            st.markdown(f"**Nombre:** `{nombre_tutor or '—'}`")
                            st.markdown(f"**Documento:** `{doc_tutor or '—'}`")
                            st.markdown(f"**Teléfono / Celular:** `{cel_tutor or '—'}`")

                            if cel_tutor:
                                msg = (
                                    f"Hola {nombre_tutor or ''}, le escribimos de Pelitos Veterinaria "
                                    f"con relación a su engreído(a) {mascota['nombre'] or ''} 🐾."
                                )
                                wa_url = normalizacion.link_whatsapp(cel_tutor, msg)
                                if wa_url:
                                    cel_esc = html.escape(str(cel_tutor))
                                    st.markdown(
                                        f'<a href="{wa_url}" target="_blank" rel="noopener noreferrer" class="whatsapp-btn">'
                                        f"💬 Enviar WhatsApp a {cel_esc}</a>",
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    st.caption("Número no compatible con enlace directo de WhatsApp (requiere celular peruano de 9 dígitos).")

                        st.markdown("---")
                        tab_atn, tab_vnt, tab_cit, tab_seg = st.tabs(
                            [
                                "📋 Atenciones Clínicas",
                                "💰 Consumos / Ventas",
                                "📅 Citas / Agenda",
                                "📞 Seguimientos CRM",
                            ]
                        )

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
                            if mascota["id_cliente"]:
                                df_vnt_cli = ficha.ventas_cliente_sin_mascota(conn, mascota["id_cliente"])
                                if not df_vnt_cli.empty:
                                    st.caption("Otras compras del tutor sin mascota específica:")
                                    st.dataframe(df_vnt_cli, use_container_width=True, hide_index=True)

                        with tab_cit:
                            df_cit = ficha.citas_de_mascota_o_cliente(
                                conn, id_mascota=id_mascota_sel, id_cliente=mascota["id_cliente"]
                            )
                            if not df_cit.empty:
                                st.dataframe(df_cit, use_container_width=True, hide_index=True)
                            else:
                                st.info("No hay citas registradas en la agenda de VetPraxis.")

                        with tab_seg:
                            df_seg = seguimientos.listar(conn, id_mascota=id_mascota_sel)
                            if not df_seg.empty:
                                st.dataframe(
                                    df_seg.drop(columns=["id_cliente", "id_mascota"], errors="ignore"),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                st.info("Sin seguimientos activos para esta mascota.")

                            st.markdown("#### ➕ Registrar Nuevo Seguimiento")
                            with st.form(f"form_nuevo_seg_{id_mascota_sel}"):
                                c_mot, c_resp = st.columns(2)
                                with c_mot:
                                    motivo_nuevo = st.selectbox("Motivo", config.MOTIVOS_SEGUIMIENTO)
                                with c_resp:
                                    resp_nuevo = st.selectbox("Responsable", config.RESPONSABLES)

                                obs_nuevo = st.text_area("Observaciones o notas iniciales:")
                                c_act, c_fec = st.columns(2)
                                with c_act:
                                    prox_act = st.selectbox("Próxima Acción", config.PROXIMAS_ACCIONES)
                                with c_fec:
                                    prox_fec = st.date_input("Fecha Programada", value=date.today())

                                if st.form_submit_button("Guardar Seguimiento", type="primary"):
                                    try:
                                        seguimientos.crear_seguimiento(
                                            conn,
                                            id_cliente=mascota["id_cliente"],
                                            id_mascota=id_mascota_sel,
                                            hc=mascota["hc"],
                                            motivo=motivo_nuevo,
                                            responsable=resp_nuevo,
                                            proxima_accion=prox_act,
                                            proxima_fecha=prox_fec,
                                            observaciones=obs_nuevo.strip(),
                                        )
                                        st.session_state["flash_success"] = "¡Seguimiento registrado exitosamente!"
                                        st.rerun()
                                    except ValueError as err:
                                        st.error(str(err))

                if not df_clientes_sin_m.empty:
                    st.markdown("---")
                    st.subheader(f"👤 Clientes sin mascotas vinculadas ({len(df_clientes_sin_m)})")
                    st.dataframe(
                        df_clientes_sin_m.drop(columns=["id_cliente"], errors="ignore"),
                        use_container_width=True,
                        hide_index=True,
                    )

    # ---------------------------------------------------------------- 4. SEGUIMIENTOS CRM
    elif menu == "📞 Seguimientos CRM":
        st.markdown('<div class="main-header">📞 Gestión Operativa de Seguimientos CRM</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Embudo de contactos, reactivación de pacientes inactivos y auditoría de llamadas.</div>',
            unsafe_allow_html=True,
        )

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_estados = st.multiselect(
                "Filtrar por Estado", config.ESTADOS_SEGUIMIENTO, default=config.ESTADOS_ABIERTOS
            )
        with col_f2:
            filtro_resp = st.selectbox("Responsable", ["Todos"] + config.RESPONSABLES)
        with col_f3:
            solo_venc = st.checkbox("Mostrar únicamente casos vencidos")

        resp_param = None if filtro_resp == "Todos" else filtro_resp
        df_lista_seg = seguimientos.listar(
            conn, estados=filtro_estados, responsable=resp_param, solo_vencidos=solo_venc
        )

        if df_lista_seg.empty:
            st.info("No se encontraron seguimientos con los filtros seleccionados.")
        else:
            st.markdown(f"**Casos encontrados:** `{len(df_lista_seg)}`")
            st.dataframe(
                df_lista_seg.drop(columns=["id_cliente", "id_mascota"], errors="ignore"),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("---")
            st.subheader("🔄 Gestionar / Actualizar Estado de un Caso")
            etiquetas_seg = {
                int(r["ID"]): f"#{int(r['ID'])} — {r['Mascota']} ({r['Cliente']}) | {r['Estado']}"
                for _, r in df_lista_seg.iterrows()
            }
            id_sel = st.selectbox(
                "Seleccione el seguimiento a gestionar:",
                list(etiquetas_seg.keys()),
                format_func=lambda sid: etiquetas_seg[sid],
            )

            if id_sel:
                with st.form(f"form_transicion_seg_{id_sel}"):
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        nuevo_est = st.selectbox("Nuevo Estado", config.ESTADOS_SEGUIMIENTO)
                        usuario_gest = st.text_input("Usuario / Operador", value=nombre_usuario)
                        resultado_gest = st.text_input(
                            "Resultado de la llamada / mensaje (ej: Confirmó asistencia, No respondió)"
                        )
                    with col_g2:
                        proxima_acc = st.selectbox("Siguiente Acción", config.PROXIMAS_ACCIONES)
                        proxima_fec = st.date_input("Fecha Siguiente Gestión", value=date.today())
                        nota_gest = st.text_area("Nota detallada:")

                    guardar_trans = st.form_submit_button("💾 Guardar Transición de Estado", type="primary")

                if guardar_trans:
                    if not usuario_gest.strip():
                        st.error("Debe indicar el nombre del usuario u operador responsable.")
                    else:
                        try:
                            seguimientos.cambiar_estado(
                                conn,
                                id_seguimiento=id_sel,
                                nuevo_estado=nuevo_est,
                                usuario=usuario_gest.strip(),
                                resultado=resultado_gest.strip(),
                                proxima_accion=proxima_acc,
                                proxima_fecha=proxima_fec,
                                nota=nota_gest.strip(),
                            )
                            st.session_state["flash_success"] = f"Caso #{id_sel} actualizado a '{nuevo_est}'."
                            st.rerun()
                        except ValueError as err:
                            st.error(str(err))

                st.markdown("#### 📜 Historial de Auditoría del Caso")
                df_hist = seguimientos.historial(conn, id_sel)
                st.dataframe(df_hist, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------------- 5. IMPORTAR REPORTES VETPRAXIS
    elif menu == "📥 Importar Reportes":
        st.markdown('<div class="main-header">📥 Importador Certificado de Reportes VetPraxis</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Compatible con los reportes originales de Clientes, Mascotas, Historias Clínicas, Ventas y Citas.</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        **Formatos aceptados directamente desde VetPraxis:**
        - 👥 **Reporte de Clientes:** `Reporte de Clientes.xlsx`
        - 🐾 **Reporte de Mascotas:** `Reporte de Mascotas.xlsx`
        - 📋 **Reporte de Historias Clínicas:** `Reporte de Historias Clnicas - ....xlsx`
        - 💰 **Reporte de Comprobantes o Ventas:** `Reporte de Comprobantes....xlsx` o `Reporte de ventas por items....xlsx`
        - 📅 **Reporte de Citas / Agenda:** Exportación de `events` o archivo CSV de agenda.
        """
        )

        archivo = st.file_uploader(
            "Seleccione o arrastre el archivo de VetPraxis (.xlsx, .xls, .csv)",
            type=["xlsx", "xls", "csv"],
        )

        if archivo is not None:
            contenido = archivo.getvalue()
            nombre_archivo = archivo.name

            try:
                df_crudo = validacion.leer_archivo(contenido, nombre_archivo)
                tipo_detectado, conf = validacion.detectar_tipo_reporte(df_crudo)
            except Exception as exc:
                st.error(
                    f"❌ No se pudo leer el archivo `{nombre_archivo}` ({exc}). "
                    "Verifique que sea un archivo Excel (.xlsx/.xls) o CSV válido y no esté dañado."
                )
                df_crudo = None
                tipo_detectado, conf = "desconocido", 0.0

            if df_crudo is not None:
                col_det, col_man = st.columns(2)
                with col_det:
                    st.info(f"🔍 **Detección Automática:** `{tipo_detectado.upper()}` (Confianza: `{conf:.1%}`)")
                with col_man:
                    claves_rep = list(config.REPORTES.keys())
                    tipo_final = st.selectbox(
                        "Tipo de Reporte a Aplicar:",
                        claves_rep,
                        index=claves_rep.index(tipo_detectado) if tipo_detectado in claves_rep else 0,
                    )

                res_val = validacion.validar(contenido, nombre_archivo, tipo_final)

                if not res_val.ok:
                    st.error("❌ **El archivo no superó la validación estructural:**")
                    for err in res_val.errores:
                        st.write(f"• {err}")
                else:
                    st.success(
                        f"✅ Archivo validado exitosamente. Encabezado en fila {res_val.fila_encabezado}, "
                        f"filas de datos: **{res_val.filas}**."
                    )

                    if res_val.advertencias:
                        with st.expander("⚠️ Advertencias detectadas durante la lectura"):
                            for adv in res_val.advertencias:
                                st.write(f"• {adv}")

                    with st.expander("👁️ Vista Previa del Mapeo de Columnas"):
                        st.json(res_val.mapeo)
                        st.dataframe(res_val.df.head(5), use_container_width=True)

                    if st.button("🚀 Iniciar Ingesta & Deduplicación en Base de Datos", type="primary"):
                        with st.spinner("Procesando datos y recalculando relaciones relacionales..."):
                            descartados = (
                                len(res_val.filas_descartadas) if res_val.filas_descartadas is not None else 0
                            )
                            try:
                                resumen = importador.importar(
                                    conn=conn,
                                    tipo=tipo_final,
                                    df=res_val.df,
                                    nombre_archivo=nombre_archivo,
                                    contenido=contenido,
                                    descartados=descartados,
                                    hacer_backup=True,
                                )
                                st.session_state["flash_success"] = (
                                    f"Importación exitosa: {resumen['insertados']} insertados, "
                                    f"{resumen['actualizados']} actualizados, {resumen['duplicados']} duplicados omitidos."
                                )
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Error durante la importación: {exc}")

        st.markdown("---")
        st.subheader("📥 Descargar Plantillas Oficiales")
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            st.download_button(
                "📄 Plantilla Clientes (CSV)",
                data="Código,Documento,Nombres y Apellidos,Celular,Correo,Dirección\n",
                file_name="plantilla_clientes.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c_p2:
            st.download_button(
                "🐾 Plantilla Mascotas (CSV)",
                data="N° HC,Mascota,Especie,Raza,Sexo,DNI Propietario,Propietario,Celular Propietario\n",
                file_name="plantilla_mascotas.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c_p3:
            st.download_button(
                "📋 Plantilla Atenciones (CSV)",
                data="FECHA DE ATENCIÓN,TIPO DE ATENCIÓN,HC,PACIENTE,MOTIVO,DIAGNÓSTICO,TRATAMIENTO\n",
                file_name="plantilla_atenciones.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ---------------------------------------------------------------- 6. INTEGRACIÓN VETPRAXIS
    elif menu == "🌐 Integración VetPraxis":
        st.markdown('<div class="main-header">🌐 Integración & Extractor de VetPraxis</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Cómo extraer y sincronizar la agenda de citas desde platform.vetpraxis.app/#/events</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        ### 📌 Explicación Técnica de la URL de VetPraxis
        Cuando navegas a una URL como:
        `https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=%5B%222026-09-22T05:00:00.000Z%22,%222026-09-23T04:59:59.999Z%22%5D;type=;status=pending;client_id=`

        VetPraxis es una aplicación de una sola página (**SPA en Angular**). Los parámetros separados por punto y coma (`;`) son **parámetros de matriz (matrix parameters)** del enrutador de Angular:
        - **`#/events`**: Módulo de calendario y agenda de citas.
        - **`startAtRange`**: Rango de fechas ISO en formato UTC (`%5B%22...%22%5D` es `["2026-09-22T05:00:00.000Z", ...]`).
        - **`status=pending`**: Filtra eventos con estado pendiente.
        - **`page=1` / `sort=start_at`**: Paginación y orden cronológico.
        """
        )

        st.markdown("---")
        st.subheader("🔍 Analizador de URLs de VetPraxis")
        url_input = st.text_input(
            "Pegue aquí una URL de eventos de VetPraxis:",
            value="https://platform.vetpraxis.app/#/events;sort=start_at;direction=desc;page=1;startAtRange=%5B%222026-09-22T05:00:00.000Z%22,%222026-09-23T04:59:59.999Z%22%5D;type=;status=pending;client_id=",
        )

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
                    rango_txt = ", ".join(info_url["fechas_interpretadas"]) if info_url["fechas_interpretadas"] else "Sin rango"
                    st.markdown(f"**Rango de Fechas Detectado:** `{rango_txt}`")
                    st.markdown(f"**Orden:** `{info_url['orden']} ({info_url['direccion']})`")
            else:
                st.warning(info_url.get("error", "URL no reconocida."))

        st.markdown("---")
        st.subheader("🛠️ ¿Cómo extraer los datos sin requerir contraseña?")
        st.markdown(
            """
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
        """
        )

        script_js = vetpraxis_extractor.generar_script_consola_js()
        st.code(script_js, language="javascript")

        st.markdown("---")
        st.subheader("📥 Cargar Citas / Eventos Extraídos en JSON")
        json_input = st.text_area("Pegue el contenido JSON o array de eventos aquí:")
        if st.button("Procesar Eventos JSON", type="primary"):
            if not json_input.strip():
                st.warning("Pegue un contenido JSON válido antes de procesar.")
            else:
                try:
                    datos_json = json.loads(json_input)
                    res_ext = vetpraxis_extractor.importar_citas_json(conn, datos_json)
                    if res_ext["ok"]:
                        resumen = res_ext["resumen"]
                        st.session_state["flash_success"] = (
                            f"¡Citas importadas! {resumen['insertados']} agregadas, "
                            f"{resumen['duplicados']} duplicadas omitidas."
                        )
                        st.rerun()
                    else:
                        errores_txt = "; ".join(res_ext.get("errores", ["Error desconocido."]))
                        st.error(f"Error importando citas: {errores_txt}")
                except json.JSONDecodeError as exc:
                    st.error(f"JSON inválido (línea {exc.lineno}, columna {exc.colno}): {exc.msg}")
                except Exception as exc:
                    st.error(f"Error procesando eventos JSON: {exc}")

    # ---------------------------------------------------------------- 7. CALIDAD DE RELACIONES
    elif menu == "⚠️ Calidad de Relaciones":
        st.markdown('<div class="main-header">⚠️ Calidad & Auditoría de Relaciones</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Monitoreo de vínculos entre Mascotas, Tutores, Atenciones y Facturación.</div>',
            unsafe_allow_html=True,
        )

        df_calidad = dashboard.calidad_relaciones(conn)
        st.dataframe(df_calidad, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🚨 Casos que Requieren Revisión Manual")

        df_rev_masc = database.consultar(
            conn,
            """
            SELECT id_mascota, hc AS HC, nombre AS Mascota, propietario_nombre AS 'Tutor en Reporte',
                   propietario_celular AS Celular, propietario_documento AS DNI, alerta AS Alerta
            FROM mascotas
            WHERE estado_relacion IN ('REQUIERE REVISIÓN', 'SIN COINCIDENCIA')
            LIMIT 100
            """,
        )
        if not df_rev_masc.empty:
            st.dataframe(df_rev_masc, use_container_width=True, hide_index=True)

            st.markdown("#### 🔗 Vincular Paciente a un Cliente Existente Manualmente")
            filtro_cli_vinc = st.text_input(
                "Filtrar cliente por nombre, DNI o celular:",
                placeholder="Escriba parte del nombre, DNI o teléfono para buscar entre todos los clientes...",
            )

            if filtro_cli_vinc.strip():
                q_norm = normalizacion.normalizar_texto(filtro_cli_vinc) or ""
                q_raw = filtro_cli_vinc.strip()
                clientes_disponibles = database.consultar(
                    conn,
                    """
                    SELECT id_cliente, nombre, documento, celular
                    FROM clientes
                    WHERE nombre_norm LIKE ? OR documento_norm LIKE ? OR celular_norm LIKE ? OR nombre LIKE ?
                    ORDER BY nombre
                    LIMIT 200
                    """,
                    (f"%{q_norm}%", f"%{q_raw}%", f"%{q_raw}%", f"%{q_raw}%"),
                )
            else:
                clientes_disponibles = database.consultar(
                    conn,
                    "SELECT id_cliente, nombre, documento, celular FROM clientes ORDER BY nombre",
                )

            if clientes_disponibles.empty:
                st.warning("No hay clientes registrados que coincidan con el filtro actual.")
            else:
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    etiquetas_m = {
                        int(r["id_mascota"]): f"#{int(r['id_mascota'])} — {r['Mascota']} (HC: {r['HC'] or '—'})"
                        for _, r in df_rev_masc.iterrows()
                    }
                    id_m_asig = st.selectbox(
                        "Seleccione mascota a vincular:",
                        list(etiquetas_m.keys()),
                        format_func=lambda mid: etiquetas_m[mid],
                    )
                with col_v2:
                    etiquetas_c = {
                        int(r["id_cliente"]): f"{r['nombre']} (DNI: {r['documento'] or '—'}, Cel: {r['celular'] or '—'}) [#{int(r['id_cliente'])}]"
                        for _, r in clientes_disponibles.iterrows()
                    }
                    id_c_asig = st.selectbox(
                        "Asignar al Cliente:",
                        list(etiquetas_c.keys()),
                        format_func=lambda cid: etiquetas_c[cid],
                    )

                if st.button("Confirmar Vinculación Manual", type="primary"):
                    relaciones.asignar_manual(
                        conn,
                        tabla="mascotas",
                        id_registro=id_m_asig,
                        responsable=nombre_usuario,
                        id_cliente=id_c_asig,
                    )
                    st.session_state["flash_success"] = "Mascota vinculada exitosamente al cliente."
                    st.rerun()
        else:
            st.success("🎉 Todas las mascotas cuentan con un tutor identificado o relación segura.")

    # ---------------------------------------------------------------- 8. HISTORIAL DE CARGAS
    elif menu == "📑 Historial de Cargas":
        st.markdown('<div class="main-header">📑 Historial de Cargas & Trazabilidad</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Auditoría completa de archivos procesados, fechas y firmas criptográficas SHA-256.</div>',
            unsafe_allow_html=True,
        )

        df_hist = database.consultar(
            conn,
            """
            SELECT id_importacion AS ID, tipo_reporte AS Reporte, archivo AS Archivo,
                   fecha_importacion AS 'Fecha Importación', registros_leidos AS 'Leídos',
                   insertados AS 'Insertados', duplicados AS 'Duplicados',
                   hash_archivo AS 'Firma SHA-256'
            FROM importaciones
            ORDER BY id_importacion DESC
            """,
        )
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no se han realizado importaciones de archivos.")

    # ---------------------------------------------------------------- 9. PROTOCOLOS CLÍNICOS
    elif menu == "⚙️ Protocolos Clínicos":
        if rol_actual != "admin":
            st.error("Acceso restringido: requiere rol de Administrador.")
            st.stop()

        st.markdown('<div class="main-header">⚙️ Protocolos Clínicos & Fidelización Preventiva</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Reglas configurables para la generación automatizada de recordatorios preventivos.</div>',
            unsafe_allow_html=True,
        )

        reglas_cargadas = reglas.cargar_reglas()
        if not reglas_cargadas:
            st.info("No se encontraron protocolos clínicos configurados en `data/reglas_clinicas.json`.")
        else:
            df_reglas = pd.DataFrame(
                [
                    {
                        "ID": r.get("id", "—"),
                        "Protocolo": r.get("nombre", "—"),
                        "Origen": r.get("origen", "—"),
                        "Criterio": r.get("criterio_tipo", "—"),
                        "Intervalo (días)": r.get("intervalo_dias", 0),
                        "Tolerancia (días)": r.get("tolerancia_previa_dias", 0),
                        "Aprobado por": r.get("aprobado_por") or "Pendiente",
                        "Estado": "Activa" if reglas.regla_aplicable(r) else "Inactiva / Sin aprobar",
                    }
                    for r in reglas_cargadas
                ]
            )
            st.dataframe(df_reglas, use_container_width=True, hide_index=True)

            st.markdown("#### 🔍 Simulación / Consulta de Candidatos")
            regla_por_id = {r["id"]: r for r in reglas_cargadas if r.get("id")}
            sel_regla_id = st.selectbox(
                "Seleccione un protocolo para previsualizar pacientes candidatos:",
                list(regla_por_id.keys()),
                format_func=lambda rid: f"{regla_por_id[rid].get('nombre', rid)} ({regla_por_id[rid].get('origen')})",
            )
            regla_sel = regla_por_id[sel_regla_id]
            incluir_inactivas = st.checkbox("Simular aunque la regla esté pendiente de aprobación médica", value=False)
            df_cand = reglas.candidatos(conn, regla_sel, ignorar_estado=incluir_inactivas)
            if not df_cand.empty:
                st.success(f"Candidatos detectados: **{len(df_cand)}**")
                st.dataframe(df_cand.drop(columns=["id_mascota"], errors="ignore"), use_container_width=True, hide_index=True)
            else:
                if not reglas.regla_aplicable(regla_sel) and not incluir_inactivas:
                    st.info("Este protocolo está inactivo o pendiente de aprobación veterinaria.")
                else:
                    st.info("No hay pacientes candidatos que cumplan el intervalo configurado actualmente.")

            with st.expander("📄 Ver definición JSON cruda"):
                st.json(reglas_cargadas)

    # ---------------------------------------------------------------- 10. COPIAS DE SEGURIDAD
    elif menu == "💾 Copias de Seguridad":
        if rol_actual != "admin":
            st.error("Acceso restringido: requiere rol de Administrador.")
            st.stop()

        st.markdown('<div class="main-header">💾 Copias de Seguridad & Protección de Datos</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Respaldos completos en caliente mediante SQLite nativo y restauración segura.</div>',
            unsafe_allow_html=True,
        )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("📦 Generar Nueva Copia de Seguridad Ahora", type="primary"):
                ruta_bk = backup.crear_backup(conn, motivo="manual")
                st.session_state["flash_success"] = f"Copia creada exitosamente: {ruta_bk.name}"
                st.rerun()

        backups_disp = backup.listar_backups()
        if backups_disp:
            st.markdown(f"**Copias de seguridad disponibles:** `{len(backups_disp)}`")
            df_bk = pd.DataFrame(
                [
                    {
                        "Archivo": b["nombre"],
                        "Fecha": b["fecha"],
                        "Tamaño": f"{b['tamano_bytes'] / 1024:.1f} KB",
                    }
                    for b in backups_disp
                ]
            )
            st.dataframe(df_bk, use_container_width=True, hide_index=True)

            with st.expander("♻️ Restaurar una Copia de Seguridad"):
                st.warning(
                    "Se creará automáticamente un respaldo preventivo del estado actual antes de restaurar."
                )
                bk_por_nombre = {b["nombre"]: b["ruta"] for b in backups_disp}
                bk_sel = st.selectbox("Seleccione respaldo a restaurar:", list(bk_por_nombre.keys()))
                confirmar_rest = st.checkbox("Confirmo que deseo reemplazar la base actual con esta copia.")
                if st.button("Restaurar Copia Seleccionada"):
                    if not confirmar_rest:
                        st.error("Marque la casilla de confirmación antes de restaurar.")
                    else:
                        backup.restaurar_backup(conn, bk_por_nombre[bk_sel])
                        inicializar_esquema_bd.clear()
                        st.session_state["flash_success"] = f"Base de datos restaurada desde {bk_sel}."
                        st.rerun()
        else:
            st.info("No se han generado copias de seguridad aún.")

        st.markdown("---")
        st.subheader("⚠️ Zona Peligrosa")
        with st.expander("🗑️ Limpiar / Reiniciar Base de Datos"):
            st.error("Esta acción eliminará todos los clientes, historias clínicas, ventas y seguimientos registrados.")
            confirmar_chk = st.checkbox("Entiendo que se generará un backup preventivo y se vaciará la BD activa.")
            confirmar = st.text_input("Escriba 'ELIMINAR' para confirmar:")
            if st.button("Ejecutar Limpieza Total"):
                if confirmar == "ELIMINAR" and confirmar_chk:
                    backup.crear_backup(conn, motivo="antes_de_limpieza_total")
                    demo.limpiar_base_datos(conn)
                    st.session_state["flash_success"] = "Base de datos reseteada a 0 registros (respaldo preventivo guardado)."
                    st.rerun()
                else:
                    st.error("Confirmación incorrecta. Marque la casilla y escriba exactamente ELIMINAR.")
