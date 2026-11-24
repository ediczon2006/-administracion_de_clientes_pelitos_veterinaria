"""
auth.py - Autenticación Segura y Control de Roles para Pelitos CRM
==================================================================
Protege el acceso a datos sensibles (clientes, mascotas, historias clínicas, ventas)
mediante contraseñas hasheadas con PBKDF2-HMAC-SHA256 y control de roles (admin / operador).

Las credenciales se cargan exclusivamente desde `st.secrets` o variables de entorno,
nunca desde código fuente.
"""
from __future__ import annotations

import getpass
import hashlib
import hmac
import os
import secrets
import time
from typing import Any

PBKDF2_ITERACIONES = 260_000
MAX_INTENTOS_FALLIDOS = 5
BLOQUEO_SEGUNDOS = 60

ROLES_VALIDOS = {"admin", "operador"}
SECCIONES_SOLO_ADMIN = {
    "⚙️ Protocolos Clínicos",
    "💾 Copias de Seguridad",
}


def generar_hash_contrasena(contrasena: str, salt_hex: str | None = None) -> str:
    """Genera un hash PBKDF2-HMAC-SHA256 con salt aleatorio."""
    if not contrasena or len(contrasena) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    salt = salt_hex or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        bytes.fromhex(salt),
        PBKDF2_ITERACIONES,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERACIONES}${salt}${dk.hex()}"


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    """Verifica una contraseña contra un hash PBKDF2-HMAC-SHA256 en tiempo constante."""
    if not contrasena or not hash_guardado:
        return False
    try:
        partes = str(hash_guardado).strip().split("$")
        if len(partes) != 4 or partes[0] != "pbkdf2_sha256":
            return False
        iteraciones = int(partes[1])
        if iteraciones < 100_000:
            return False
        salt_bytes = bytes.fromhex(partes[2])
        esperado = bytes.fromhex(partes[3])
        calculado = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            salt_bytes,
            iteraciones,
        )
        return hmac.compare_digest(calculado, esperado)
    except (ValueError, TypeError):
        return False


def _leer_st_secrets(secrets_obj: Any = None) -> dict:
    """Lee la sección [auth] de st.secrets sin lanzar error si el archivo no existe."""
    if secrets_obj is not None:
        return dict(secrets_obj) if hasattr(secrets_obj, "items") else {}
    try:
        import streamlit as st
        if "auth" in st.secrets:
            return dict(st.secrets["auth"])
    except Exception:
        pass
    return {}


def cargar_usuarios(secrets_auth: dict | None = None, env: dict | None = None) -> dict[str, dict]:
    """
    Carga usuarios configurados desde `st.secrets['auth']` o variables de entorno.
    Retorna un diccionario {username_lower: {'usuario', 'nombre', 'rol', 'password_hash'}}.
    """
    fuente_env = env if env is not None else os.environ
    auth_cfg = secrets_auth if secrets_auth is not None else _leer_st_secrets()
    usuarios: dict[str, dict] = {}

    # 1. Formato estructurado [auth.users.<usuario>] en st.secrets
    users_cfg = auth_cfg.get("users") if isinstance(auth_cfg, dict) else None
    if isinstance(users_cfg, dict):
        for uname, datos in users_cfg.items():
            if not hasattr(datos, "get"):
                continue
            pwd_hash = str(datos.get("password_hash") or "").strip()
            rol = str(datos.get("role") or datos.get("rol") or "operador").strip().lower()
            if rol not in ROLES_VALIDOS:
                rol = "operador"
            if uname and pwd_hash:
                key = str(uname).strip().lower()
                usuarios[key] = {
                    "usuario": str(uname).strip(),
                    "nombre": str(datos.get("nombre") or datos.get("name") or uname).strip(),
                    "rol": rol,
                    "password_hash": pwd_hash,
                }

    # 2. Formato plano en st.secrets['auth']
    if isinstance(auth_cfg, dict):
        admin_u = str(auth_cfg.get("admin_user") or "admin").strip()
        admin_h = str(auth_cfg.get("admin_password_hash") or "").strip()
        if admin_h:
            usuarios[admin_u.lower()] = {
                "usuario": admin_u,
                "nombre": str(auth_cfg.get("admin_name") or "Administrador").strip(),
                "rol": "admin",
                "password_hash": admin_h,
            }
        op_u = str(auth_cfg.get("operator_user") or "recepcion").strip()
        op_h = str(auth_cfg.get("operator_password_hash") or "").strip()
        if op_h:
            usuarios[op_u.lower()] = {
                "usuario": op_u,
                "nombre": str(auth_cfg.get("operator_name") or "Recepción").strip(),
                "rol": "operador",
                "password_hash": op_h,
            }

    # 3. Variables de entorno (tienen prioridad para Docker / despliegues CI)
    env_admin_h = str(fuente_env.get("PELITOS_ADMIN_PASSWORD_HASH") or "").strip()
    if env_admin_h:
        env_admin_u = str(fuente_env.get("PELITOS_ADMIN_USER") or "admin").strip()
        usuarios[env_admin_u.lower()] = {
            "usuario": env_admin_u,
            "nombre": str(fuente_env.get("PELITOS_ADMIN_NAME") or "Administrador").strip(),
            "rol": "admin",
            "password_hash": env_admin_h,
        }

    env_op_h = str(fuente_env.get("PELITOS_OPERATOR_PASSWORD_HASH") or "").strip()
    if env_op_h:
        env_op_u = str(fuente_env.get("PELITOS_OPERATOR_USER") or "recepcion").strip()
        usuarios[env_op_u.lower()] = {
            "usuario": env_op_u,
            "nombre": str(fuente_env.get("PELITOS_OPERATOR_NAME") or "Recepción").strip(),
            "rol": "operador",
            "password_hash": env_op_h,
        }

    return usuarios


