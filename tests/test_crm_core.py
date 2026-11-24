"""
test_crm_core.py - Suite Autocontenida de Calidad, Seguridad y Regresión
========================================================================
Valida todos los módulos críticos del CRM, autenticación, relaciones,
respaldos, referencias de app.py y controles de seguridad/accesibilidad de index.html.
"""
import ast
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pytest

from modules import (
    auth,
    backup,
    buscador,
    config,
    dashboard,
    database,
    demo,
    importador,
    normalizacion,
    reglas,
    relaciones,
    seguimientos,
    validacion,
    vetpraxis_extractor,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def entorno_aislado(tmp_path, monkeypatch):
    """Aísla por completo BD y carpetas de datos para cada prueba."""
    orig = tmp_path / "originales"
    proc = tmp_path / "procesados"
    bk = tmp_path / "backup"
    ej = tmp_path / "ejemplos"
    db_file = tmp_path / "test_crm.db"
    for d in (orig, proc, bk, ej):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "DATA_ORIGINALES", orig)
    monkeypatch.setattr(config, "DATA_PROCESADOS", proc)
    monkeypatch.setattr(config, "BACKUP_DIR", bk)
    monkeypatch.setattr(config, "DIR_EJEMPLOS", ej)
    monkeypatch.setattr(config, "DB_PATH", db_file)

    database.init_db(db_file)
    with database.get_db(db_file) as conn:
        yield conn, db_file


def test_autenticacion_pbkdf2_y_roles():
    pwd_hash = auth.generar_hash_contrasena("Pelitos2026!")
    assert pwd_hash.startswith("pbkdf2_sha256$")
    assert auth.verificar_contrasena("Pelitos2026!", pwd_hash) is True
    assert auth.verificar_contrasena("Incorrecta123", pwd_hash) is False
    assert auth.verificar_contrasena("", pwd_hash) is False

    with pytest.raises(ValueError):
        auth.generar_hash_contrasena("corta")

    usuarios = auth.cargar_usuarios(
        secrets_auth={},
        env={
            "PELITOS_ADMIN_USER": "jefe",
            "PELITOS_ADMIN_PASSWORD_HASH": pwd_hash,
            "PELITOS_OPERATOR_USER": "recep",
            "PELITOS_OPERATOR_PASSWORD_HASH": pwd_hash,
        },
    )
    perfil_admin = auth.autenticar_credenciales("jefe", "Pelitos2026!", usuarios)
    assert perfil_admin is not None and perfil_admin["rol"] == "admin"
    assert auth.autenticar_credenciales("jefe", "mala", usuarios) is None
    assert auth.autenticar_credenciales("noexiste", "Pelitos2026!", usuarios) is None

    assert auth.puede_acceder_seccion("admin", "💾 Copias de Seguridad") is True
    assert auth.puede_acceder_seccion("operador", "💾 Copias de Seguridad") is False
    assert auth.puede_acceder_seccion("operador", "🔍 Búsqueda & Ficha 360°") is True


def test_whatsapp_y_normalizacion():
    url = normalizacion.link_whatsapp("+51 987-654-321", "Hola Pelitos")
    assert url == "https://wa.me/51987654321?text=Hola%20Pelitos"
    assert normalizacion.normalizar_telefono("963-333-444") == ("963333444", True)
    assert normalizacion.normalizar_telefono("987654321 / 912345678") == ("987654321", True)
    assert normalizacion.normalizar_telefono("987 654 321 - 912 345 678") == ("987654321", True)
    assert normalizacion.link_whatsapp("062512345", "Hola") is None
    assert normalizacion.link_whatsapp("", "Hola") is None


def test_demo_buscador_y_clientes_sin_mascota(entorno_aislado):
    conn, _ = entorno_aislado
    res = demo.cargar_demo(conn, forzar=True)
    assert res["ok"] is True

    # Verificar alias de columnas usados por app.py
    df_busq = buscador.buscar(conn, "Firulais")
    assert not df_busq.empty
    assert "Paciente" in df_busq.columns
    assert "Tutor" in df_busq.columns

    # Mascota sin vínculo (Toby / Propietario Desconocido) debe aparecer en búsqueda inteligente
    df_sin_vinc = buscador.buscar(conn, "Propietario Desconocido")
    assert not df_sin_vinc.empty
    assert "Toby" in df_sin_vinc["Paciente"].tolist()

    # Cliente sin mascota (Agroveterinaria Ficticia SAC) debe ser localizable
    df_cli_sin_m = buscador.buscar_clientes_sin_mascota(conn, "Agroveterinaria")
    assert not df_cli_sin_m.empty


