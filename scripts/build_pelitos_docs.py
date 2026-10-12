"""
build_pelitos_docs.py  –  v5 In-App Viewer, Edit & Delete Edition
==================================================================
ACTUALIZACIONES:
  + VISOR INTEGRADO (NO REQUIERE DESCARGAR):
      - Word (.docx): Renderizado HTML formateado directo via Mammoth.js
      - Excel (.xlsx, .xls, .csv): Tabla interactiva completa via SheetJS
      - PDF (.pdf): Visor embebido en iframe dentro de la app
      - Imágenes: Visor con ajuste responsivo
      - Video & Audio: Reproductores HTML5 integrados
      - Código / Texto: Visor con resaltado y tipografía monospace
  + EDICIÓN Y RENOMBRADO:
      - Modal de renombrado para editar el nombre de cualquier archivo
      - Botón "Editar" en el Inspector y en la fila de cada archivo
  + ELIMINACIÓN:
      - Botón "Eliminar" en el Inspector y en cada fila
      - Eliminación por lote ("Eliminar seleccionados")
  + CERO DESCARGAS FORZADAS:
      - Al hacer doble clic o clic en "Abrir / Ver", se abre el visor modal directamente
"""
import base64, os

def leer_b64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_data = f"data:image/png;base64,{leer_b64('assets/logo_pelitos.png')}"

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pelitos Docs - Gestión Documental</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <!-- Mammoth.js para previsualizar Word (.docx) directamente en el navegador sin descargar -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.6.0/mammoth.browser.min.js"></script>
  <!-- SheetJS para previsualizar Excel (.xlsx, .xls, .csv) en tablas interactivas -->
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{
      font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      background:#F1F5F9; color:#1E293B;
      height:100vh; overflow:hidden; font-size:13px;
    }}
    ::-webkit-scrollbar {{ width:5px; height:5px; }}
    ::-webkit-scrollbar-track {{ background:#F1F5F9; }}
    ::-webkit-scrollbar-thumb {{ background:#CBD5E1; border-radius:4px; }}

    .sidebar-active {{ background:#5B21B6!important; color:#fff!important; font-weight:700; }}
    .tree-active    {{ background:#FDE68A!important; color:#78350F!important; border-radius:6px; font-weight:700; }}
    .row-selected   {{ background:#EDE9FE!important; }}
    .row-selected td{{ color:#5B21B6; font-weight:600; }}

    .animate-pulse-slow {{ animation:pulse-s 2s ease-in-out infinite; }}
    @keyframes pulse-s {{ 0%,100%{{opacity:1}} 50%{{opacity:.55}} }}

    /* Badges de extensión */
    .ext-badge {{
      display:inline-block; padding:2px 7px; border-radius:5px;
      font-size:11px; font-weight:700; letter-spacing:.4px;
      text-transform:uppercase; white-space:nowrap;
    }}
    .ext-pdf    {{ background:#FEE2E2; color:#B91C1C; }}
    .ext-doc    {{ background:#DBEAFE; color:#1D4ED8; }}
    .ext-xls    {{ background:#D1FAE5; color:#065F46; }}
    .ext-ppt    {{ background:#FEF3C7; color:#92400E; }}
    .ext-img    {{ background:#FCE7F3; color:#9D174D; }}
    .ext-vid    {{ background:#EDE9FE; color:#5B21B6; }}
    .ext-mp3    {{ background:#FDF4FF; color:#7E22CE; }}
    .ext-zip    {{ background:#FFF7ED; color:#C2410C; }}
    .ext-txt    {{ background:#F0FDF4; color:#166534; }}
    .ext-code   {{ background:#FAFAFA; color:#15803D; }}
    .ext-js     {{ background:#FEF9C3; color:#854D0E; }}
    .ext-html   {{ background:#FFF1F2; color:#BE123C; }}
    .ext-default{{ background:#F1F5F9; color:#475569; }}
    .folder-badge{{ background:#FEF3C7; color:#92400E; }}

    /* Overlay Drag & Drop */
    .drop-zone-overlay {{
      display:none; position:fixed; inset:0;
      background:rgba(91,33,182,0.85); backdrop-filter:blur(6px);
      z-index:90; align-items:center; justify-content:center;
      color:white; flex-direction:column; gap:14px; pointer-events:none;
    }}
    body.drag-over .drop-zone-overlay {{ display:flex; }}

    /* Tablas en visor Excel */
    #visor-contenido table {{
      border-collapse: collapse; width: 100%; background: white;
    }}
    #visor-contenido table td, #visor-contenido table th {{
      border: 1px solid #E2E8F0; padding: 6px 12px; font-size: 12px;
      color: #1E293B; white-space: nowrap;
    }}
    #visor-contenido table tr:first-child td, #visor-contenido table tr:first-child th {{
      background: #F8FAFC; font-weight: 700; color: #475569; position: sticky; top: 0;
    }}

    /* Estilos visor Word */
    #visor-contenido .word-doc p {{ margin-bottom: 0.75rem; line-height: 1.6; }}
    #visor-contenido .word-doc h1 {{ font-size: 1.5rem; font-weight: 800; margin: 1rem 0 0.5rem; color: #0F172A; }}
    #visor-contenido .word-doc h2 {{ font-size: 1.25rem; font-weight: 700; margin: 0.85rem 0 0.4rem; color: #1E293B; }}
    #visor-contenido .word-doc h3 {{ font-size: 1.1rem; font-weight: 600; margin: 0.75rem 0 0.35rem; color: #334155; }}
    #visor-contenido .word-doc table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    #visor-contenido .word-doc td, #visor-contenido .word-doc th {{ border: 1px solid #CBD5E1; padding: 6px 10px; }}

    /* Loading */
    #loading-overlay {{
      display:none; position:fixed; inset:0;
      background:rgba(88,28,135,.6); backdrop-filter:blur(4px);
      z-index:60; align-items:center; justify-content:center;
    }}
    #loading-overlay.active {{ display:flex; }}

    /* Toast */
    #toast {{
      position:fixed; bottom:1.25rem; right:1.25rem;
      background:#16002B; color:#fff; font-size:13px;
      padding:.65rem 1.1rem; border-radius:.75rem;
      box-shadow:0 4px 24px rgba(0,0,0,.35); z-index:70;
      display:flex; align-items:center; gap:.5rem; max-width:24rem;
      transform:translateY(5rem); opacity:0;
      transition:transform .2s,opacity .2s;
    }}
    #toast.show {{ transform:translateY(0); opacity:1; }}
  </style>
</head>

<body class="flex h-screen overflow-hidden">

<!-- Overlay visual al arrastrar archivos a la ventana -->
<div class="drop-zone-overlay">
  <div class="w-20 h-20 bg-white/20 rounded-3xl flex items-center justify-center animate-bounce">
    <i data-lucide="file-up" class="w-10 h-10 text-white"></i>
  </div>
  <p class="text-2xl font-bold">Suelta tus archivos aquí</p>
  <p class="text-sm opacity-90">Soporta Word, Excel, PDF, imágenes, videos y cualquier formato</p>
</div>

<!-- Inputs ocultos para subida de archivos y carpetas -->
<input type="file" id="input-files" multiple accept="*/*" style="display:none">
<input type="file" id="input-folder" webkitdirectory multiple accept="*/*" style="display:none">

<!-- ══════════════ SIDEBAR ══════════════ -->
<aside class="w-60 bg-[#16002B] text-slate-200 flex flex-col shrink-0 overflow-y-auto select-none"
       style="min-width:15rem">

  <!-- Logo -->
  <div class="p-3 border-b border-purple-900/60 flex items-center gap-2 bg-white/5">
    <img src="{logo_data}" alt="Pelitos Veterinaria" class="h-9 object-contain" style="max-width:140px;">
  </div>
  <div class="px-3 py-2 border-b border-purple-900/40 bg-[#1E0040]/60">
    <p class="text-xs text-purple-300 font-bold tracking-widest">PELITOS DOCS</p>
    <p class="text-xs text-slate-400 mt-0.5">Gestión Documental Empresarial</p>
  </div>

  <!-- Nav -->
  <nav class="px-2 pt-3 space-y-0.5">
    <button id="nav-inicio" onclick="navActivar('inicio')"
      class="sidebar-active w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium">
      <i data-lucide="home" class="w-4 h-4 shrink-0"></i> Inicio
    </button>
    <button id="nav-explorador" onclick="navActivar('explorador')"
      class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-purple-900/50 hover:text-white font-medium">
      <i data-lucide="folder-open" class="w-4 h-4 text-amber-400 shrink-0"></i> Explorador
    </button>
    <button id="nav-favoritos" onclick="navActivar('favoritos')"
      class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-purple-900/50 hover:text-white font-medium">
      <i data-lucide="star" class="w-4 h-4 text-amber-400 shrink-0"></i> Favoritos
    </button>
    <button id="nav-recientes" onclick="navActivar('recientes')"
      class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-purple-900/50 hover:text-white font-medium">
      <i data-lucide="clock" class="w-4 h-4 shrink-0"></i> Recientes
    </button>
  </nav>

  <!-- Unidades de Negocio -->
  <div class="px-3 pt-4 pb-1">
    <p class="text-xs font-bold text-purple-400 uppercase tracking-widest mb-2">Unidades de Negocio</p>
    <div class="space-y-0.5">
      <button onclick="selUnidad('Consultorio Veterinario')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="stethoscope" class="w-3.5 h-3.5 text-blue-400 shrink-0"></i><span class="truncate">Consultorio Veterinario</span>
      </button>
      <button onclick="selUnidad('Estética Canina')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-white bg-purple-900/30 text-left font-semibold">
        <i data-lucide="scissors" class="w-3.5 h-3.5 text-pink-400 shrink-0"></i><span class="truncate">Estética Canina</span>
      </button>
      <button onclick="selUnidad('Laboratorio Veterinario')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="flask-conical" class="w-3.5 h-3.5 text-emerald-400 shrink-0"></i><span class="truncate">Laboratorio Veterinario</span>
      </button>
      <button onclick="selUnidad('Farmacia Veterinaria')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="pill" class="w-3.5 h-3.5 text-orange-400 shrink-0"></i><span class="truncate">Farmacia Veterinaria</span>
      </button>
      <button onclick="selUnidad('Pet Shop')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="shopping-cart" class="w-3.5 h-3.5 text-amber-400 shrink-0"></i><span class="truncate">Pet Shop</span>
      </button>
      <button onclick="selUnidad('Pelitos Móvil')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="truck" class="w-3.5 h-3.5 text-sky-400 shrink-0"></i><span class="truncate">Pelitos Móvil</span>
      </button>
      <button onclick="selUnidad('Hospedaje de Mascotas')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="house" class="w-3.5 h-3.5 text-purple-400 shrink-0"></i><span class="truncate">Hospedaje de Mascotas</span>
      </button>
    </div>
  </div>

  <!-- Servicios Compartidos -->
  <div class="px-3 pt-3 pb-4">
    <p class="text-xs font-bold text-purple-400 uppercase tracking-widest mb-2">Servicios Compartidos</p>
    <div class="space-y-0.5">
      <button onclick="selUnidad('Recepción y Clientes')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="headset" class="w-3.5 h-3.5 text-blue-400 shrink-0"></i><span class="truncate">Recepción y Clientes</span>
      </button>
      <button onclick="selUnidad('Recursos Humanos')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="users" class="w-3.5 h-3.5 text-sky-400 shrink-0"></i><span class="truncate">Recursos Humanos</span>
      </button>
      <button onclick="selUnidad('Marketing Corporativo')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="megaphone" class="w-3.5 h-3.5 text-purple-400 shrink-0"></i><span class="truncate">Marketing Corporativo</span>
      </button>
      <button onclick="selUnidad('Compras y Logística')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="package" class="w-3.5 h-3.5 text-amber-500 shrink-0"></i><span class="truncate">Compras y Logística</span>
      </button>
      <button onclick="selUnidad('Tecnología y Software')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="laptop" class="w-3.5 h-3.5 text-blue-400 shrink-0"></i><span class="truncate">Tecnología y Software</span>
      </button>
      <button onclick="selUnidad('Calidad y Auditoría')" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-purple-900/40 hover:text-white text-left font-medium">
        <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-400 shrink-0"></i><span class="truncate">Calidad y Auditoría</span>
      </button>
    </div>
  </div>
</aside>

<!-- ══════════════ ÁREA PRINCIPAL ══════════════ -->
<main class="flex-1 flex flex-col overflow-hidden">

  <!-- TOPBAR -->
  <header class="h-14 bg-white border-b border-slate-200 px-4 flex items-center gap-3 shrink-0 shadow-sm z-20">
    <div class="relative flex-1 max-w-md">
      <input id="buscador-top" oninput="aplicarFiltros()" type="text"
        placeholder="Buscar por nombre, extensión..."
        class="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2
               placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition">
      <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
    </div>

    <!-- Filtro de tipo -->
    <select id="filtro-tipo-top" onchange="aplicarFiltros()"
      class="text-sm bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-600
             focus:outline-none focus:ring-2 focus:ring-purple-400 cursor-pointer font-medium">
      <option value="">Todos los tipos</option>
      <option value="folder">📁 Carpetas</option>
      <option value="pdf">📄 PDF</option>
      <option value="doc">📝 Word</option>
      <option value="xls">📊 Excel</option>
      <option value="ppt">📑 PowerPoint</option>
      <option value="img">🖼️ Imágenes</option>
      <option value="vid">🎬 Videos</option>
      <option value="mp3">🎵 Audio</option>
      <option value="zip">🗜️ Comprimidos</option>
      <option value="txt">📃 Texto</option>
      <option value="code">💻 Código</option>
    </select>

    <!-- Botones de subida de archivos y carpetas -->
    <div class="flex items-center gap-2 shrink-0">
      <button onclick="abrirArchivos()"
        class="flex items-center gap-1.5 bg-[#5B21B6] hover:bg-[#4C1D95]
               text-white text-sm font-bold px-3.5 py-2 rounded-lg shadow transition"
        title="Subir documentos individuales o en lote (Word, Excel, PDF, fotos...)">
        <i data-lucide="file-up" class="w-4 h-4"></i> Subir Archivos
      </button>

      <button onclick="abrirDirectorio()"
        class="flex items-center gap-1.5 bg-purple-50 hover:bg-purple-100 text-purple-800
               border border-purple-200 text-sm font-bold px-3.5 py-2 rounded-lg transition"
        title="Abrir una carpeta completa de tu computadora">
        <i data-lucide="folder-open" class="w-4 h-4 text-amber-500"></i> Abrir Carpeta
      </button>
    </div>

    <select id="ordenar-por" onchange="aplicarFiltros()"
      class="text-sm bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-600
             focus:outline-none focus:ring-2 focus:ring-purple-400 cursor-pointer">
      <option value="nombre">↑ Nombre</option>
      <option value="tipo">↑ Tipo</option>
      <option value="tamano">↓ Tamaño</option>
      <option value="fecha">↓ Fecha</option>
    </select>

    <div class="flex items-center border border-slate-200 rounded-lg overflow-hidden shrink-0">
      <button id="btn-vista-lista" onclick="cambiarVista('lista')" title="Vista lista"
        class="px-2.5 py-2 bg-purple-50 text-purple-700 hover:bg-purple-100 transition">
        <i data-lucide="list" class="w-4 h-4"></i>
      </button>
      <button id="btn-vista-grid" onclick="cambiarVista('grid')" title="Vista cuadrícula"
        class="px-2.5 py-2 text-slate-500 hover:bg-slate-50 transition">
        <i data-lucide="layout-grid" class="w-4 h-4"></i>
      </button>
    </div>

    <button onclick="maximizarVentana()" title="Pantalla completa"
      class="text-slate-400 hover:text-slate-700 transition shrink-0">
      <i data-lucide="maximize-2" class="w-5 h-5"></i>
    </button>
  </header>

  <!-- CONTENIDO SCROLLABLE -->
  <div class="flex-1 overflow-y-auto p-4 space-y-4">

    <!-- ══ VISTA INICIO ══ -->
    <section id="vista-inicio" class="space-y-4">

      <!-- Hero Banner -->
      <div class="relative rounded-2xl overflow-hidden bg-gradient-to-r from-purple-900 via-purple-800 to-indigo-900
                  p-6 shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <img src="{logo_data}" alt="Pelitos Veterinaria"
               class="h-14 object-contain mb-3"
               style="filter:brightness(0) invert(1);">
          <p class="text-purple-200 text-sm font-semibold">Tu biblioteca empresarial veterinaria</p>
          <p class="text-white/70 text-xs mt-1">Sube tus archivos Word, PDF, Excel o carpetas completas y visualízalos al instante</p>
        </div>
        <div class="text-right text-white">
          <p class="text-base font-bold">Cuidamos vidas,</p>
          <p class="text-base font-bold">impulsamos sueños <span class="text-pink-300">❤️</span></p>
          <div class="flex items-center gap-2 mt-3 ml-auto">
            <button onclick="abrirArchivos()"
              class="bg-amber-400 hover:bg-amber-300 text-amber-900 font-bold
                     text-sm px-4 py-2 rounded-lg shadow transition flex items-center gap-1.5">
              <i data-lucide="file-up" class="w-4 h-4"></i> Subir Archivos
            </button>
            <button onclick="abrirDirectorio()"
              class="bg-white/10 hover:bg-white/20 text-white font-bold
                     text-sm px-4 py-2 rounded-lg border border-white/20 transition flex items-center gap-1.5">
              <i data-lucide="folder-open" class="w-4 h-4 text-amber-300"></i> Abrir Carpeta
            </button>
          </div>
        </div>
        <div class="absolute right-5 bottom-3 opacity-10 text-white text-8xl select-none pointer-events-none">🐾</div>
      </div>

      <!-- Unidades de Negocio -->
      <div>
        <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-2">Unidades de Negocio</h3>
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
          <div onclick="selUnidad('Consultorio Veterinario')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-blue-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="stethoscope" class="w-4 h-4 text-blue-600 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Consultorio Veterinario</span>
            </div>
          </div>
          <div onclick="selUnidad('Estética Canina')" class="cursor-pointer bg-pink-50 p-3 rounded-xl border-2 border-pink-400 shadow-sm hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="scissors" class="w-4 h-4 text-pink-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Estética Canina</span>
            </div>
          </div>
          <div onclick="selUnidad('Laboratorio Veterinario')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-emerald-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="flask-conical" class="w-4 h-4 text-emerald-600 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Laboratorio Veterinario</span>
            </div>
          </div>
          <div onclick="selUnidad('Farmacia Veterinaria')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-orange-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="pill" class="w-4 h-4 text-orange-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Farmacia Veterinaria</span>
            </div>
          </div>
          <div onclick="selUnidad('Pet Shop')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-amber-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="shopping-cart" class="w-4 h-4 text-amber-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Pet Shop</span>
            </div>
          </div>
          <div onclick="selUnidad('Pelitos Móvil')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-sky-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="truck" class="w-4 h-4 text-sky-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Pelitos Móvil</span>
            </div>
          </div>
          <div onclick="selUnidad('Hospedaje de Mascotas')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-purple-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="house" class="w-4 h-4 text-purple-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800 leading-tight">Hospedaje de Mascotas</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Servicios Compartidos -->
      <div>
        <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-2">Servicios Compartidos</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          <div onclick="selUnidad('Recepción y Clientes')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-blue-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="headset" class="w-4 h-4 text-blue-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800">Recepción y Clientes</span>
            </div>
          </div>
          <div onclick="selUnidad('Recursos Humanos')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-sky-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="users" class="w-4 h-4 text-sky-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800">Recursos Humanos</span>
            </div>
          </div>
          <div onclick="selUnidad('Marketing Corporativo')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-purple-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="megaphone" class="w-4 h-4 text-purple-600 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800">Marketing Corporativo</span>
            </div>
          </div>
          <div onclick="selUnidad('Compras y Logística')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-amber-500 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="package" class="w-4 h-4 text-amber-600 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800">Compras y Logística</span>
            </div>
          </div>
          <div onclick="selUnidad('Tecnología y Software')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-blue-500 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="laptop" class="w-4 h-4 text-blue-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800">Tecnología y Software</span>
            </div>
          </div>
          <div onclick="selUnidad('Calidad y Auditoría')" class="cursor-pointer bg-white p-3 rounded-xl border border-slate-200 shadow-sm hover:border-emerald-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <i data-lucide="shield-check" class="w-4 h-4 text-emerald-500 shrink-0"></i>
              <span class="text-xs font-bold text-slate-800">Calidad y Auditoría</span>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA Principal -->
      <div class="bg-white rounded-2xl border-2 border-dashed border-purple-300 p-8
                  flex flex-col items-center justify-center text-center shadow-inner hover:border-purple-500 transition">
        <div class="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-300/40 mb-3">
          <i data-lucide="files" class="w-9 h-9 text-white"></i>
        </div>
        <h3 class="text-base font-bold text-slate-800 mb-1">Cargar documentos o carpetas</h3>
        <p class="text-sm text-slate-500 max-w-md leading-relaxed mb-4">
          Visualiza tus archivos directamente en pantalla <strong>sin tener que descargarlos</strong>.<br>
          Soporta Word, Excel, PDF, imágenes, videos, audio y código.
        </p>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <button onclick="abrirArchivos()"
            class="flex items-center gap-2 bg-[#5B21B6] hover:bg-[#4C1D95] text-white text-sm font-bold px-5 py-2.5 rounded-xl shadow transition">
            <i data-lucide="file-up" class="w-4 h-4"></i> Seleccionar Archivo(s)
          </button>
          <button onclick="abrirDirectorio()"
            class="flex items-center gap-2 bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 text-sm font-bold px-5 py-2.5 rounded-xl transition">
            <i data-lucide="folder-open" class="w-4 h-4 text-amber-500"></i> Seleccionar Carpeta
          </button>
        </div>
        <p class="text-xs text-slate-400 mt-3">Arrastra y suelta cualquier archivo en la pantalla</p>
      </div>

    </section>

    <!-- ══ VISTA EXPLORADOR ══ -->
    <section id="vista-explorador" class="hidden space-y-3">

      <!-- Breadcrumb -->
      <div id="breadcrumb-bar"
        class="flex items-center gap-1.5 text-sm text-slate-500 flex-wrap bg-white border border-slate-200
               rounded-xl px-4 py-2.5 shadow-sm overflow-x-auto">
        <i data-lucide="hard-drive" class="w-4 h-4 text-slate-400 shrink-0"></i>
        <span class="text-slate-400 font-medium">Carga archivos o selecciona una carpeta...</span>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-2">
        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-total" class="text-xl font-black text-purple-700">—</p>
          <p class="text-xs text-slate-500 mt-0.5">Archivos</p>
        </div>
        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-carpetas" class="text-xl font-black text-amber-600">—</p>
          <p class="text-xs text-slate-500 mt-0.5">Carpetas</p>
        </div>
        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-tamano" class="text-xl font-black text-emerald-700">—</p>
          <p class="text-xs text-slate-500 mt-0.5">Tamaño total</p>
        </div>
        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-tipos" class="text-xl font-black text-blue-600">—</p>
          <p class="text-xs text-slate-500 mt-0.5">Tipos distintos</p>
        </div>
      </div>

      <!-- Panel 3 columnas -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex"
           style="height:calc(100vh - 340px); min-height:380px;">

        <!-- ÁRBOL -->
        <div id="panel-arbol" class="w-52 border-r border-slate-100 p-2 overflow-y-auto bg-slate-50/50 shrink-0">
          <p class="text-xs font-bold text-slate-400 uppercase tracking-wider px-1 mb-2">Árbol de directorios</p>
          <div id="arbol-dir" class="space-y-0.5">
            <p class="text-slate-400 px-2 py-6 text-center text-xs">Sin datos</p>
          </div>
          <p id="nota-arbol-flat" class="text-xs text-slate-400 text-center py-2 hidden">
            (Vista de archivos)
          </p>
        </div>

        <!-- TABLA -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Sub-header -->
          <div class="border-b border-slate-100 px-4 py-2 flex items-center gap-2 bg-white shrink-0">
            <span id="label-ruta-actual" class="text-xs text-slate-500 font-mono truncate flex-1 select-all">
              Seleccione archivos o una carpeta
            </span>
            <button onclick="abrirArchivos()" title="Agregar más archivos"
              class="text-purple-600 hover:bg-purple-50 text-xs font-semibold px-2 py-1 rounded flex items-center gap-1 transition">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i> Agregar archivos
            </button>
            <button onclick="subirNivel()" title="Subir un nivel" id="btn-subir"
              class="text-slate-400 hover:text-purple-600 transition p-1 rounded hover:bg-purple-50 hidden">
              <i data-lucide="arrow-up" class="w-4 h-4"></i>
            </button>
            <button onclick="actualizarDirectorio()" title="Actualizar"
              class="text-slate-400 hover:text-purple-600 transition p-1 rounded hover:bg-purple-50">
              <i data-lucide="refresh-cw" class="w-4 h-4"></i>
            </button>
            <button onclick="abrirDirectorio()" title="Abrir carpeta"
              class="text-slate-400 hover:text-purple-600 transition p-1 rounded hover:bg-purple-50">
              <i data-lucide="folder-open" class="w-4 h-4"></i>
            </button>
          </div>

          <div class="overflow-auto flex-1" id="tabla-scroll-container">
            <table class="w-full text-left border-collapse" id="tabla-arch">
              <thead class="bg-slate-50 border-b border-slate-100 sticky top-0 z-10 text-xs text-slate-500">
                <tr>
                  <th class="py-2.5 px-3 w-8">
                    <input type="checkbox" id="chk-all" onclick="selTodos(this)"
                      class="rounded text-purple-600 focus:ring-0 w-3.5 h-3.5">
                  </th>
                  <th class="py-2.5 px-3 font-semibold cursor-pointer hover:text-slate-800 select-none"
                      onclick="ordenarPor('nombre')">Nombre ↕</th>
                  <th class="py-2.5 px-3 font-semibold">Tipo</th>
                  <th class="py-2.5 px-3 font-semibold cursor-pointer hover:text-slate-800 select-none"
                      onclick="ordenarPor('fecha')">Modificado ↕</th>
                  <th class="py-2.5 px-3 font-semibold cursor-pointer hover:text-slate-800 select-none text-right"
                      onclick="ordenarPor('tamano')">Tamaño ↕</th>
                  <th class="py-2.5 px-3 font-semibold text-center w-24">Acciones</th>
                </tr>
              </thead>
              <tbody id="tabla-body" class="divide-y divide-slate-50 text-sm">
                <tr><td colspan="6" class="text-center py-16 text-slate-400">
                  <i data-lucide="files" class="w-10 h-10 mx-auto mb-3 opacity-30"></i>
                  <p class="text-sm font-medium">Aún no has cargado archivos o carpetas.</p>
                  <div class="flex items-center justify-center gap-3 mt-3">
                    <button onclick="abrirArchivos()"
                      class="text-purple-600 hover:underline text-sm font-semibold flex items-center gap-1">
                      <i data-lucide="file-up" class="w-3.5 h-3.5"></i> Subir Archivos
                    </button>
                    <span class="text-slate-300">|</span>
                    <button onclick="abrirDirectorio()"
                      class="text-purple-600 hover:underline text-sm font-semibold flex items-center gap-1">
                      <i data-lucide="folder-open" class="w-3.5 h-3.5"></i> Abrir Carpeta
                    </button>
                  </div>
                </td></tr>
              </tbody>
            </table>
          </div>

          <!-- Status bar con botón de eliminación por lote -->
          <div class="border-t border-slate-100 px-4 py-1.5 flex items-center justify-between
                      text-xs text-slate-400 bg-slate-50 shrink-0">
            <span id="status-bar">0 elementos</span>
            <div class="flex items-center gap-3">
              <span id="status-sel">0 seleccionados</span>
              <button id="btn-eliminar-lote" onclick="eliminarLoteSeleccionado()"
                class="hidden text-red-600 hover:text-red-700 font-semibold flex items-center gap-1 hover:bg-red-50 px-2 py-0.5 rounded transition">
                <i data-lucide="trash-2" class="w-3 h-3"></i> Eliminar seleccionados
              </button>
            </div>
          </div>
        </div>

        <!-- INSPECTOR -->
        <div class="w-60 border-l border-slate-100 flex flex-col shrink-0 overflow-y-auto bg-white">
          <div class="p-3 border-b border-slate-100">
            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Inspector</p>
          </div>
          <div id="inspector-body" class="p-3 flex-1 text-xs space-y-3">
            <div class="text-center text-slate-300 py-10">
              <i data-lucide="file-search" class="w-9 h-9 mx-auto mb-2"></i>
              <p class="text-sm">Selecciona un archivo</p>
            </div>
          </div>
          <div id="inspector-actions" class="p-3 border-t border-slate-100 space-y-2 hidden">
            <!-- Botón de previsualización directa -->
            <button onclick="abrirDocumento()"
              class="w-full bg-[#5B21B6] hover:bg-[#4C1D95] text-white text-xs font-bold
                     py-2.5 px-3 rounded-xl shadow transition flex items-center justify-center gap-1.5">
              <i data-lucide="eye" class="w-4 h-4"></i> Ver sin descargar
            </button>
            <div class="grid grid-cols-2 gap-1.5">
              <button onclick="abrirModalRenombrar()"
                class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold
                       py-2 px-2 rounded-lg flex items-center justify-center gap-1 transition">
                <i data-lucide="edit-3" class="w-3.5 h-3.5 text-blue-600"></i> Editar
              </button>
              <button onclick="eliminarArchivoSeleccionado()"
                class="bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold
                       py-2 px-2 rounded-lg flex items-center justify-center gap-1 transition">
                <i data-lucide="trash-2" class="w-3.5 h-3.5 text-red-600"></i> Eliminar
              </button>
            </div>
            <div class="grid grid-cols-2 gap-1.5">
              <button onclick="copiarRutaInspector()"
                class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium
                       py-1.5 px-2 rounded-lg flex items-center justify-center gap-1 transition">
                <i data-lucide="copy" class="w-3 h-3 text-slate-500"></i> Copiar nom.
              </button>
              <button onclick="toggleFavoritoInspector()" id="btn-fav-inspector"
                class="bg-slate-100 hover:bg-amber-50 text-slate-700 text-xs font-medium
                       py-1.5 px-2 rounded-lg flex items-center justify-center gap-1 transition">
                <i data-lucide="star" class="w-3 h-3 text-amber-500"></i> Fav.
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- Vista grid -->
      <div id="vista-grid" class="hidden">
        <div id="grid-archivos"
          class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2"></div>
      </div>
    </section>

    <!-- ══ VISTA FAVORITOS ══ -->
    <section id="vista-favoritos" class="hidden">
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center text-slate-400">
        <i data-lucide="star" class="w-10 h-10 mx-auto mb-3 text-amber-400"></i>
        <p class="text-base font-semibold text-slate-700">Favoritos</p>
        <p id="lbl-fav-empty" class="text-sm mt-2">Aún no tienes favoritos marcados.</p>
        <div id="lista-favoritos" class="mt-4 text-left space-y-1 hidden"></div>
      </div>
    </section>

    <!-- ══ VISTA RECIENTES ══ -->
    <section id="vista-recientes" class="hidden">
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center text-slate-400">
        <i data-lucide="clock" class="w-10 h-10 mx-auto mb-3"></i>
        <p class="text-base font-semibold text-slate-700">Recientes</p>
        <p id="lbl-rec-empty" class="text-sm mt-2">No has abierto ningún archivo aún.</p>
        <div id="lista-recientes" class="mt-4 text-left space-y-1 hidden"></div>
      </div>
    </section>

  </div>
</main>

<!-- ══════════════ MODAL VISOR INTEGRADO (SIN DESCARGAR) ══════════════ -->
<div id="modal-visor" class="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm hidden items-center justify-center p-3 sm:p-6">
  <div class="bg-white rounded-2xl shadow-2xl flex flex-col w-full max-w-5xl h-[88vh] overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
    <!-- Header del visor -->
    <div class="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between bg-slate-50 shrink-0">
      <div class="flex items-center gap-2.5 overflow-hidden">
        <div id="visor-icon" class="w-8 h-8 rounded-lg flex items-center justify-center bg-purple-100 text-purple-700 shrink-0">
          <i data-lucide="file-text" class="w-4 h-4"></i>
        </div>
        <div class="truncate">
          <h4 id="visor-nombre" class="font-bold text-slate-800 text-sm truncate max-w-md">Documento</h4>
          <div class="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
            <span id="visor-badge" class="ext-badge ext-doc">Word</span>
            <span id="visor-tamano">—</span>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <button onclick="editarNombreDesdeVisor()"
          class="text-slate-600 hover:text-purple-700 hover:bg-slate-200 px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
          title="Renombrar archivo">
          <i data-lucide="edit-3" class="w-3.5 h-3.5 text-blue-600"></i> <span class="hidden sm:inline">Renombrar</span>
        </button>
        <button onclick="descargarArchivoActual()"
          class="text-slate-600 hover:text-purple-700 hover:bg-slate-200 px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
          title="Descargar copia del archivo">
          <i data-lucide="download" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">Descargar</span>
        </button>
        <button onclick="eliminarArchivoActual()"
          class="text-red-600 hover:text-red-700 hover:bg-red-50 px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
          title="Eliminar archivo">
          <i data-lucide="trash-2" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">Eliminar</span>
        </button>
        <div class="h-4 w-px bg-slate-300 mx-1"></div>
        <button onclick="cerrarVisor()"
          class="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg hover:bg-slate-200 transition"
          title="Cerrar visor">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
    </div>
    <!-- Contenedor del visor -->
    <div id="visor-contenido" class="flex-1 overflow-auto bg-slate-100 p-4 sm:p-6 flex items-center justify-center">
      <!-- Se inyecta dinámicamente según el tipo de archivo -->
    </div>
  </div>
</div>

<!-- ══════════════ MODAL RENOMBRAR / EDITAR ══════════════ -->
<div id="modal-renombrar" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm hidden items-center justify-center p-4">
  <div class="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md border border-slate-200">
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center shrink-0">
        <i data-lucide="edit-3" class="w-5 h-5"></i>
      </div>
      <div>
        <h3 class="text-base font-bold text-slate-800">Editar nombre de archivo</h3>
        <p class="text-xs text-slate-400">Modifica el nombre del documento</p>
      </div>
    </div>
    <div class="space-y-3">
      <label class="block text-xs font-semibold text-slate-600">Nuevo nombre</label>
      <input type="text" id="input-nuevo-nombre"
        class="w-full text-sm bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition"
        placeholder="Nombre del archivo...">
      <div class="flex items-center justify-end gap-2 pt-2">
        <button onclick="cerrarModalRenombrar()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition">Cancelar</button>
        <button onclick="guardarNuevoNombre()" class="px-5 py-2 text-xs font-bold text-white bg-[#5B21B6] hover:bg-[#4C1D95] rounded-lg shadow transition">Guardar cambios</button>
      </div>
    </div>
  </div>
</div>

<!-- TOAST -->
<div id="toast" role="alert" aria-live="assertive">
  <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400 shrink-0" id="toast-icon"></i>
  <span id="toast-msg"></span>
</div>

<!-- LOADING -->
<div id="loading-overlay" role="status" aria-label="Cargando">
  <div class="bg-white rounded-2xl p-7 flex flex-col items-center gap-4 shadow-2xl">
    <div class="w-12 h-12 border-4 border-purple-200 border-t-purple-700 rounded-full animate-spin"></div>
    <p id="loading-msg" class="text-sm font-bold text-slate-700">Leyendo archivos...</p>
    <p id="loading-sub" class="text-xs text-slate-400">Por favor espera</p>
  </div>
</div>

<script>
// ════════════════════════════════════════════════════════════════════
//  PELITOS DOCS — Visor Integrado, Edición y Eliminación
// ════════════════════════════════════════════════════════════════════

const FS_API = 'showDirectoryPicker' in window;

const state = {{
  currentEntries : [],
  filtrados      : [],
  selObj         : null,
  selSet         : new Set(),
  navStack       : [],
  currentHandle  : null,
  dirHandle      : null,
  favoritos      : new Set(),
  recientes      : [],
  vistaActual    : 'lista',
  loadVersion    : 0,
  toastTimer     : null,
  modoAPI        : false,
}};

let entryVisorActual = null;
let entryParaRenombrar = null;

// Escapar caracteres para prevenir XSS
function esc(str) {{
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

// ─── Diccionario de extensiones ───────────────────────────────────
const EXT_META = {{
  // Documentos Word
  doc   :{{label:'Word',        badge:'ext-doc',   icon:'file-text',        color:'text-blue-600'   }},
  docx  :{{label:'Word',        badge:'ext-doc',   icon:'file-text',        color:'text-blue-600'   }},
  docm  :{{label:'Word',        badge:'ext-doc',   icon:'file-text',        color:'text-blue-600'   }},
  dotx  :{{label:'Word',        badge:'ext-doc',   icon:'file-text',        color:'text-blue-600'   }},
  // Hojas de cálculo Excel
  xls   :{{label:'Excel',       badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  xlsx  :{{label:'Excel',       badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  xlsm  :{{label:'Excel',       badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  csv   :{{label:'CSV',         badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-700'}},
  tsv   :{{label:'TSV',         badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-700'}},
  ods   :{{label:'Excel',       badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  // Presentaciones PowerPoint
  ppt   :{{label:'PowerPoint',  badge:'ext-ppt',   icon:'presentation',     color:'text-orange-600' }},
  pptx  :{{label:'PowerPoint',  badge:'ext-ppt',   icon:'presentation',     color:'text-orange-600' }},
  // PDF
  pdf   :{{label:'PDF',         badge:'ext-pdf',   icon:'file-text',        color:'text-red-600'    }},
  // Imágenes
  jpg   :{{label:'Imagen JPG',  badge:'ext-img',   icon:'image',            color:'text-pink-600'   }},
  jpeg  :{{label:'Imagen JPG',  badge:'ext-img',   icon:'image',            color:'text-pink-600'   }},
  png   :{{label:'Imagen PNG',  badge:'ext-img',   icon:'image',            color:'text-pink-600'   }},
  gif   :{{label:'GIF',         badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  webp  :{{label:'WebP',        badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  svg   :{{label:'SVG',         badge:'ext-img',   icon:'image',            color:'text-purple-600' }},
  bmp   :{{label:'BMP',         badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  tiff  :{{label:'TIFF',        badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  psd   :{{label:'Photoshop',   badge:'ext-img',   icon:'image',            color:'text-blue-700'   }},
  ai    :{{label:'Illustrator', badge:'ext-img',   icon:'image',            color:'text-orange-700' }},
  // Videos
  mp4   :{{label:'Video MP4',   badge:'ext-vid',   icon:'video',            color:'text-purple-600' }},
  mov   :{{label:'Video MOV',   badge:'ext-vid',   icon:'video',            color:'text-purple-600' }},
  avi   :{{label:'Video AVI',   badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  mkv   :{{label:'Video MKV',   badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  webm  :{{label:'Video WebM',  badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  // Audio
  mp3   :{{label:'Audio MP3',   badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  wav   :{{label:'Audio WAV',   badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  flac  :{{label:'Audio FLAC',  badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  ogg   :{{label:'Audio OGG',   badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  m4a   :{{label:'Audio M4A',   badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  // Comprimidos
  zip   :{{label:'ZIP',         badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  rar   :{{label:'RAR',         badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  '7z'  :{{label:'7-Zip',       badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  tar   :{{label:'TAR',         badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  gz    :{{label:'GZIP',        badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  // Texto
  txt   :{{label:'Texto',       badge:'ext-txt',   icon:'file-text',        color:'text-slate-600'  }},
  md    :{{label:'Markdown',    badge:'ext-txt',   icon:'file-text',        color:'text-slate-600'  }},
  xml   :{{label:'XML',         badge:'ext-txt',   icon:'file-code',        color:'text-slate-600'  }},
  // Código
  json  :{{label:'JSON',        badge:'ext-js',    icon:'braces',           color:'text-yellow-700' }},
  html  :{{label:'HTML',        badge:'ext-html',  icon:'file-code',        color:'text-rose-600'   }},
  css   :{{label:'CSS',         badge:'ext-html',  icon:'file-code',        color:'text-blue-500'   }},
  js    :{{label:'JavaScript',  badge:'ext-js',    icon:'file-code',        color:'text-yellow-700' }},
  ts    :{{label:'TypeScript',  badge:'ext-js',    icon:'file-code',        color:'text-blue-600'   }},
  py    :{{label:'Python',      badge:'ext-code',  icon:'file-code',        color:'text-green-700'  }},
  sql   :{{label:'SQL',         badge:'ext-code',  icon:'database',         color:'text-orange-700' }},
  sh    :{{label:'Script',      badge:'ext-code',  icon:'terminal',         color:'text-slate-700'  }},
  bat   :{{label:'Batch',       badge:'ext-code',  icon:'terminal',         color:'text-slate-700'  }},
}};

function getExtMeta(nombre, esDir) {{
  if (esDir) return {{label:'Carpeta', badge:'folder-badge', icon:'folder', color:'text-amber-500'}};
  const ext = nombre.includes('.') ? nombre.split('.').pop().toLowerCase() : '';
  return EXT_META[ext] || {{label: ext ? ext.toUpperCase() : 'Archivo', badge:'ext-default', icon:'file', color:'text-slate-500'}};
}}

function formatSize(bytes) {{
  if (bytes == null || bytes < 0) return '—';
  if (bytes === 0) return '0 B';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes/1024).toFixed(1) + ' KB';
  if (bytes < 1073741824) return (bytes/1048576).toFixed(1) + ' MB';
  return (bytes/1073741824).toFixed(2) + ' GB';
}}

function formatDate(ts) {{
  if (!ts) return '—';
  try {{
    return new Intl.DateTimeFormat('es-PE',{{
      day:'2-digit',month:'2-digit',year:'numeric',
      hour:'2-digit',minute:'2-digit'
    }}).format(new Date(ts));
  }} catch {{ return '—'; }}
}}

// ─── ACCIONES DE CARGA ────────────────────────────────────────────
function abrirArchivos() {{
  document.getElementById('input-files').click();
}}

document.getElementById('input-files').addEventListener('change', function(e) {{
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  cargarArchivos(files, state.currentEntries.length > 0);
  e.target.value = '';
}});

function abrirDirectorio() {{
  if (FS_API) {{
    abrirConFsApi();
  }} else {{
    document.getElementById('input-folder').click();
  }}
}}

async function abrirConFsApi() {{
  try {{
    const handle = await window.showDirectoryPicker({{mode:'read'}});
    state.dirHandle     = handle;
    state.currentHandle  = handle;
    state.navStack      = [handle];
    state.modoAPI       = true;
    document.getElementById('panel-arbol').style.display = '';
    document.getElementById('nota-arbol-flat').classList.add('hidden');
    document.getElementById('btn-subir').classList.remove('hidden');
    await cargarEntradasAPI(handle);
    navActivar('explorador');
  }} catch(e) {{
    if (e.name !== 'AbortError') toast('Error al abrir carpeta: ' + e.message, true);
  }}
}}

document.getElementById('input-folder').addEventListener('change', function(e) {{
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  state.modoAPI = false;
  document.getElementById('panel-arbol').style.display = 'none';
  document.getElementById('nota-arbol-flat').classList.remove('hidden');
  document.getElementById('btn-subir').classList.add('hidden');
  cargarEntradasPlanas(files);
  navActivar('explorador');
  e.target.value = '';
}});

function cargarArchivos(files, append = false) {{
  mostrarLoading('Procesando archivos...', files.length + ' archivo(s)');
  try {{
    const nuevasEntradas = Array.from(files).map(f => ({{
      name: f.name,
      kind: 'file',
      size: f.size,
      lastMod: f.lastModified,
      handle: null,
      fileObj: f
    }}));

    let entries = append ? [...state.currentEntries] : [];
    nuevasEntradas.forEach(ne => {{
      const idx = entries.findIndex(e => e.name === ne.name);
      if (idx >= 0) entries[idx] = ne;
      else entries.push(ne);
    }});

    entries.sort((a,b) => {{
      if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
      return a.name.localeCompare(b.name, 'es', {{sensitivity:'base'}});
    }});

    const totalSize = entries.reduce((acc, e) => acc + (e.size || 0), 0);
    const rutaLbl = document.getElementById('label-ruta-actual');
    if (rutaLbl) rutaLbl.textContent = 'Archivos cargados (' + entries.length + ')';

    document.getElementById('panel-arbol').style.display = 'none';
    document.getElementById('nota-arbol-flat').classList.remove('hidden');
    document.getElementById('btn-subir').classList.add('hidden');
    state.modoAPI = false;

    aplicarNuevasEntradas(entries, totalSize, 'Archivos cargados');
    navActivar('explorador');
    toast(nuevasEntradas.length + ' archivo(s) cargado(s) exitosamente');
  }} catch(e) {{
    toast('Error al cargar archivos: ' + e.message, true);
  }}
  ocultarLoading();
}}

// Drag & Drop
window.addEventListener('dragover', (e) => {{
  e.preventDefault();
  document.body.classList.add('drag-over');
}});

window.addEventListener('dragleave', (e) => {{
  if (e.clientX <= 0 || e.clientY <= 0) {{
    document.body.classList.remove('drag-over');
  }}
}});

window.addEventListener('drop', (e) => {{
  e.preventDefault();
  document.body.classList.remove('drag-over');
  if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length) {{
    cargarArchivos(e.dataTransfer.files, state.currentEntries.length > 0);
  }}
}});

// ─── Lectura de carpetas ──────────────────────────────────────────
async function cargarEntradasAPI(dirHandle) {{
  const version = ++state.loadVersion;
  mostrarLoading('Leyendo carpeta...', dirHandle.name);
  try {{
    const entries = [];
    let totalSize = 0;
    for await (const [name, handle] of dirHandle.entries()) {{
      if (version !== state.loadVersion) {{ ocultarLoading(); return; }}
      let size = null, lastMod = null;
      if (handle.kind === 'file') {{
        try {{
          const file = await handle.getFile();
          size = file.size; lastMod = file.lastModified; totalSize += file.size;
        }} catch {{}}
      }}
      entries.push({{name, handle, kind: handle.kind, size, lastMod, fileObj: null}});
    }}
    if (version !== state.loadVersion) {{ ocultarLoading(); return; }}
    entries.sort((a,b) => {{
      if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
      return a.name.localeCompare(b.name, 'es', {{sensitivity:'base'}});
    }});
    const rutaLbl = document.getElementById('label-ruta-actual');
    if (rutaLbl) rutaLbl.textContent = dirHandle.name + '/';
    aplicarNuevasEntradas(entries, totalSize, dirHandle.name);
  }} catch(e) {{
    toast('Error al leer carpeta: ' + e.message, true);
  }}
  ocultarLoading();
}}

function cargarEntradasPlanas(files) {{
  mostrarLoading('Procesando carpeta...', files.length + ' archivos');
  try {{
    let totalSize = 0;
    const nombreCarpeta = files[0]?.webkitRelativePath?.split('/')[0] || 'Carpeta seleccionada';
    const entradasMap = new Map();

    files.forEach(f => {{
      const partes = f.webkitRelativePath.split('/');
      if (partes.length === 2) {{
        const nombre = partes[1];
        totalSize += f.size;
        entradasMap.set(nombre, {{
          name: nombre, kind:'file', size: f.size,
          lastMod: f.lastModified, handle: null, fileObj: f
        }});
      }} else if (partes.length >= 3) {{
        const carpeta = partes[1];
        if (!entradasMap.has(carpeta)) {{
          entradasMap.set(carpeta, {{
            name: carpeta, kind:'directory', size: null,
            lastMod: null, handle: null, fileObj: null
          }});
        }}
      }}
    }});

    const entries = Array.from(entradasMap.values());
    entries.sort((a,b) => {{
      if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
      return a.name.localeCompare(b.name, 'es', {{sensitivity:'base'}});
    }});

    const lbl = document.getElementById('label-ruta-actual');
    if (lbl) lbl.textContent = nombreCarpeta + '/';
    aplicarNuevasEntradas(entries, totalSize, nombreCarpeta);
  }} catch(e) {{
    toast('Error al procesar carpeta: ' + e.message, true);
  }}
  ocultarLoading();
}}

function aplicarNuevasEntradas(entries, totalSize, nombreDir) {{
  state.currentEntries = entries;
  state.filtrados      = [];
  state.selObj         = null;
  state.selSet         = new Set();

  const buscador = document.getElementById('buscador-top');
  if (buscador) buscador.value = '';
  const filtroTipo = document.getElementById('filtro-tipo-top');
  if (filtroTipo) filtroTipo.value = '';

  renderTabla(entries);
  if (state.modoAPI) renderArbol();
  actualizarStats(entries, totalSize);
  actualizarBreadcrumb(nombreDir);
  actualizarInspector(null);
}}

function actualizarStats(entries, totalSize) {{
  const carpetas = entries.filter(e => e.kind === 'directory').length;
  const archivos = entries.filter(e => e.kind === 'file').length;
  const tipos    = new Set(entries.filter(e => e.kind==='file')
                    .map(e => e.name.includes('.') ? e.name.split('.').pop().toLowerCase() : '_')).size;
  document.getElementById('stat-total').textContent    = archivos;
  document.getElementById('stat-carpetas').textContent  = carpetas;
  document.getElementById('stat-tamano').textContent    = formatSize(totalSize);
  document.getElementById('stat-tipos').textContent     = tipos;
  document.getElementById('status-bar').textContent     =
    entries.length + ' elementos (' + archivos + ' archivos, ' + carpetas + ' carpetas)';
}}

// ─── RENDER TABLA CON BOTONES DE EDITAR Y ELIMINAR ────────────────
function renderTabla(entries) {{
  const tbody = document.getElementById('tabla-body');
  tbody.innerHTML = '';

  if (entries.length === 0) {{
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 6;
    td.className = 'text-center py-16 text-slate-400 text-sm';
    td.innerHTML = `
      <i data-lucide="folder-search" class="w-10 h-10 mx-auto mb-3 opacity-30"></i>
      <p class="font-medium">No hay archivos para mostrar con este filtro.</p>
    `;
    tr.appendChild(td);
    tbody.appendChild(tr);
    if (window.lucide) lucide.createIcons();
    return;
  }}

  if (state.modoAPI && state.navStack.length > 1) {{
    const trUp = document.createElement('tr');
    trUp.className = 'cursor-pointer hover:bg-slate-50 transition';
    trUp.ondblclick = subirNivel;
    trUp.innerHTML = `
      <td class="py-2.5 px-3"></td>
      <td class="py-2.5 px-3" colspan="5">
        <div class="flex items-center gap-2 text-slate-400 text-sm hover:text-purple-600">
          <i data-lucide="corner-left-up" class="w-4 h-4"></i>
          <span class="font-medium">.. (subir un nivel)</span>
        </div>
      </td>`;
    tbody.appendChild(trUp);
  }}

  entries.forEach(entry => {{
    const meta       = getExtMeta(entry.name, entry.kind === 'directory');
    const isSelected = state.selSet.has(entry);
    const tr = document.createElement('tr');
    tr.className = 'cursor-pointer transition hover:bg-slate-50 ' + (isSelected ? 'row-selected' : '');
    tr.onclick  = (e) => seleccionar(entry, e);
    // Doble clic abre el visor directamente sin descargar
    tr.ondblclick = () => abrirEntrada(entry);

    // Checkbox
    const tdChk = document.createElement('td');
    tdChk.className = 'py-2.5 px-3';
    const chk = document.createElement('input');
    chk.type = 'checkbox'; chk.checked = isSelected;
    chk.className = 'rounded text-purple-600 focus:ring-0 w-3.5 h-3.5';
    chk.onclick = (e) => {{ e.stopPropagation(); toggleSel(entry); }};
    tdChk.appendChild(chk);
    tr.appendChild(tdChk);

    // Nombre
    const tdName = document.createElement('td');
    tdName.className = 'py-2.5 px-3';
    const nameDiv = document.createElement('div');
    nameDiv.className = 'flex items-center gap-2';
    const lIcon = document.createElement('i');
    lIcon.setAttribute('data-lucide', meta.icon);
    lIcon.className = 'w-4 h-4 ' + meta.color + ' shrink-0';
    const nameSpan = document.createElement('span');
    nameSpan.className = 'font-medium text-slate-800 truncate max-w-xs text-sm';
    nameSpan.title = entry.name;
    nameSpan.textContent = entry.name;
    nameDiv.appendChild(lIcon);
    nameDiv.appendChild(nameSpan);
    if (state.favoritos.has(entry.name)) {{
      const starI = document.createElement('i');
      starI.setAttribute('data-lucide','star');
      starI.className = 'w-3.5 h-3.5 text-amber-400 shrink-0 fill-amber-400';
      nameDiv.appendChild(starI);
    }}
    tdName.appendChild(nameDiv);
    tr.appendChild(tdName);

    // Tipo
    const tdTipo = document.createElement('td');
    tdTipo.className = 'py-2.5 px-3';
    const badge = document.createElement('span');
    badge.className = 'ext-badge ' + meta.badge;
    badge.textContent = meta.label;
    tdTipo.appendChild(badge);
    tr.appendChild(tdTipo);

    // Fecha
    const tdFecha = document.createElement('td');
    tdFecha.className = 'py-2.5 px-3 text-slate-400 text-xs';
    tdFecha.textContent = formatDate(entry.lastMod);
    tr.appendChild(tdFecha);

    // Tamaño
    const tdSize = document.createElement('td');
    tdSize.className = 'py-2.5 px-3 text-slate-400 font-mono text-xs text-right';
    if (entry.kind === 'directory') {{
      const sp = document.createElement('span');
      sp.className = 'text-amber-600 font-semibold';
      sp.textContent = 'Carpeta';
      tdSize.appendChild(sp);
    }} else {{
      tdSize.textContent = formatSize(entry.size);
    }}
    tr.appendChild(tdSize);

    // Acciones: Ver / Editar / Eliminar
    const tdAcc = document.createElement('td');
    tdAcc.className = 'py-2 px-2 text-center';
    tdAcc.innerHTML = `
      <div class="flex items-center justify-center gap-1">
        <button onclick="event.stopPropagation(); abrirVisorPara(state.currentEntries[${{state.currentEntries.indexOf(entry)}}])"
          class="text-slate-400 hover:text-purple-700 hover:bg-purple-50 p-1.5 rounded transition"
          title="Ver sin descargar">
          <i data-lucide="eye" class="w-3.5 h-3.5"></i>
        </button>
        <button onclick="event.stopPropagation(); abrirModalRenombrarPara(state.currentEntries[${{state.currentEntries.indexOf(entry)}}])"
          class="text-slate-400 hover:text-blue-600 hover:bg-blue-50 p-1.5 rounded transition"
          title="Renombrar / Editar">
          <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
        </button>
        <button onclick="event.stopPropagation(); eliminarEntrada(state.currentEntries[${{state.currentEntries.indexOf(entry)}}])"
          class="text-slate-400 hover:text-red-600 hover:bg-red-50 p-1.5 rounded transition"
          title="Eliminar">
          <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
        </button>
      </div>
    `;
    tr.appendChild(tdAcc);

    tbody.appendChild(tr);
  }});

  if (window.lucide) lucide.createIcons();
}}

// ─── VISOR INTEGRADO (NO DESCARGA) ────────────────────────────────
async function abrirVisorPara(entry) {{
  if (!entry) return;
  entryVisorActual = entry;
  const modal = document.getElementById('modal-visor');
  const nombreEl = document.getElementById('visor-nombre');
  const badgeEl = document.getElementById('visor-badge');
  const tamanoEl = document.getElementById('visor-tamano');
  const iconEl = document.getElementById('visor-icon');
  const contenido = document.getElementById('visor-contenido');

  const meta = getExtMeta(entry.name, entry.kind === 'directory');
  nombreEl.textContent = entry.name;
  badgeEl.className = 'ext-badge ' + meta.badge;
  badgeEl.textContent = meta.label;
  tamanoEl.textContent = entry.kind === 'directory' ? 'Carpeta' : formatSize(entry.size);
  iconEl.innerHTML = `<i data-lucide="${{meta.icon}}" class="w-4 h-4"></i>`;

  contenido.innerHTML = `
    <div class="flex flex-col items-center gap-3 text-slate-400">
      <div class="w-10 h-10 border-4 border-purple-200 border-t-purple-700 rounded-full animate-spin"></div>
      <p class="text-sm font-medium">Cargando previsualización sin descargar...</p>
    </div>
  `;
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  if (window.lucide) lucide.createIcons();

  try {{
    let file = null;
    if (entry.fileObj) file = entry.fileObj;
    else if (entry.handle) file = await entry.handle.getFile();

    if (!file) {{
      contenido.innerHTML = `<p class="text-slate-400">No se pudo acceder al archivo seleccionado.</p>`;
      return;
    }}

    const ext = entry.name.includes('.') ? entry.name.split('.').pop().toLowerCase() : '';

    // 1. WORD (.docx, .docm)
    if (['docx', 'docm'].includes(ext)) {{
      if (window.mammoth) {{
        const arrayBuffer = await file.arrayBuffer();
        const res = await window.mammoth.convertToHtml({{ arrayBuffer }});
        contenido.innerHTML = `
          <div class="bg-white rounded-xl shadow-lg p-8 sm:p-12 max-w-3xl w-full mx-auto my-auto overflow-auto max-h-full border border-slate-200 word-doc">
            ${{res.value || '<p class="text-slate-400 italic">Documento Word sin texto</p>'}}
          </div>
        `;
      }} else {{
        contenido.innerHTML = `
          <div class="bg-white p-8 rounded-2xl shadow max-w-md text-center space-y-3">
            <i data-lucide="file-text" class="w-12 h-12 text-blue-600 mx-auto"></i>
            <h4 class="font-bold text-slate-800 text-base">${{entry.name}}</h4>
            <p class="text-xs text-slate-500">Documento de Word listo.</p>
          </div>
        `;
      }}
    }}
    // 2. EXCEL (.xlsx, .xls, .csv, .tsv, .ods)
    else if (['xlsx', 'xls', 'csv', 'tsv', 'ods'].includes(ext)) {{
      if (window.XLSX) {{
        const arrayBuffer = await file.arrayBuffer();
        const workbook = window.XLSX.read(arrayBuffer, {{ type: 'array' }});
        const sheetName = workbook.SheetNames[0] || 'Hoja1';
        const worksheet = workbook.Sheets[sheetName];
        const htmlTable = window.XLSX.utils.sheet_to_html(worksheet, {{ editable: false }});
        contenido.innerHTML = `
          <div class="bg-white rounded-xl shadow-lg p-4 max-w-full w-full h-full overflow-auto flex flex-col border border-slate-200">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-3 shrink-0">
              <span class="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <i data-lucide="sheet" class="w-4 h-4 text-emerald-600"></i> Hoja activa: ${{sheetName}}
              </span>
              <span class="text-xs text-slate-400">Total hojas: ${{workbook.SheetNames.length}}</span>
            </div>
            <div class="overflow-auto flex-1 border border-slate-200 rounded-lg text-xs">
              ${{htmlTable}}
            </div>
          </div>
        `;
      }} else {{
        const txt = await file.text();
        contenido.innerHTML = `
          <div class="bg-white rounded-xl shadow p-4 max-w-full w-full h-full overflow-auto text-xs font-mono">
            <pre>${{esc(txt)}}</pre>
          </div>
        `;
      }}
    }}
    // 3. PDF (.pdf)
    else if (ext === 'pdf') {{
      const url = URL.createObjectURL(file);
      contenido.innerHTML = `
        <iframe src="${{url}}#toolbar=1" class="w-full h-full rounded-xl border border-slate-200 bg-white shadow-lg" frameborder="0"></iframe>
      `;
    }}
    // 4. IMÁGENES (.jpg, .jpeg, .png, .gif, .webp, .svg, .bmp)
    else if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'].includes(ext)) {{
      const url = URL.createObjectURL(file);
      contenido.innerHTML = `
        <div class="flex items-center justify-center w-full h-full p-2">
          <img src="${{url}}" alt="${{entry.name}}" class="max-w-full max-h-full object-contain rounded-xl shadow-xl bg-white p-2 border border-slate-200">
        </div>
      `;
    }}
    // 5. VIDEOS (.mp4, .webm, .mov, .mkv, .avi)
    else if (['mp4', 'webm', 'mov', 'mkv', 'avi'].includes(ext)) {{
      const url = URL.createObjectURL(file);
      contenido.innerHTML = `
        <div class="flex items-center justify-center w-full h-full p-2">
          <video controls autoplay class="max-w-full max-h-full rounded-xl shadow-2xl bg-black">
            <source src="${{url}}">
          </video>
        </div>
      `;
    }}
    // 6. AUDIO (.mp3, .wav, .ogg, .m4a, .flac)
    else if (['mp3', 'wav', 'ogg', 'm4a', 'flac'].includes(ext)) {{
      const url = URL.createObjectURL(file);
      contenido.innerHTML = `
        <div class="bg-white p-8 rounded-2xl shadow-xl flex flex-col items-center gap-4 text-center max-w-md w-full border border-slate-200">
          <div class="w-20 h-20 bg-purple-100 text-purple-700 rounded-2xl flex items-center justify-center">
            <i data-lucide="music" class="w-10 h-10"></i>
          </div>
          <p class="font-bold text-slate-800 text-sm break-all">${{entry.name}}</p>
          <audio controls autoplay class="w-full mt-2">
            <source src="${{url}}">
          </audio>
        </div>
      `;
    }}
    // 7. TEXTO / CÓDIGO (.txt, .md, .json, .py, .js, .ts, .html, .css, .sql, .xml, .sh, .bat)
    else if (['txt', 'md', 'json', 'py', 'js', 'ts', 'html', 'css', 'sql', 'xml', 'sh', 'bat', 'log'].includes(ext)) {{
      const text = await file.text();
      contenido.innerHTML = `
        <div class="bg-slate-900 text-slate-100 p-6 rounded-xl shadow-xl max-w-4xl w-full h-full overflow-auto font-mono text-xs leading-relaxed select-text border border-slate-800">
          <pre><code>${{esc(text)}}</code></pre>
        </div>
      `;
    }}
    // 8. OTROS FORMATOS
    else {{
      contenido.innerHTML = `
        <div class="bg-white p-8 rounded-2xl shadow-lg max-w-md text-center space-y-3 border border-slate-200">
          <div class="w-16 h-16 bg-slate-100 rounded-2xl mx-auto flex items-center justify-center text-slate-600">
            <i data-lucide="${{meta.icon}}" class="w-8 h-8"></i>
          </div>
          <h4 class="font-bold text-slate-800 text-base break-all">${{entry.name}}</h4>
          <p class="text-xs text-slate-400">Tipo: ${{meta.label}} • Tamaño: ${{formatSize(entry.size)}}</p>
          <div class="flex items-center justify-center gap-2 pt-2">
            <button onclick="abrirModalRenombrarPara(entryVisorActual)" class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-4 py-2 rounded-xl transition">Renombrar</button>
            <button onclick="descargarArchivo(entryVisorActual)" class="bg-[#5B21B6] hover:bg-[#4C1D95] text-white text-xs font-bold px-4 py-2 rounded-xl transition">Descargar</button>
          </div>
        </div>
      `;
    }}
  }} catch(err) {{
    contenido.innerHTML = `
      <div class="bg-white p-6 rounded-2xl shadow text-center text-red-500 max-w-md">
        <i data-lucide="alert-circle" class="w-10 h-10 mx-auto mb-2"></i>
        <p class="font-bold text-sm">No se pudo cargar la vista previa</p>
        <p class="text-xs text-slate-400 mt-1">${{err.message}}</p>
      </div>
    `;
  }}

  addReciente(entry);
  if (window.lucide) lucide.createIcons();
}}

function cerrarVisor() {{
  const modal = document.getElementById('modal-visor');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  document.getElementById('visor-contenido').innerHTML = '';
  entryVisorActual = null;
}}

function editarNombreDesdeVisor() {{
  if (entryVisorActual) abrirModalRenombrarPara(entryVisorActual);
}}

function descargarArchivoActual() {{
  if (entryVisorActual) descargarArchivo(entryVisorActual);
}}

function eliminarArchivoActual() {{
  if (!entryVisorActual) return;
  const toDelete = entryVisorActual;
  cerrarVisor();
  eliminarEntrada(toDelete);
}}

// ─── ELIMINAR ARCHIVOS ────────────────────────────────────────────
function eliminarEntrada(entry, conConfirm = true) {{
  if (conConfirm && !confirm(`¿Estás seguro de eliminar "${{entry.name}}"?`)) return;
  const idx = state.currentEntries.indexOf(entry);
  if (idx >= 0) {{
    state.currentEntries.splice(idx, 1);
  }}
  state.selSet.delete(entry);
  if (state.selObj === entry) state.selObj = null;
  state.favoritos.delete(entry.name);

  const totalSize = state.currentEntries.reduce((acc, e) => acc + (e.size || 0), 0);
  actualizarStats(state.currentEntries, totalSize);
  aplicarFiltros();
  actualizarInspector(null);
  toast(`"${{entry.name}}" eliminado`);
}}

function eliminarArchivoSeleccionado() {{
  if (!state.selObj) return;
  eliminarEntrada(state.selObj);
}}

function eliminarLoteSeleccionado() {{
  const seleccionados = Array.from(state.selSet);
  if (!seleccionados.length) return;
  if (!confirm(`¿Eliminar los ${{seleccionados.length}} archivo(s) seleccionados?`)) return;

  seleccionados.forEach(entry => {{
    const idx = state.currentEntries.indexOf(entry);
    if (idx >= 0) state.currentEntries.splice(idx, 1);
    state.favoritos.delete(entry.name);
  }});
  state.selSet.clear();
  state.selObj = null;

  const totalSize = state.currentEntries.reduce((acc, e) => acc + (e.size || 0), 0);
  actualizarStats(state.currentEntries, totalSize);
  aplicarFiltros();
  actualizarInspector(null);
  toast(`${{seleccionados.length}} archivo(s) eliminados`);
}}

// ─── EDITAR / RENOMBRAR ───────────────────────────────────────────
function abrirModalRenombrarPara(entry) {{
  entryParaRenombrar = entry;
  const input = document.getElementById('input-nuevo-nombre');
  input.value = entry.name;
  document.getElementById('modal-renombrar').classList.remove('hidden');
  document.getElementById('modal-renombrar').classList.add('flex');
  setTimeout(() => input.focus(), 50);
}}

function abrirModalRenombrar() {{
  if (state.selObj) abrirModalRenombrarPara(state.selObj);
}}

function cerrarModalRenombrar() {{
  document.getElementById('modal-renombrar').classList.add('hidden');
  document.getElementById('modal-renombrar').classList.remove('flex');
  entryParaRenombrar = null;
}}

function guardarNuevoNombre() {{
  if (!entryParaRenombrar) return;
  const input = document.getElementById('input-nuevo-nombre');
  const nuevoNombre = input.value.trim();
  if (!nuevoNombre) {{
    toast('El nombre no puede estar vacío', true);
    return;
  }}
  const viejoNombre = entryParaRenombrar.name;
  entryParaRenombrar.name = nuevoNombre;

  if (state.favoritos.has(viejoNombre)) {{
    state.favoritos.delete(viejoNombre);
    state.favoritos.add(nuevoNombre);
  }}

  cerrarModalRenombrar();
  aplicarFiltros();
  actualizarInspector(entryParaRenombrar);

  const visorNombre = document.getElementById('visor-nombre');
  if (visorNombre && entryVisorActual === entryParaRenombrar) {{
    visorNombre.textContent = nuevoNombre;
  }}

  toast(`Renombrado a: ${{nuevoNombre}}`);
}}

// Descargar archivo si el usuario explícitamente lo solicita
function descargarArchivo(entry) {{
  if (!entry) return;
  const getF = async () => {{
    if (entry.fileObj) return entry.fileObj;
    if (entry.handle) return await entry.handle.getFile();
    return null;
  }};
  getF().then(f => {{
    if (!f) return;
    const url = URL.createObjectURL(f);
    const a = document.createElement('a');
    a.href = url;
    a.download = entry.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }});
}}

// ─── Árbol ────────────────────────────────────────────────────────
function renderArbol() {{
  const arbol = document.getElementById('arbol-dir');
  arbol.innerHTML = '';
  state.navStack.forEach((h, idx) => {{
    const isCurrent = idx === state.navStack.length - 1;
    const div = document.createElement('div');
    div.className = 'flex items-center gap-1.5 py-1.5 px-2 rounded cursor-pointer ' +
      (isCurrent ? 'tree-active' : 'text-slate-600 hover:bg-slate-200/60');
    div.style.paddingLeft = (8 + idx * 10) + 'px';
    const icon = document.createElement('i');
    icon.setAttribute('data-lucide', idx === 0 ? 'hard-drive' : 'folder');
    icon.className = 'w-3.5 h-3.5 shrink-0 ' + (isCurrent ? 'text-amber-600' : 'text-amber-500');
    const sp = document.createElement('span');
    sp.className = 'truncate text-xs font-medium';
    sp.textContent = h.name;
    div.appendChild(icon); div.appendChild(sp);
    div.onclick = () => navArbol(idx);
    arbol.appendChild(div);
  }});
  if (window.lucide) lucide.createIcons();
}}

async function navArbol(idx) {{
  if (!state.modoAPI || idx === state.navStack.length - 1) return;
  state.navStack = state.navStack.slice(0, idx + 1);
  state.currentHandle = state.navStack[state.navStack.length - 1];
  await cargarEntradasAPI(state.currentHandle);
}}

async function abrirEntrada(entry) {{
  if (!entry) return;
  if (entry.kind === 'directory') {{
    if (state.modoAPI && entry.handle) {{
      state.navStack.push(entry.handle);
      state.currentHandle = entry.handle;
      await cargarEntradasAPI(entry.handle);
    }} else {{
      toast('Navega dentro de subcarpetas seleccionándolas con "Abrir Carpeta".');
    }}
  }} else {{
    // Abrir directamente en el visor integrado sin descargar
    await abrirVisorPara(entry);
  }}
}}

async function subirNivel() {{
  if (!state.modoAPI || state.navStack.length <= 1) return;
  state.navStack.pop();
  state.currentHandle = state.navStack[state.navStack.length - 1];
  await cargarEntradasAPI(state.currentHandle);
}}

async function actualizarDirectorio() {{
  if (state.modoAPI && state.currentHandle) {{
    await cargarEntradasAPI(state.currentHandle);
    toast('Carpeta actualizada');
  }} else if (state.currentEntries.length) {{
    toast('Listado actualizado');
  }} else {{
    toast('No hay archivos cargados.', true);
  }}
}}

// ─── Selección ────────────────────────────────────────────────────
function seleccionar(entry, event) {{
  if (event && event.ctrlKey) {{
    if (state.selSet.has(entry)) state.selSet.delete(entry);
    else state.selSet.add(entry);
  }} else {{
    state.selSet = new Set([entry]);
  }}
  state.selObj = entry;
  actualizarInspector(entry);
  renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
  actualizarBarraSeleccion();
}}

function toggleSel(entry) {{
  if (state.selSet.has(entry)) state.selSet.delete(entry);
  else state.selSet.add(entry);
  actualizarBarraSeleccion();
}}

function selTodos(chk) {{
  const lista = state.filtrados.length ? state.filtrados : state.currentEntries;
  if (chk.checked) lista.forEach(e => state.selSet.add(e));
  else state.selSet.clear();
  renderTabla(lista);
  actualizarBarraSeleccion();
}}

function actualizarBarraSeleccion() {{
  const count = state.selSet.size;
  document.getElementById('status-sel').textContent = count + ' seleccionados';
  const btnLote = document.getElementById('btn-eliminar-lote');
  if (btnLote) {{
    if (count > 0) btnLote.classList.remove('hidden');
    else btnLote.classList.add('hidden');
  }}
}}

// ─── Inspector ────────────────────────────────────────────────────
function actualizarInspector(entry) {{
  const body    = document.getElementById('inspector-body');
  const actions = document.getElementById('inspector-actions');
  if (!entry) {{
    body.innerHTML = `
      <div class="text-center text-slate-300 py-10">
        <i data-lucide="file-search" class="w-9 h-9 mx-auto mb-2"></i>
        <p class="text-sm">Selecciona un archivo</p>
      </div>`;
    actions.classList.add('hidden');
    if (window.lucide) lucide.createIcons();
    return;
  }}
  const meta  = getExtMeta(entry.name, entry.kind === 'directory');
  const isFav = state.favoritos.has(entry.name);

  body.innerHTML = `
    <div class="flex flex-col items-center py-3 border-b border-slate-100">
      <div class="w-14 h-14 rounded-xl flex items-center justify-center bg-slate-100 mb-2">
        <i data-lucide="${{meta.icon}}" class="w-8 h-8 ${{meta.color}}"></i>
      </div>
      <p class="font-bold text-slate-800 text-center text-xs break-all leading-tight px-1">${{entry.name}}</p>
      <span class="ext-badge ${{meta.badge}} mt-1">${{meta.label}}</span>
    </div>
    <div class="space-y-1.5 text-xs pt-2">
      <div class="flex justify-between gap-1">
        <span class="text-slate-400">Tipo:</span>
        <span class="font-semibold text-slate-700">${{meta.label}}</span>
      </div>
      <div class="flex justify-between gap-1">
        <span class="text-slate-400">Tamaño:</span>
        <span class="font-semibold text-slate-700">${{entry.kind==='directory'?'—':formatSize(entry.size)}}</span>
      </div>
      <div class="flex justify-between gap-1">
        <span class="text-slate-400">Modificado:</span>
        <span class="font-semibold text-slate-700">${{formatDate(entry.lastMod)}}</span>
      </div>
      ${{isFav ? '<div class="flex items-center gap-1 text-amber-600 font-semibold mt-1 text-xs"><i data-lucide="star" class="w-3 h-3 fill-amber-400"></i> En favoritos</div>' : ''}}
    </div>
  `;

  actions.classList.remove('hidden');
  const btnFav = document.getElementById('btn-fav-inspector');
  btnFav.innerHTML =
    `<i data-lucide="star" class="w-3 h-3 ${{isFav ? 'text-amber-400 fill-amber-400' : 'text-slate-400'}}"></i> ${{isFav ? 'Quitar' : 'Fav.'}}`;
  if (window.lucide) lucide.createIcons();
}}

function abrirDocumento() {{
  if (state.selObj) abrirVisorPara(state.selObj);
}}

function copiarRutaInspector() {{
  if (!state.selObj) return;
  navigator.clipboard.writeText(state.selObj.name)
    .then(() => toast('Nombre copiado al portapapeles'))
    .catch(() => toast('Error al copiar', true));
}}

function toggleFavoritoInspector() {{
  if (!state.selObj) return;
  const nombre = state.selObj.name;
  if (state.favoritos.has(nombre)) {{
    state.favoritos.delete(nombre);
    toast('Removido de favoritos');
  }} else {{
    state.favoritos.add(nombre);
    toast('Agregado a favoritos: ' + nombre);
  }}
  actualizarInspector(state.selObj);
  renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
  renderListaFavoritos();
}}

// ─── Filtros ──────────────────────────────────────────────────────
function aplicarFiltros() {{
  if (!state.currentEntries.length) return;
  const q    = (document.getElementById('buscador-top')?.value || '').toLowerCase().trim();
  const tipo = document.getElementById('filtro-tipo-top')?.value || '';
  const ord  = document.getElementById('ordenar-por')?.value || 'nombre';

  let resultado = state.currentEntries.filter(entry => {{
    const matchQ = !q || entry.name.toLowerCase().includes(q);
    let matchTipo = true;
    if (tipo === 'folder') {{
      matchTipo = entry.kind === 'directory';
    }} else if (tipo && entry.kind === 'file') {{
      const ext = entry.name.includes('.') ? entry.name.split('.').pop().toLowerCase() : '';
      const m = EXT_META[ext];
      switch(tipo) {{
        case 'pdf' :
          matchTipo = ext === 'pdf';
          break;
        case 'doc' :
          matchTipo = ['doc','docx','docm','dotx'].includes(ext);
          break;
        case 'xls' :
          matchTipo = ['xls','xlsx','xlsm','csv','tsv','ods'].includes(ext);
          break;
        case 'ppt' :
          matchTipo = ['ppt','pptx'].includes(ext);
          break;
        case 'img' :
          matchTipo = ['jpg','jpeg','png','gif','webp','svg','bmp','tiff','psd','ai'].includes(ext) || m?.badge === 'ext-img';
          break;
        case 'vid' :
          matchTipo = ['mp4','mov','avi','mkv','webm'].includes(ext) || m?.badge === 'ext-vid';
          break;
        case 'mp3' :
          matchTipo = ['mp3','wav','flac','ogg','m4a'].includes(ext) || m?.badge === 'ext-mp3';
          break;
        case 'zip' :
          matchTipo = ['zip','rar','7z','tar','gz'].includes(ext) || m?.badge === 'ext-zip';
          break;
        case 'txt' :
          matchTipo = ['txt','md','xml','log'].includes(ext) || m?.badge === 'ext-txt';
          break;
        case 'code':
          matchTipo = ['py','js','ts','html','css','json','sql','sh','bat'].includes(ext) || ['ext-code','ext-js','ext-html'].includes(m?.badge || '');
          break;
      }}
    }}
    return matchQ && matchTipo;
  }});

  resultado.sort((a, b) => {{
    if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
    let va = a.name.toLowerCase(), vb = b.name.toLowerCase();
    if (ord === 'tipo') {{
      va = a.name.includes('.') ? a.name.split('.').pop().toLowerCase() : '';
      vb = b.name.includes('.') ? b.name.split('.').pop().toLowerCase() : '';
    }} else if (ord === 'tamano') {{
      va = a.size ?? -1; vb = b.size ?? -1;
    }} else if (ord === 'fecha') {{
      va = a.lastMod ?? 0; vb = b.lastMod ?? 0;
    }}
    if (va < vb) return -1; if (va > vb) return 1; return 0;
  }});

  state.filtrados = resultado;
  renderTabla(resultado);
  if (state.vistaActual === 'grid') renderGrid(resultado);
  document.getElementById('status-bar').textContent =
    resultado.length + ' de ' + state.currentEntries.length + ' elementos';
}}

function ordenarPor(col) {{
  const sel = document.getElementById('ordenar-por');
  if (sel) sel.value = col;
  aplicarFiltros();
}}

// ─── Vista Grid ───────────────────────────────────────────────────
function cambiarVista(tipo) {{
  state.vistaActual = tipo;
  const tablaScroll  = document.getElementById('tabla-scroll-container');
  const gridContainer = document.getElementById('vista-grid');
  const btnLista     = document.getElementById('btn-vista-lista');
  const btnGrid      = document.getElementById('btn-vista-grid');
  if (tipo === 'lista') {{
    tablaScroll.classList.remove('hidden');
    gridContainer.classList.add('hidden');
    btnLista.className = 'px-2.5 py-2 bg-purple-50 text-purple-700 hover:bg-purple-100 transition';
    btnGrid.className  = 'px-2.5 py-2 text-slate-500 hover:bg-slate-50 transition';
    renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
  }} else {{
    tablaScroll.classList.add('hidden');
    gridContainer.classList.remove('hidden');
    btnLista.className = 'px-2.5 py-2 text-slate-500 hover:bg-slate-50 transition';
    btnGrid.className  = 'px-2.5 py-2 bg-purple-50 text-purple-700 hover:bg-purple-100 transition';
    renderGrid(state.filtrados.length ? state.filtrados : state.currentEntries);
  }}
}}

function renderGrid(entries) {{
  const grid = document.getElementById('grid-archivos');
  grid.innerHTML = '';
  entries.forEach(entry => {{
    const meta = getExtMeta(entry.name, entry.kind === 'directory');
    const div = document.createElement('div');
    div.className = 'cursor-pointer bg-white border border-slate-200 rounded-xl p-2.5 flex flex-col items-center text-center hover:border-purple-400 hover:shadow transition select-none';
    div.ondblclick = () => abrirEntrada(entry);
    div.onclick    = () => seleccionar(entry, null);
    div.innerHTML = `
      <div class="w-11 h-11 flex items-center justify-center rounded-lg bg-slate-50 mb-1.5">
        <i data-lucide="${{meta.icon}}" class="w-7 h-7 ${{meta.color}}"></i>
      </div>
      <p class="text-xs text-slate-700 font-medium break-all leading-tight max-h-9 overflow-hidden" title="${{entry.name}}">${{entry.name}}</p>
      <span class="ext-badge ${{meta.badge}} mt-1">${{meta.label}}</span>
      ${{entry.kind==='file' ? '<p class="text-xs text-slate-400 mt-0.5">'+formatSize(entry.size)+'</p>' : ''}}
    `;
    grid.appendChild(div);
  }});
  if (window.lucide) lucide.createIcons();
}}

// ─── Breadcrumb ───────────────────────────────────────────────────
function actualizarBreadcrumb(nombreDir) {{
  const bar = document.getElementById('breadcrumb-bar');
  bar.innerHTML = '';
  if (state.modoAPI) {{
    state.navStack.forEach((h, idx) => {{
      if (idx > 0) {{
        const sep = document.createElement('i');
        sep.setAttribute('data-lucide','chevron-right');
        sep.className = 'w-3.5 h-3.5 text-slate-300 shrink-0';
        bar.appendChild(sep);
      }}
      const span = document.createElement('span');
      const isCurrent = idx === state.navStack.length - 1;
      span.className = 'cursor-pointer text-sm ' + (isCurrent
        ? 'text-purple-700 font-bold'
        : 'text-slate-500 hover:text-purple-600 hover:underline');
      span.textContent = h.name;
      span.onclick = () => navArbol(idx);
      bar.appendChild(span);
    }});
  }} else {{
    const span = document.createElement('span');
    span.className = 'text-sm text-purple-700 font-bold';
    span.textContent = nombreDir || 'Archivos cargados';
    bar.appendChild(span);
  }}
  if (window.lucide) lucide.createIcons();
}}

// ─── Recientes y Favoritos ────────────────────────────────────────
function addReciente(entry) {{
  state.recientes = [entry, ...state.recientes.filter(r => r.name !== entry.name)].slice(0, 20);
  renderListaRecientes();
}}

function renderListaRecientes() {{
  const cont = document.getElementById('lista-recientes');
  const empty = document.getElementById('lbl-rec-empty');
  if (!cont || !empty) return;
  if (!state.recientes.length) {{ cont.classList.add('hidden'); empty.classList.remove('hidden'); return; }}
  empty.classList.add('hidden'); cont.classList.remove('hidden');
  cont.innerHTML = '';
  state.recientes.forEach(entry => {{
    const div = document.createElement('div');
    div.className = 'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-50 cursor-pointer';
    div.onclick = () => abrirVisorPara(entry);
    const meta = getExtMeta(entry.name, false);
    div.innerHTML = `
      <i data-lucide="${{meta.icon}}" class="w-4 h-4 ${{meta.color}} shrink-0"></i>
      <span class="text-sm text-slate-700 font-medium truncate">${{entry.name}}</span>
    `;
    cont.appendChild(div);
  }});
  if (window.lucide) lucide.createIcons();
}}

function renderListaFavoritos() {{
  const cont = document.getElementById('lista-favoritos');
  const empty = document.getElementById('lbl-fav-empty');
  if (!cont || !empty) return;
  if (!state.favoritos.size) {{ cont.classList.add('hidden'); empty.classList.remove('hidden'); return; }}
  empty.classList.add('hidden'); cont.classList.remove('hidden');
  cont.innerHTML = '';
  state.favoritos.forEach(nombre => {{
    const div = document.createElement('div');
    div.className = 'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-amber-50';
    div.innerHTML = `
      <i data-lucide="star" class="w-4 h-4 text-amber-400 fill-amber-400 shrink-0"></i>
      <span class="text-sm text-slate-700 font-medium truncate">${{nombre}}</span>
    `;
    cont.appendChild(div);
  }});
  if (window.lucide) lucide.createIcons();
}}

// ─── Navegación de secciones ─────────────────────────────────────
const VISTAS = {{
  inicio    :'vista-inicio',
  explorador:'vista-explorador',
  favoritos :'vista-favoritos',
  recientes :'vista-recientes',
}};

function navActivar(sec) {{
  Object.values(VISTAS).forEach(id => document.getElementById(id)?.classList.add('hidden'));
  const target = VISTAS[sec] || VISTAS.inicio;
  document.getElementById(target)?.classList.remove('hidden');
  Object.keys(VISTAS).forEach(n => {{
    const el = document.getElementById('nav-' + n);
    if (!el) return;
    el.className = n === sec
      ? 'sidebar-active w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium'
      : 'w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-purple-900/50 hover:text-white';
  }});
  if (sec === 'explorador' && state.currentEntries.length) {{
    renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
    if (state.modoAPI) renderArbol();
  }}
  if (sec === 'favoritos') renderListaFavoritos();
  if (sec === 'recientes') renderListaRecientes();
  if (window.lucide) lucide.createIcons();
}}

function selUnidad(unidad) {{
  toast('Unidad seleccionada: ' + unidad);
}}

// ─── UI Helpers ───────────────────────────────────────────────────
function mostrarLoading(msg, sub) {{
  document.getElementById('loading-msg').textContent = msg || 'Cargando...';
  document.getElementById('loading-sub').textContent = sub || 'Por favor espera';
  document.getElementById('loading-overlay').classList.add('active');
}}

function ocultarLoading() {{
  document.getElementById('loading-overlay').classList.remove('active');
}}

function toast(msg, isError = false) {{
  const t = document.getElementById('toast');
  const m = document.getElementById('toast-msg');
  const ic = document.getElementById('toast-icon');
  m.textContent = msg;
  t.style.background = isError ? '#7F1D1D' : '#16002B';
  ic.setAttribute('data-lucide', isError ? 'alert-circle' : 'check-circle');
  ic.className = 'w-4 h-4 ' + (isError ? 'text-red-400' : 'text-emerald-400') + ' shrink-0';
  t.classList.add('show');
  if (window.lucide) lucide.createIcons();
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => t.classList.remove('show'), 3500);
}}

function maximizarVentana() {{
  if (!document.fullscreenElement)
    document.documentElement.requestFullscreen().catch(()=>{{}});
  else
    document.exitFullscreen().catch(()=>{{}});
}}

window.addEventListener('DOMContentLoaded', () => {{
  if (window.lucide) lucide.createIcons();
}});
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"index.html generado: {len(HTML):,} caracteres")
print("[OK] Visor integrado sin descargar (Word via Mammoth, Excel via SheetJS, PDF, fotos, video)")
print("[OK] Funcion de eliminar (individual y por lote)")
print("[OK] Funcion de editar / renombrar con modal")