def autenticar_credenciales(
    usuario: str,
    contrasena: str,
    usuarios: dict[str, dict] | None = None,
) -> dict | None:
    """Valida usuario y contraseña; retorna el perfil autenticado o None."""
    catalogo = usuarios if usuarios is not None else cargar_usuarios()
    clave = (usuario or "").strip().lower()
    if not clave or clave not in catalogo:
        # Ejecutar verificación dummy para mitigar enumeración por tiempo
        verificar_contrasena(contrasena or "x", f"pbkdf2_sha256${PBKDF2_ITERACIONES}${'00'*16}${'00'*32}")
        return None
    registro = catalogo[clave]
    if verificar_contrasena(contrasena, registro["password_hash"]):
        return {
            "usuario": registro["usuario"],
            "nombre": registro["nombre"],
            "rol": registro["rol"],
        }
    return None


def puede_acceder_seccion(rol: str, seccion: str) -> bool:
    """Indica si un rol está autorizado para abrir una sección del panel."""
    if seccion in SECCIONES_SOLO_ADMIN:
        return rol == "admin"
    return rol in ROLES_VALIDOS


def requerir_autenticacion(st_module) -> dict | None:
    """
    Puerta de acceso obligatoria (fail-closed) para Streamlit.
    Retorna el perfil de usuario autenticado o detiene la ejecución (`st.stop()`).
    """
    if st_module.session_state.get("auth_user"):
        return st_module.session_state["auth_user"]

    usuarios = cargar_usuarios()

    # Modo desarrollo local explícito (desactivado por defecto)
    if not usuarios and os.environ.get("PELITOS_LOCAL_DEV_NO_AUTH") == "1":
        perfil_dev = {
            "usuario": "local_dev",
            "nombre": "Modo Desarrollo Local",
            "rol": "operador",
            "modo_dev": True,
        }
        st_module.session_state["auth_user"] = perfil_dev
        return perfil_dev

    st_module.markdown(
        '<div class="main-header">🔐 Acceso Restringido — Pelitos Veterinaria CRM</div>',
        unsafe_allow_html=True,
    )
    st_module.markdown(
        '<div class="sub-header">Inicie sesión con sus credenciales autorizadas para gestionar clientes e historias clínicas.</div>',
        unsafe_allow_html=True,
    )

    if not usuarios:
        st_module.error(
            "⛔ **Autenticación obligatoria no configurada.** Por seguridad, el acceso a los datos "
            "clínicos y administrativos permanece bloqueado hasta configurar credenciales."
        )
        st_module.markdown(
            """
            ### ¿Cómo configurar el acceso en 2 pasos?
            1. Genere un hash seguro de contraseña desde la terminal del proyecto:
               ```bash
               python -m modules.auth
               ```
            2. Copie el bloque generado en **`.streamlit/secrets.toml`** (en local, usando como guía `.streamlit/secrets.toml.example`)
               o en **Streamlit Community Cloud → Settings → Secrets**, o defina las variables de entorno:
               `PELITOS_ADMIN_USER` y `PELITOS_ADMIN_PASSWORD_HASH`.
            """
        )
        st_module.stop()
        return None

    ahora = time.time()
    bloqueado_hasta = float(st_module.session_state.get("auth_lock_until", 0.0))
    if ahora < bloqueado_hasta:
        restante = int(bloqueado_hasta - ahora) + 1
        st_module.error(
            f"Demasiados intentos fallidos. Espere **{restante} segundos** antes de volver a intentarlo."
        )
        st_module.stop()
        return None

    col_c1, col_c2, col_c3 = st_module.columns([1, 2, 1])
    with col_c2:
        with st_module.form("form_login_pelitos", clear_on_submit=False):
            st_module.subheader("Iniciar Sesión")
            u_in = st_module.text_input("Usuario", placeholder="admin o recepcion")
            p_in = st_module.text_input("Contraseña", type="password", placeholder="••••••••")
            enviado = st_module.form_submit_button("Ingresar al Panel", type="primary", use_container_width=True)

        if enviado:
            perfil = autenticar_credenciales(u_in, p_in, usuarios)
            if perfil:
                st_module.session_state["auth_user"] = perfil
                st_module.session_state["auth_failed_attempts"] = 0
                st_module.session_state["auth_lock_until"] = 0.0
                st_module.rerun()
            else:
                intentos = int(st_module.session_state.get("auth_failed_attempts", 0)) + 1
                st_module.session_state["auth_failed_attempts"] = intentos
                if intentos >= MAX_INTENTOS_FALLIDOS:
                    st_module.session_state["auth_lock_until"] = time.time() + BLOQUEO_SEGUNDOS
                    st_module.session_state["auth_failed_attempts"] = 0
                    st_module.error(
                        f"Cuenta bloqueada temporalmente por {BLOQUEO_SEGUNDOS} segundos tras "
                        f"{MAX_INTENTOS_FALLIDOS} intentos fallidos."
                    )
                else:
                    restantes = MAX_INTENTOS_FALLIDOS - intentos
                    st_module.error(f"Usuario o contraseña incorrectos. Intentos restantes: {restantes}.")

    st_module.stop()
    return None