def test_importador_preserva_cero_y_dashboard(entorno_aislado):
    conn, _ = entorno_aislado
    df_v = pd.DataFrame([
        {
            "fecha": "2026-09-20",
            "comprobante": "B001-999",
            "cliente_documento": "45678912",
            "cliente_nombre": "Cliente Cero",
            "item": "Cortesía Desparasitación",
            "cantidad": 0,
            "precio": 0.0,
            "total": 0.0,
            "fila_excel": 2,
        }
    ])
    resumen = importador.importar(conn, "ventas", df_v, "ventas_cero.csv", b"csv", hacer_backup=False)
    assert resumen["insertados"] == 1
    row = conn.execute("SELECT cantidad, precio, total FROM ventas WHERE comprobante = 'B001-999'").fetchone()
    assert row["cantidad"] == 0.0
    assert row["precio"] == 0.0
    assert row["total"] == 0.0

    kpis = dashboard.calcular(conn)
    assert len(kpis) == 7
    with pytest.raises(ValueError):
        database.contar(conn, "tabla_invalida; DROP TABLE clientes")


def test_relaciones_manual_deshacer_y_homonimos(entorno_aislado):
    conn, _ = entorno_aislado
    demo.cargar_demo(conn, forzar=True)

    # Vincular mascota manualmente y deshacer sobre atenciones (regresión id_atencione)
    m = conn.execute("SELECT id_mascota FROM mascotas LIMIT 1").fetchone()
    c = conn.execute("SELECT id_cliente FROM clientes LIMIT 1").fetchone()
    relaciones.asignar_cliente_a_mascota(conn, m["id_mascota"], c["id_cliente"], responsable="AdminTest")
    m_post = conn.execute("SELECT estado_relacion FROM mascotas WHERE id_mascota = ?", (m["id_mascota"],)).fetchone()
    assert m_post["estado_relacion"] == config.MANUAL

    atn = conn.execute("SELECT id_atencion FROM atenciones LIMIT 1").fetchone()
    relaciones.asignar_manual(conn, "atenciones", atn["id_atencion"], "AdminTest", id_mascota=m["id_mascota"])
    relaciones.deshacer_manual(conn, "atenciones", atn["id_atencion"])

    # Verificar homónimo en ventas (María López Vega tiene 2 registros en demo) -> REQUIERE REVISIÓN
    v_hom = conn.execute("SELECT estado_relacion FROM ventas WHERE cliente_nombre = 'María López Vega'").fetchone()
    assert v_hom["estado_relacion"] == config.REVISION


def test_seguimientos_y_reglas_atenciones_y_ventas(entorno_aislado):
    conn, _ = entorno_aislado
    demo.cargar_demo(conn, forzar=True)

    m = conn.execute("SELECT id_mascota, id_cliente, hc FROM mascotas WHERE hc_norm = '1001'").fetchone()
    ayer = (date.today() - timedelta(days=2)).isoformat()
    sid = seguimientos.crear_seguimiento(
        conn, m["id_cliente"], m["id_mascota"], m["hc"],
        motivo=config.MOTIVOS_SEGUIMIENTO[0],
        responsable=config.RESPONSABLES[0],
        proxima_accion=config.PROXIMAS_ACCIONES[0],
        proxima_fecha=ayer,
        observaciones="Caso vencido prueba",
    )
    df_venc = seguimientos.listar(conn, solo_vencidos=True)
    assert sid in df_venc["ID"].tolist()

    seguimientos.cambiar_estado(conn, sid, "Reactivado", "Recepción", resultado="Asistió", nota="Confirmado")
    df_hist = seguimientos.historial(conn, sid)
    assert len(df_hist) >= 2

    # Probar reglas clínicas tanto de atenciones como de ventas
    reglas_list = reglas.cargar_reglas()
    regla_ventas = next(r for r in reglas_list if r["origen"] == "ventas")
    df_cand_v = reglas.candidatos(conn, regla_ventas, ignorar_estado=True)
    assert not df_cand_v.empty


def test_vetpraxis_extractor_json(entorno_aislado):
    conn, _ = entorno_aislado
    demo.cargar_demo(conn, forzar=True)

    assert "application/json" in vetpraxis_extractor.generar_script_consola_js()
    res_vacio = vetpraxis_extractor.importar_citas_json(conn, [])
    assert res_vacio["ok"] is False

    res_unico = vetpraxis_extractor.importar_citas_json(
        conn,
        {"start_at": "2026-09-25 10:00:00", "client_name": "Ana Torres Quispe", "patient_name": "Firulais", "hc": "1001"},
    )
    assert res_unico["ok"] is True
    assert res_unico["resumen"]["insertados"] == 1


