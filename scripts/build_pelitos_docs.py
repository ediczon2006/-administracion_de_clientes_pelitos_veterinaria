"""
build_pelitos_docs.py  –  v3 Universal Browser Edition
=======================================================
NUEVAS CORRECCIONES:
  + Soporte UNIVERSAL de navegadores:
      - Chrome / Edge:  showDirectoryPicker() (API moderna con árbol de carpetas)
      - Firefox / Safari / cualquier otro: <input type=file webkitdirectory> (selección plana)
  + Eliminar contadores falsos ("328 docs") de tarjetas de unidades y servicios.
    Las tarjetas solo muestran nombre e ícono; el contador aparece SOLO si se carga una carpeta real.
  + Eliminar todo aviso "Requiere Edge / Chrome" — ya no aplica.
  + El botón "Abrir Carpeta" siempre está activo en cualquier navegador.
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
      display:flex; align-items:center; gap:.5rem; max-width:22rem;
      transform:translateY(5rem); opacity:0;
      transition:transform .2s,opacity .2s;
    }}
    #toast.show {{ transform:translateY(0); opacity:1; }}

    /* Input file oculto para fallback universal */
    #input-folder {{ display:none; }}
  </style>
</head>

<body class="flex h-screen overflow-hidden">

<!-- Input oculto para navegadores sin showDirectoryPicker (Firefox, Safari) -->
<input type="file" id="input-folder" webkitdirectory multiple accept="*/*">

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
    <div class="relative flex-1 max-w-lg">
      <input id="buscador-top" oninput="aplicarFiltros()" type="text"
        placeholder="Buscar archivos por nombre, extensión..."
        class="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2
               placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition">
      <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
    </div>

    <select id="filtro-tipo-top" onchange="aplicarFiltros()"
      class="text-sm bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-600
             focus:outline-none focus:ring-2 focus:ring-purple-400 cursor-pointer">
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

    <!-- BOTÓN ABRIR — siempre activo en todos los navegadores -->
    <button onclick="abrirDirectorio()"
      class="flex items-center gap-2 bg-[#5B21B6] hover:bg-[#4C1D95]
             text-white text-sm font-bold px-4 py-2 rounded-lg shadow transition">
      <i data-lucide="folder-open" class="w-4 h-4"></i> Abrir Carpeta
    </button>

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
          <p class="text-white/70 text-xs mt-1">Documentos organizados para un crecimiento sostenible</p>
        </div>
        <div class="text-right text-white">
          <p class="text-base font-bold">Cuidamos vidas,</p>
          <p class="text-base font-bold">impulsamos sueños <span class="text-pink-300">❤️</span></p>
          <button onclick="abrirDirectorio()"
            class="mt-3 bg-amber-400 hover:bg-amber-300 text-amber-900 font-bold
                   text-sm px-5 py-2 rounded-lg shadow transition flex items-center gap-2 ml-auto">
            <i data-lucide="folder-open" class="w-4 h-4"></i> Explorar mis archivos
          </button>
        </div>
        <div class="absolute right-5 bottom-3 opacity-10 text-white text-8xl select-none pointer-events-none">🐾</div>
      </div>

      <!-- Unidades de Negocio — SIN contadores hardcodeados -->
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

      <!-- Servicios Compartidos — SIN contadores hardcodeados -->
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

      <!-- CTA Explorador — compatible con todos los navegadores -->
      <div onclick="abrirDirectorio()"
        class="bg-white rounded-2xl border-2 border-dashed border-purple-300 p-10
               flex flex-col items-center justify-center text-center shadow-inner cursor-pointer
               hover:border-purple-500 hover:bg-purple-50/50 transition">
        <div class="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-300/40 mb-4">
          <i data-lucide="folder-open" class="w-9 h-9 text-white"></i>
        </div>
        <h3 class="text-base font-bold text-slate-800 mb-1">Explorar archivos de tu computadora</h3>
        <p class="text-sm text-slate-500 max-w-sm leading-relaxed">
          Haz clic para seleccionar una carpeta. Compatible con<br>
          <strong>Chrome, Edge, Firefox, Safari</strong> y cualquier navegador moderno.
        </p>
        <p class="text-sm text-purple-500 mt-3 font-bold animate-pulse-slow">▶ Haz clic aquí para comenzar</p>
        <!-- Badge de soporte detectado dinámicamente por JS -->
        <p id="lbl-modo-api" class="text-xs text-slate-400 mt-2"></p>
      </div>

    </section>

    <!-- ══ VISTA EXPLORADOR ══ -->
    <section id="vista-explorador" class="hidden space-y-3">

      <!-- Breadcrumb -->
      <div id="breadcrumb-bar"
        class="flex items-center gap-1.5 text-sm text-slate-500 flex-wrap bg-white border border-slate-200
               rounded-xl px-4 py-2.5 shadow-sm overflow-x-auto">
        <i data-lucide="hard-drive" class="w-4 h-4 text-slate-400 shrink-0"></i>
        <span class="text-slate-400 font-medium">Selecciona una carpeta...</span>
      </div>

      <!-- Stats — solo se muestran si hay datos reales -->
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

        <!-- ÁRBOL (solo visible en modo FS API) -->
        <div id="panel-arbol" class="w-52 border-r border-slate-100 p-2 overflow-y-auto bg-slate-50/50 shrink-0">
          <p class="text-xs font-bold text-slate-400 uppercase tracking-wider px-1 mb-2">Árbol de directorios</p>
          <div id="arbol-dir" class="space-y-0.5">
            <p class="text-slate-400 px-2 py-6 text-center text-xs">Sin datos</p>
          </div>
          <p id="nota-arbol-flat" class="text-xs text-slate-400 text-center py-2 hidden">
            (Vista plana: sin árbol)
          </p>
        </div>

        <!-- TABLA -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Sub-header -->
          <div class="border-b border-slate-100 px-4 py-2 flex items-center gap-3 bg-white shrink-0">
            <span id="label-ruta-actual" class="text-xs text-slate-500 font-mono truncate flex-1 select-all">
              Seleccione una carpeta
            </span>
            <button onclick="subirNivel()" title="Subir un nivel" id="btn-subir"
              class="text-slate-400 hover:text-purple-600 transition p-1 rounded hover:bg-purple-50 hidden">
              <i data-lucide="arrow-up" class="w-4 h-4"></i>
            </button>
            <button onclick="actualizarDirectorio()" title="Actualizar"
              class="text-slate-400 hover:text-purple-600 transition p-1 rounded hover:bg-purple-50">
              <i data-lucide="refresh-cw" class="w-4 h-4"></i>
            </button>
            <button onclick="abrirDirectorio()" title="Cambiar carpeta"
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
                  <th class="py-2.5 px-3 font-semibold text-center">Acc.</th>
                </tr>
              </thead>
              <tbody id="tabla-body" class="divide-y divide-slate-50 text-sm">
                <tr><td colspan="6" class="text-center py-16 text-slate-400">
                  <i data-lucide="folder-open" class="w-10 h-10 mx-auto mb-3 opacity-30"></i>
                  <p class="text-sm font-medium">Aún no has abierto ninguna carpeta.</p>
                  <button onclick="abrirDirectorio()"
                    class="mt-3 text-purple-600 hover:underline text-sm font-semibold">
                    Haz clic aquí para comenzar →
                  </button>
                </td></tr>
              </tbody>
            </table>
          </div>

          <!-- Status bar -->
          <div class="border-t border-slate-100 px-4 py-1.5 flex items-center justify-between
                      text-xs text-slate-400 bg-slate-50 shrink-0">
            <span id="status-bar">0 elementos</span>
            <span id="status-sel">0 seleccionados</span>
          </div>
        </div>

        <!-- INSPECTOR -->
        <div class="w-56 border-l border-slate-100 flex flex-col shrink-0 overflow-y-auto bg-white">
          <div class="p-3 border-b border-slate-100">
            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Inspector</p>
          </div>
          <div id="inspector-body" class="p-3 flex-1 text-xs space-y-3">
            <div class="text-center text-slate-300 py-10">
              <i data-lucide="file-search" class="w-9 h-9 mx-auto mb-2"></i>
              <p class="text-sm">Selecciona un archivo</p>
            </div>
          </div>
          <div id="inspector-actions" class="p-2 border-t border-slate-100 space-y-1.5 hidden">
            <button onclick="abrirDocumento()"
              class="w-full bg-[#5B21B6] hover:bg-[#4C1D95] text-white text-xs font-bold
                     py-2 px-2 rounded-lg shadow transition flex items-center justify-center gap-1.5">
              <i data-lucide="eye" class="w-3.5 h-3.5"></i> Abrir
            </button>
            <div class="grid grid-cols-2 gap-1">
              <button onclick="copiarRutaInspector()"
                class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium
                       py-1.5 px-1 rounded-lg flex items-center justify-center gap-1">
                <i data-lucide="copy" class="w-3 h-3"></i> Ruta
              </button>
              <button onclick="toggleFavoritoInspector()" id="btn-fav-inspector"
                class="bg-slate-100 hover:bg-amber-50 text-slate-700 text-xs font-medium
                       py-1.5 px-1 rounded-lg flex items-center justify-center gap-1">
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
//  PELITOS DOCS — Explorador Universal (Chrome, Edge, Firefox, Safari)
//  Estrategia dual:
//    MODO A: showDirectoryPicker()  → Chrome/Edge (árbol completo)
//    MODO B: <input webkitdirectory> → Firefox/Safari/todos (lista plana)
// ════════════════════════════════════════════════════════════════════

const FS_API = 'showDirectoryPicker' in window;  // ¿Soporta FS Access API?

// ─── Estado global ─────────────────────────────────────────────────
const state = {{
  currentEntries : [],   // Entradas del directorio actual
  filtrados      : [],   // Subconjunto filtrado
  selObj         : null, // Objeto entry seleccionado
  selSet         : new Set(),
  navStack       : [],   // Solo modo A (FS API)
  currentHandle  : null, // Solo modo A
  dirHandle      : null, // Solo modo A
  favoritos      : new Set(),
  recientes      : [],
  vistaActual    : 'lista',
  loadVersion    : 0,
  toastTimer     : null,
  modoAPI        : false, // true = FS API, false = input fallback
}};

// ─── Utilidades ───────────────────────────────────────────────────
const EXT_META = {{
  pdf  :{{label:'PDF',        badge:'ext-pdf',   icon:'file-text',        color:'text-red-600'    }},
  doc  :{{label:'Word',       badge:'ext-doc',   icon:'file-text',        color:'text-blue-600'   }},
  docx :{{label:'Word',       badge:'ext-doc',   icon:'file-text',        color:'text-blue-600'   }},
  xls  :{{label:'Excel',      badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  xlsx :{{label:'Excel',      badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  xlsm :{{label:'Excel',      badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  csv  :{{label:'CSV',        badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-700'}},
  ppt  :{{label:'PowerPoint', badge:'ext-ppt',   icon:'presentation',     color:'text-orange-600' }},
  pptx :{{label:'PowerPoint', badge:'ext-ppt',   icon:'presentation',     color:'text-orange-600' }},
  jpg  :{{label:'Imagen JPG', badge:'ext-img',   icon:'image',            color:'text-pink-600'   }},
  jpeg :{{label:'Imagen JPG', badge:'ext-img',   icon:'image',            color:'text-pink-600'   }},
  png  :{{label:'Imagen PNG', badge:'ext-img',   icon:'image',            color:'text-pink-600'   }},
  gif  :{{label:'GIF',        badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  bmp  :{{label:'BMP',        badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  svg  :{{label:'SVG',        badge:'ext-img',   icon:'image',            color:'text-purple-600' }},
  webp :{{label:'WebP',       badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  tiff :{{label:'TIFF',       badge:'ext-img',   icon:'image',            color:'text-pink-500'   }},
  mp4  :{{label:'Video MP4',  badge:'ext-vid',   icon:'video',            color:'text-purple-600' }},
  mov  :{{label:'Video MOV',  badge:'ext-vid',   icon:'video',            color:'text-purple-600' }},
  avi  :{{label:'Video AVI',  badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  mkv  :{{label:'Video MKV',  badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  wmv  :{{label:'Video WMV',  badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  webm :{{label:'Video WebM', badge:'ext-vid',   icon:'video',            color:'text-purple-500' }},
  mp3  :{{label:'Audio MP3',  badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  wav  :{{label:'Audio WAV',  badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  flac :{{label:'Audio FLAC', badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  ogg  :{{label:'Audio OGG',  badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  m4a  :{{label:'Audio M4A',  badge:'ext-mp3',   icon:'music',            color:'text-violet-600' }},
  zip  :{{label:'ZIP',        badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  rar  :{{label:'RAR',        badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  '7z' :{{label:'7-Zip',      badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  tar  :{{label:'TAR',        badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  gz   :{{label:'GZIP',       badge:'ext-zip',   icon:'archive',          color:'text-orange-600' }},
  txt  :{{label:'Texto',      badge:'ext-txt',   icon:'file-text',        color:'text-slate-600'  }},
  md   :{{label:'Markdown',   badge:'ext-txt',   icon:'file-text',        color:'text-slate-600'  }},
  json :{{label:'JSON',       badge:'ext-js',    icon:'braces',           color:'text-yellow-700' }},
  xml  :{{label:'XML',        badge:'ext-txt',   icon:'file-code',        color:'text-slate-600'  }},
  html :{{label:'HTML',       badge:'ext-html',  icon:'file-code',        color:'text-rose-600'   }},
  htm  :{{label:'HTML',       badge:'ext-html',  icon:'file-code',        color:'text-rose-600'   }},
  css  :{{label:'CSS',        badge:'ext-html',  icon:'file-code',        color:'text-blue-500'   }},
  js   :{{label:'JavaScript', badge:'ext-js',    icon:'file-code',        color:'text-yellow-700' }},
  ts   :{{label:'TypeScript', badge:'ext-js',    icon:'file-code',        color:'text-blue-600'   }},
  py   :{{label:'Python',     badge:'ext-code',  icon:'file-code',        color:'text-green-700'  }},
  java :{{label:'Java',       badge:'ext-code',  icon:'file-code',        color:'text-red-700'    }},
  cpp  :{{label:'C++',        badge:'ext-code',  icon:'file-code',        color:'text-slate-700'  }},
  cs   :{{label:'C#',         badge:'ext-code',  icon:'file-code',        color:'text-purple-700' }},
  go   :{{label:'Go',         badge:'ext-code',  icon:'file-code',        color:'text-sky-700'    }},
  rb   :{{label:'Ruby',       badge:'ext-code',  icon:'file-code',        color:'text-red-600'    }},
  sql  :{{label:'SQL',        badge:'ext-code',  icon:'database',         color:'text-orange-700' }},
  sh   :{{label:'Script',     badge:'ext-code',  icon:'terminal',         color:'text-slate-700'  }},
  bat  :{{label:'Batch',      badge:'ext-code',  icon:'terminal',         color:'text-slate-700'  }},
  exe  :{{label:'Ejecutable', badge:'ext-default',icon:'cpu',             color:'text-slate-700'  }},
  dll  :{{label:'DLL',        badge:'ext-default',icon:'cpu',             color:'text-slate-700'  }},
  psd  :{{label:'Photoshop',  badge:'ext-img',   icon:'image',            color:'text-blue-700'   }},
  ai   :{{label:'Illustrator',badge:'ext-img',   icon:'image',            color:'text-orange-700' }},
  fig  :{{label:'Figma',      badge:'ext-img',   icon:'image',            color:'text-purple-700' }},
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

// ─── APERTURA DE CARPETA — MODO DUAL ──────────────────────────────
function abrirDirectorio() {{
  if (FS_API) {{
    abrirConFsApi();
  }} else {{
    // Fallback universal: dispara el input file
    document.getElementById('input-folder').click();
  }}
}}

// MODO A: File System Access API (Chrome / Edge)
async function abrirConFsApi() {{
  try {{
    const handle = await window.showDirectoryPicker({{mode:'read'}});
    state.dirHandle    = handle;
    state.currentHandle = handle;
    state.navStack     = [handle];
    state.modoAPI      = true;
    document.getElementById('panel-arbol').style.display = '';
    document.getElementById('nota-arbol-flat').classList.add('hidden');
    document.getElementById('btn-subir').classList.remove('hidden');
    await cargarEntradasAPI(handle);
    navActivar('explorador');
  }} catch(e) {{
    if (e.name !== 'AbortError') toast('Error al abrir carpeta: ' + e.message, true);
  }}
}}

// MODO B: input[type=file webkitdirectory] (Firefox / Safari / todos)
document.getElementById('input-folder').addEventListener('change', function(e) {{
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  state.modoAPI = false;
  document.getElementById('panel-arbol').style.display = 'none';
  document.getElementById('nota-arbol-flat').classList.remove('hidden');
  document.getElementById('btn-subir').classList.add('hidden');
  cargarEntradasPlanas(files);
  navActivar('explorador');
  // Resetear el input para poder volver a abrir la misma carpeta
  e.target.value = '';
}});

// ─── MODO A: cargar desde FS API ──────────────────────────────────
async function cargarEntradasAPI(dirHandle) {{
  const version = ++state.loadVersion;
  mostrarLoading('Leyendo archivos...', dirHandle.name);
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
        }} catch {{ /* sin permiso */ }}
      }}
      entries.push({{name, handle, kind: handle.kind, size, lastMod, fileObj: null}});
    }}
    if (version !== state.loadVersion) {{ ocultarLoading(); return; }}
    entries.sort((a,b) => {{
      if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
      return a.name.localeCompare(b.name, 'es', {{sensitivity:'base'}});
    }});
    aplicarNuevasEntradas(entries, totalSize, dirHandle.name);
  }} catch(e) {{
    toast('Error al leer el directorio: ' + e.message, true);
  }}
  ocultarLoading();
}}

// ─── MODO B: cargar desde FileList plano ──────────────────────────
function cargarEntradasPlanas(files) {{
  mostrarLoading('Procesando archivos...', files.length + ' archivos');
  try {{
    let totalSize = 0;
    const nombreCarpeta = files[0]?.webkitRelativePath?.split('/')[0] || 'Carpeta seleccionada';

    // Agrupar: archivos directos de la raíz + subcarpetas de primer nivel
    const entradasMap = new Map(); // nombre → entry

    files.forEach(f => {{
      const partes = f.webkitRelativePath.split('/');
      if (partes.length === 2) {{
        // Archivo directo en la raíz
        const nombre = partes[1];
        totalSize += f.size;
        entradasMap.set(nombre, {{
          name: nombre, kind:'file', size: f.size,
          lastMod: f.lastModified, handle: null, fileObj: f
        }});
      }} else if (partes.length >= 3) {{
        // Subcarpeta de primer nivel
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
    if (lbl) lbl.textContent = nombreCarpeta + '/ (vista plana)';
    aplicarNuevasEntradas(entries, totalSize, nombreCarpeta);
  }} catch(e) {{
    toast('Error al procesar archivos: ' + e.message, true);
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

// ─── Stats ─────────────────────────────────────────────────────────
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

// ─── Render Tabla ─────────────────────────────────────────────────
function renderTabla(entries) {{
  const tbody = document.getElementById('tabla-body');
  tbody.innerHTML = '';

  if (entries.length === 0) {{
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 6;
    td.className = 'text-center py-10 text-slate-400 text-sm';
    td.textContent = 'Carpeta vacía o sin resultados';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }}

  // Fila ".." solo en modo API con navegación profunda
  if (state.modoAPI && state.navStack.length > 1) {{
    const trUp = document.createElement('tr');
    trUp.className = 'cursor-pointer hover:bg-slate-50 transition';
    trUp.ondblclick = subirNivel;
    const tdChk = document.createElement('td');
    tdChk.className = 'py-2.5 px-3';
    trUp.appendChild(tdChk);
    const tdName = document.createElement('td');
    tdName.colSpan = 5;
    tdName.className = 'py-2.5 px-3';
    const w = document.createElement('div');
    w.className = 'flex items-center gap-2 text-slate-400 text-sm hover:text-purple-600';
    const ic = document.createElement('i');
    ic.setAttribute('data-lucide','corner-left-up');
    ic.className = 'w-4 h-4';
    const sp = document.createElement('span');
    sp.className = 'font-medium';
    sp.textContent = '.. (subir un nivel)';
    w.appendChild(ic); w.appendChild(sp);
    tdName.appendChild(w);
    trUp.appendChild(tdName);
    tbody.appendChild(trUp);
  }}

  entries.forEach(entry => {{
    const meta       = getExtMeta(entry.name, entry.kind === 'directory');
    const isSelected = state.selSet.has(entry);
    const tr = document.createElement('tr');
    tr.className = 'cursor-pointer transition hover:bg-slate-50 ' + (isSelected ? 'row-selected' : '');
    tr.onclick  = (e) => seleccionar(entry, e);
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

    // Nombre — textContent previene XSS
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

    // Acción
    const tdAcc = document.createElement('td');
    tdAcc.className = 'py-2.5 px-3 text-center';
    const btnAcc = document.createElement('button');
    btnAcc.className = 'text-slate-300 hover:text-purple-600 transition p-1 rounded';
    btnAcc.title = 'Seleccionar';
    btnAcc.onclick = (e) => {{ e.stopPropagation(); seleccionar(entry, null); }};
    const moreI = document.createElement('i');
    moreI.setAttribute('data-lucide','more-horizontal');
    moreI.className = 'w-4 h-4';
    btnAcc.appendChild(moreI);
    tdAcc.appendChild(btnAcc);
    tr.appendChild(tdAcc);

    tbody.appendChild(tr);
  }});

  if (window.lucide) lucide.createIcons();
}}

// ─── Árbol (solo modo API) ─────────────────────────────────────────
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

// ─── Abrir entrada ────────────────────────────────────────────────
async function abrirEntrada(entry) {{
  if (!entry) return;
  if (entry.kind === 'directory') {{
    if (state.modoAPI && entry.handle) {{
      state.navStack.push(entry.handle);
      state.currentHandle = entry.handle;
      await cargarEntradasAPI(entry.handle);
    }} else {{
      toast('Navegación interna no disponible en modo Firefox/Safari. Selecciona una subcarpeta desde el botón Abrir Carpeta.', false);
    }}
  }} else {{
    try {{
      let file;
      if (entry.fileObj) {{
        // Modo B: File object ya disponible
        file = entry.fileObj;
      }} else if (entry.handle) {{
        // Modo A: obtener desde FileSystemFileHandle
        file = await entry.handle.getFile();
      }} else {{
        toast('No se puede abrir este archivo', true);
        return;
      }}
      const url = URL.createObjectURL(file);
      window.open(url, '_blank');
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
      addReciente(entry);
      toast('Abriendo: ' + entry.name);
    }} catch(e) {{
      toast('No se pudo abrir: ' + e.message, true);
    }}
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
    toast('Directorio actualizado');
  }} else if (!state.modoAPI && state.currentEntries.length) {{
    toast('Vuelve a abrir la carpeta para actualizar.');
  }} else {{
    toast('No hay carpeta abierta.', true);
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
  document.getElementById('status-sel').textContent = state.selSet.size + ' seleccionados';
}}

function toggleSel(entry) {{
  if (state.selSet.has(entry)) state.selSet.delete(entry);
  else state.selSet.add(entry);
  document.getElementById('status-sel').textContent = state.selSet.size + ' seleccionados';
}}

function selTodos(chk) {{
  const lista = state.filtrados.length ? state.filtrados : state.currentEntries;
  if (chk.checked) lista.forEach(e => state.selSet.add(e));
  else state.selSet.clear();
  renderTabla(lista);
  document.getElementById('status-sel').textContent = state.selSet.size + ' seleccionados';
}}

// ─── Inspector ────────────────────────────────────────────────────
function actualizarInspector(entry) {{
  const body    = document.getElementById('inspector-body');
  const actions = document.getElementById('inspector-actions');
  if (!entry) {{
    body.innerHTML = '';
    const w = document.createElement('div');
    w.className = 'text-center text-slate-300 py-10';
    w.innerHTML = '<i data-lucide="file-search" class="w-9 h-9 mx-auto mb-2"></i>';
    const p = document.createElement('p');
    p.className = 'text-sm'; p.textContent = 'Selecciona un archivo';
    w.appendChild(p);
    body.appendChild(w);
    actions.classList.add('hidden');
    if (window.lucide) lucide.createIcons();
    return;
  }}
  const meta  = getExtMeta(entry.name, entry.kind === 'directory');
  const isFav = state.favoritos.has(entry.name);

  body.innerHTML = '';
  const topBox = document.createElement('div');
  topBox.className = 'flex flex-col items-center py-3 border-b border-slate-100';
  const iconW = document.createElement('div');
  iconW.className = 'w-14 h-14 rounded-xl flex items-center justify-center bg-slate-100 mb-2';
  const bIcon = document.createElement('i');
  bIcon.setAttribute('data-lucide', meta.icon);
  bIcon.className = 'w-8 h-8 ' + meta.color;
  iconW.appendChild(bIcon);
  const nameP = document.createElement('p');
  nameP.className = 'font-bold text-slate-800 text-center text-xs break-all leading-tight px-1';
  nameP.textContent = entry.name;
  const badgeSp = document.createElement('span');
  badgeSp.className = 'ext-badge ' + meta.badge + ' mt-1';
  badgeSp.textContent = meta.label;
  topBox.appendChild(iconW); topBox.appendChild(nameP); topBox.appendChild(badgeSp);
  body.appendChild(topBox);

  const metaDiv = document.createElement('div');
  metaDiv.className = 'space-y-1.5 text-xs pt-2';
  [
    ['Tipo',      meta.label],
    ['Tamaño',    entry.kind==='directory'?'—':formatSize(entry.size)],
    ['Modificado',formatDate(entry.lastMod)],
  ].forEach(([label, value]) => {{
    const row = document.createElement('div');
    row.className = 'flex justify-between gap-1';
    const lbl = document.createElement('span');
    lbl.className = 'text-slate-400'; lbl.textContent = label + ':';
    const val = document.createElement('span');
    val.className = 'font-semibold text-slate-700 text-right truncate max-w-[8rem]';
    val.textContent = value; val.title = value;
    row.appendChild(lbl); row.appendChild(val);
    metaDiv.appendChild(row);
  }});
  if (isFav) {{
    const favRow = document.createElement('div');
    favRow.className = 'flex items-center gap-1 text-amber-600 font-semibold mt-1 text-xs';
    favRow.innerHTML = '<i data-lucide="star" class="w-3 h-3 fill-amber-400"></i> En favoritos';
    metaDiv.appendChild(favRow);
  }}
  body.appendChild(metaDiv);

  actions.classList.remove('hidden');
  const btnFav = document.getElementById('btn-fav-inspector');
  btnFav.innerHTML =
    '<i data-lucide="star" class="w-3 h-3 ' + (isFav?'text-amber-400 fill-amber-400':'text-slate-400') + '"></i> ' +
    (isFav ? 'Quitar' : 'Fav.');
  if (window.lucide) lucide.createIcons();
}}

async function abrirDocumento() {{
  if (state.selObj) await abrirEntrada(state.selObj);
}}

function copiarRutaInspector() {{
  if (!state.selObj) return;
  const ruta = (state.currentHandle?.name || 'carpeta') + '\\\\' + state.selObj.name;
  navigator.clipboard.writeText(ruta)
    .then(() => toast('Ruta copiada'))
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
    toast('Favorito: ' + nombre);
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
        case 'pdf' : matchTipo = ext === 'pdf'; break;
        case 'doc' : matchTipo = ['doc','docx'].includes(ext); break;
        case 'xls' : matchTipo = ['xls','xlsx','xlsm','csv'].includes(ext); break;
        case 'ppt' : matchTipo = ['ppt','pptx'].includes(ext); break;
        case 'img' : matchTipo = m?.badge === 'ext-img'; break;
        case 'vid' : matchTipo = m?.badge === 'ext-vid'; break;
        case 'mp3' : matchTipo = m?.badge === 'ext-mp3'; break;
        case 'zip' : matchTipo = m?.badge === 'ext-zip'; break;
        case 'txt' : matchTipo = m?.badge === 'ext-txt'; break;
        case 'code': matchTipo = ['ext-code','ext-js','ext-html'].includes(m?.badge || ''); break;
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
    const iconBox = document.createElement('div');
    iconBox.className = 'w-11 h-11 flex items-center justify-center rounded-lg bg-slate-50 mb-1.5';
    const icon = document.createElement('i');
    icon.setAttribute('data-lucide', meta.icon);
    icon.className = 'w-7 h-7 ' + meta.color;
    iconBox.appendChild(icon);
    const nameP = document.createElement('p');
    nameP.className = 'text-xs text-slate-700 font-medium break-all leading-tight max-h-9 overflow-hidden';
    nameP.title = entry.name; nameP.textContent = entry.name;
    const badgeSp = document.createElement('span');
    badgeSp.className = 'ext-badge ' + meta.badge + ' mt-1';
    badgeSp.textContent = meta.label;
    div.appendChild(iconBox); div.appendChild(nameP); div.appendChild(badgeSp);
    if (entry.kind === 'file') {{
      const sizeP = document.createElement('p');
      sizeP.className = 'text-xs text-slate-400 mt-0.5';
      sizeP.textContent = formatSize(entry.size);
      div.appendChild(sizeP);
    }}
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
    // Modo B: mostrar solo el nombre de la carpeta seleccionada
    const span = document.createElement('span');
    span.className = 'text-sm text-purple-700 font-bold';
    span.textContent = nombreDir || 'Carpeta seleccionada';
    bar.appendChild(span);
    const note = document.createElement('span');
    note.className = 'text-xs text-slate-400 ml-2';
    note.textContent = '(vista raíz — modo compatible)';
    bar.appendChild(note);
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
    div.onclick = () => abrirEntrada(entry);
    const meta = getExtMeta(entry.name, false);
    const icon = document.createElement('i');
    icon.setAttribute('data-lucide', meta.icon);
    icon.className = 'w-4 h-4 ' + meta.color + ' shrink-0';
    const sp = document.createElement('span');
    sp.className = 'text-sm text-slate-700 font-medium truncate';
    sp.textContent = entry.name;
    div.appendChild(icon); div.appendChild(sp);
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
    const icon = document.createElement('i');
    icon.setAttribute('data-lucide','star');
    icon.className = 'w-4 h-4 text-amber-400 fill-amber-400 shrink-0';
    const sp = document.createElement('span');
    sp.className = 'text-sm text-slate-700 font-medium truncate';
    sp.textContent = nombre;
    div.appendChild(icon); div.appendChild(sp);
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
  toast('Cargando: ' + unidad);
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

// ─── Init ─────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {{
  if (window.lucide) lucide.createIcons();
  // Informar al usuario qué modo está disponible
  const lbl = document.getElementById('lbl-modo-api');
  if (lbl) {{
    lbl.textContent = FS_API
      ? '✅ Modo avanzado disponible (Chrome/Edge) — árbol de carpetas completo'
      : '✅ Modo compatible activo — funciona en Firefox, Safari y cualquier navegador';
  }}
}});
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"index.html generado: {len(HTML):,} caracteres")
print("[OK] Compatible con: Chrome, Edge, Firefox, Safari")
print("[OK] Sin contadores de documentos falsos")
print("[OK] Modo A (FS API): arbol + navegacion jerarquica")
print("[OK] Modo B (input fallback): lista plana universal")