def cerrar_sesion(st_module) -> None:
    """Cierra la sesión autenticada actual."""
    for clave in ("auth_user", "auth_failed_attempts", "auth_lock_until"):
        st_module.session_state.pop(clave, None)


def _cli_generar_hash() -> None:
    print("=== Generador de Credenciales Seguras (Pelitos Veterinaria CRM) ===")
    usuario = input("Nombre de usuario [admin]: ").strip() or "admin"
    rol = input("Rol (admin / operador) [admin]: ").strip().lower() or "admin"
    if rol not in ROLES_VALIDOS:
        print(f"Rol '{rol}' no válido. Usando 'operador'.")
        rol = "operador"
    nombre = input(f"Nombre visible [{usuario.capitalize()}]: ").strip() or usuario.capitalize()
    pwd1 = getpass.getpass("Contraseña (mínimo 8 caracteres): ")
    pwd2 = getpass.getpass("Confirme la contraseña: ")
    if pwd1 != pwd2:
        print("Error: las contraseñas no coinciden.")
        raise SystemExit(1)
    try:
        pwd_hash = generar_hash_contrasena(pwd1)
    except ValueError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    print("\nCopie este bloque en .streamlit/secrets.toml (o en Streamlit Cloud Secrets):\n")
    print(f"[auth.users.{usuario}]")
    print(f'nombre = "{nombre}"')
    print(f'role = "{rol}"')
    print(f'password_hash = "{pwd_hash}"')


if __name__ == "__main__":
    _cli_generar_hash()