def test_backup_listar_y_restaurar_seguro(entorno_aislado):
    conn, db_file = entorno_aislado
    demo.cargar_demo(conn, forzar=True)
    ruta_bk = backup.crear_backup(conn, motivo="prueba")
    assert ruta_bk.exists()

    lista = backup.listar_backups()
    assert len(lista) >= 1
    assert set(lista[0].keys()) >= {"nombre", "ruta", "fecha", "tamano_bytes"}

    # Path traversal debe ser rechazado
    with pytest.raises(FileNotFoundError):
        backup.restaurar_backup(conn, db_file)

    # Restauración legítima
    backup.restaurar_backup(conn, ruta_bk)
    assert db_file.exists()


def test_app_py_referencias_modulos_validas():
    """Verifica por AST que app.py no llame funciones o constantes inexistentes en modules/."""
    mod_symbols = {}
    for p in sorted((ROOT / "modules").glob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        syms = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                syms.add(node.name)
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        syms.add(t.id)
        mod_symbols[p.stem] = syms

    app_tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    rotas = []
    for node in ast.walk(app_tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in mod_symbols and node.attr not in mod_symbols[node.value.id]:
                rotas.append(f"app.py:{node.lineno} -> {node.value.id}.{node.attr}")
    assert not rotas, f"Referencias rotas en app.py: {rotas}"


def test_index_html_seguridad_accesibilidad_y_consistencia():
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    # Privacidad y metadatos
    assert 'name="robots" content="noindex, nofollow"' in html
    assert 'name="description"' in html
    assert 'rel="icon"' in html

    # Sin XSS conocido ni atributos obsoletos
    assert "sheet_to_html" not in html
    assert "frameborder=" not in html
    assert "sanitizarHtmlWord" in html
    assert "0x25" in html and "0x50" in html  # Verificación firma mágica %PDF-

    # Logo Base64 único (no duplicado)
    b64_matches = re.findall(r"data:image/png;base64,[A-Za-z0-9+/=]+", html)
    assert len(b64_matches) == 1

    # Un solo <h1> y sin IDs duplicados
    assert len(re.findall(r"<h1\b", html)) == 1
    ids = re.findall(r'''\bid=["']([^"']+)["']''', html)
    dups = {k: v for k, v in Counter(ids).items() if v > 1}
    assert not dups, f"IDs duplicados: {dups}"

    # Todos los getElementById deben existir en el HTML (salvo dinámicos)
    called_ids = set(re.findall(r'''getElementById\(["']([^"']+)["']\)''', html))
    missing = called_ids - set(ids)
    assert not missing, f"IDs faltantes en index.html: {missing}"

    # Todas las 13 unidades deben coincidir con normalizarIdUnidad()
    unidades = sorted(set(re.findall(r'''selUnidad\('([^']+)'\)''', html)))
    assert len(unidades) == 13
    for u in unidades:
        sin_tilde = "".join(c for c in unicodedata.normalize("NFD", u) if unicodedata.category(c) != "Mn")
        id_esperado = "side-u-" + re.sub(r"[^a-zA-Z0-9-]", "", re.sub(r"\s+", "-", sin_tilde))
        assert id_esperado in ids, f"Falta botón sidebar {id_esperado} para {u}"

    # Todos los controles <input>/<select>/<textarea> deben tener label for o aria-label
    for m in re.finditer(r"<(input|select|textarea)\b[^>]*>", html):
        tag_html = m.group(0)
        cid_m = re.search(r'''\bid=["']([^"']+)["']''', tag_html)
        cid = cid_m.group(1) if cid_m else None
        has_aria = "aria-label=" in tag_html
        has_label = bool(cid and re.search(rf'''<label[^>]*for=["']{re.escape(cid)}["']''', html))
        assert has_aria or has_label, f"Control sin etiqueta accesible: {tag_html}"

    # Todos los handlers inline deben existir como funciones JS definidas
    handlers = set(re.findall(r'''on(?:click|change|input|keydown)=["']([^"']+)["']''', html))
    called_fns = set()
    for expr in handlers:
        for fn in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", expr):
            if fn not in ("if", "event", "stopPropagation"):
                called_fns.add(fn)
    defined_fns = set(re.findall(r"(?:async\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", html))
    assert not (called_fns - defined_fns), f"Funciones JS no definidas: {called_fns - defined_fns}"

    # Balance de etiquetas estructurales HTML
    for tag in ("aside", "main", "header", "nav", "section", "table", "thead", "tbody", "html", "head", "body"):
        opens = len(re.findall(rf"<{tag}\b", html))
        closes = len(re.findall(rf"</{tag}>", html))
        assert opens == closes, f"Desbalance de etiqueta <{tag}>: open={opens}, close={closes}"
