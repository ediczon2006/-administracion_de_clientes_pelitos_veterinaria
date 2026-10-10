"""
build_pelitos_docs.py
=====================
Genera index.html con el logo oficial de Pelitos Veterinaria incrustado en base64,
explorador de archivos real de Windows via File System Access API,
y sin ningún dato demo.
"""
import base64
import os

# --- Leer el logo oficial ---
with open("assets/logo_pelitos.png", "rb") as f:
    b64_logo = base64.b64encode(f.read()).decode("utf-8")
logo_data = f"data:image/png;base64,{b64_logo}"

# --- Leer banner de mascotas (si existe) ---
banner_data = ""
if os.path.exists("assets/banner_pets.png"):
    with open("assets/banner_pets.png", "rb") as f:
        b64_banner = base64.b64encode(f.read()).decode("utf-8")
    banner_data = f"data:image/png;base64,{b64_banner}"

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pelitos Docs - Gestión Documental Pelitos Veterinaria</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin:0; padding:0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:#F1F5F9; color:#1E293B; height:100vh; overflow:hidden;
    }}
    ::-webkit-scrollbar {{ width:5px; height:5px; }}
    ::-webkit-scrollbar-track {{ background:#F1F5F9; }}
    ::-webkit-scrollbar-thumb {{ background:#CBD5E1; border-radius:4px; }}
    .sidebar-active {{ background:#5B21B6!important; color:#fff!important; font-weight:600; }}
    .tree-active {{ background:#FDE68A!important; color:#78350F!important; border-radius:6px; font-weight:600; }}
    .row-selected {{ background:#EDE9FE!important; }}
    .row-selected td {{ color:#5B21B6; }}
    .drop-zone-active {{ background:#EDE9FE; border-color:#7C3AED!important; }}
    .animate-pulse-slow {{ animation: pulse 2s cubic-bezier(0.4,0,0.6,1) infinite; }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.6}} }}
    .ext-badge {{
      display:inline-block; padding:1px 5px; border-radius:4px;
      font-size:9px; font-weight:700; letter-spacing:.5px; text-transform:uppercase;
    }}
    .ext-pdf  {{ background:#FEE2E2; color:#B91C1C; }}
    .ext-doc  {{ background:#DBEAFE; color:#1D4ED8; }}
    .ext-xls  {{ background:#D1FAE5; color:#065F46; }}
    .ext-ppt  {{ background:#FEF3C7; color:#92400E; }}
    .ext-img  {{ background:#FCE7F3; color:#9D174D; }}
    .ext-vid  {{ background:#EDE9FE; color:#5B21B6; }}
    .ext-mp3  {{ background:#FDF4FF; color:#7E22CE; }}
    .ext-zip  {{ background:#FFF7ED; color:#C2410C; }}
    .ext-txt  {{ background:#F0FDF4; color:#166534; }}
    .ext-py   {{ background:#FAFAFA; color:#15803D; }}
    .ext-js   {{ background:#FEF9C3; color:#854D0E; }}
    .ext-html {{ background:#FFF1F2; color:#BE123C; }}
    .ext-default {{ background:#F1F5F9; color:#475569; }}
    .folder-badge {{ background:#FEF3C7; color:#92400E; }}
  </style>
</head>

<body class="flex h-screen overflow-hidden">

<!-- ============== SIDEBAR ============== -->
<aside class="w-56 bg-[#16002B] text-slate-200 flex flex-col shrink-0 overflow-y-auto select-none">

  <!-- Logo oficial -->
  <div class="p-3 border-b border-purple-900/60 flex items-center gap-2 bg-white/5">
    <img src="{logo_data}" alt="Pelitos Veterinaria" class="h-8 object-contain" style="max-width:136px;">
  </div>
  <div class="px-3 py-1.5 border-b border-purple-900/40 bg-[#1E0040]/60">
    <p class="text-[10px] text-purple-300 font-semibold tracking-widest">PELITOS DOCS</p>
    <p class="text-[9px] text-slate-400">Gestión Documental Empresarial</p>
  </div>

  <!-- Nav principal -->
  <div class="px-2 pt-3 space-y-0.5">
    <button id="nav-inicio" onclick="navActivar('inicio')"
      class="sidebar-active w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px]">
      <i data-lucide="home" class="w-3.5 h-3.5"></i> Inicio
    </button>
    <button id="nav-explorador" onclick="navActivar('explorador')"
      class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px] text-slate-300 hover:bg-purple-900/50 hover:text-white">
      <i data-lucide="folder-open" class="w-3.5 h-3.5 text-amber-400"></i> Explorador de Archivos
    </button>
    <button id="nav-buscar" onclick="navActivar('buscar')"
      class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px] text-slate-300 hover:bg-purple-900/50 hover:text-white">
      <i data-lucide="search" class="w-3.5 h-3.5"></i> Buscar
    </button>
    <button id="nav-favoritos" onclick="navActivar('favoritos')"
      class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px] text-slate-300 hover:bg-purple-900/50 hover:text-white">
      <i data-lucide="star" class="w-3.5 h-3.5 text-amber-400"></i> Favoritos
    </button>
    <button id="nav-recientes" onclick="navActivar('recientes')"
      class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px] text-slate-300 hover:bg-purple-900/50 hover:text-white">
      <i data-lucide="clock" class="w-3.5 h-3.5"></i> Recientes
    </button>
  </div>

  <!-- Sección Unidades de Negocio -->
  <div class="px-3 pt-4 pb-1">
    <p class="text-[9px] font-bold text-purple-400 uppercase tracking-widest mb-1.5">Unidades de Negocio</p>
    <div class="space-y-0.5 text-[10px]">
      <button onclick="selUnidad('Consultorio Veterinario')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="stethoscope" class="w-3 h-3 text-blue-400 shrink-0"></i><span class="truncate">Consultorio Veterinario</span>
      </button>
      <button onclick="selUnidad('Estética Canina')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-white bg-purple-900/30 text-left">
        <i data-lucide="scissors" class="w-3 h-3 text-pink-400 shrink-0"></i><span class="truncate">Estética Canina</span>
      </button>
      <button onclick="selUnidad('Laboratorio Veterinario')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="flask-conical" class="w-3 h-3 text-emerald-400 shrink-0"></i><span class="truncate">Laboratorio Veterinario</span>
      </button>
      <button onclick="selUnidad('Farmacia Veterinaria')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="pill" class="w-3 h-3 text-orange-400 shrink-0"></i><span class="truncate">Farmacia Veterinaria</span>
      </button>
      <button onclick="selUnidad('Pet Shop')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="shopping-cart" class="w-3 h-3 text-amber-400 shrink-0"></i><span class="truncate">Pet Shop</span>
      </button>
      <button onclick="selUnidad('Pelitos Móvil')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="truck" class="w-3 h-3 text-sky-400 shrink-0"></i><span class="truncate">Pelitos Móvil</span>
      </button>
      <button onclick="selUnidad('Hospedaje de Mascotas')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="house" class="w-3 h-3 text-purple-400 shrink-0"></i><span class="truncate">Hospedaje de Mascotas</span>
      </button>
    </div>
  </div>

  <!-- Sección Servicios Compartidos -->
  <div class="px-3 pt-3 pb-4">
    <p class="text-[9px] font-bold text-purple-400 uppercase tracking-widest mb-1.5">Servicios Compartidos</p>
    <div class="space-y-0.5 text-[10px]">
      <button onclick="selUnidad('Recepción y Clientes')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="headset" class="w-3 h-3 text-blue-400 shrink-0"></i><span class="truncate">Recepción y Clientes</span>
      </button>
      <button onclick="selUnidad('Recursos Humanos')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="users" class="w-3 h-3 text-sky-400 shrink-0"></i><span class="truncate">Recursos Humanos</span>
      </button>
      <button onclick="selUnidad('Marketing Corporativo')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="megaphone" class="w-3 h-3 text-purple-400 shrink-0"></i><span class="truncate">Marketing Corporativo</span>
      </button>
      <button onclick="selUnidad('Compras y Logística')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="package" class="w-3 h-3 text-amber-500 shrink-0"></i><span class="truncate">Compras y Logística</span>
      </button>
      <button onclick="selUnidad('Tecnología y Software')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="laptop" class="w-3 h-3 text-blue-400 shrink-0"></i><span class="truncate">Tecnología y Software</span>
      </button>
      <button onclick="selUnidad('Calidad y Auditoría')" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-slate-300 hover:bg-purple-900/40 hover:text-white text-left">
        <i data-lucide="shield-check" class="w-3 h-3 text-emerald-400 shrink-0"></i><span class="truncate">Calidad y Auditoría</span>
      </button>
    </div>
  </div>

</aside>

<!-- ============== ÁREA PRINCIPAL ============== -->
<main class="flex-1 flex flex-col overflow-hidden">

  <!-- TOPBAR -->
  <header class="h-12 bg-white border-b border-slate-200 px-4 flex items-center gap-3 shrink-0 shadow-sm z-20">
    <!-- Búsqueda -->
    <div class="relative flex-1 max-w-lg">
      <input id="buscador-top" oninput="buscarEnTabla(this.value)" type="text"
        placeholder="Buscar archivos por nombre, tipo, extensión..."
        class="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-8 pr-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-purple-500">
      <i data-lucide="search" class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2"></i>
    </div>
    <!-- Filtros -->
    <select id="filtro-tipo-top" onchange="aplicarFiltros()" class="text-xs bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-400 cursor-pointer">
      <option value="">Todos los tipos</option>
      <option value="folder">Carpetas</option>
      <option value="pdf">PDF</option>
      <option value="doc">Word (doc/docx)</option>
      <option value="xls">Excel (xls/xlsx)</option>
      <option value="ppt">PowerPoint</option>
      <option value="img">Imágenes</option>
      <option value="vid">Videos</option>
      <option value="mp3">Audio</option>
      <option value="zip">Comprimidos</option>
      <option value="txt">Texto</option>
      <option value="code">Código</option>
    </select>
    <!-- Botón Abrir Carpeta (FS Access API) -->
    <button onclick="abrirDirectorio()" title="Abrir carpeta de Windows"
      class="flex items-center gap-1.5 bg-[#5B21B6] hover:bg-[#4C1D95] text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow transition">
      <i data-lucide="folder-open" class="w-3.5 h-3.5"></i> Abrir Carpeta
    </button>
    <!-- Ordenar -->
    <select id="ordenar-por" onchange="aplicarFiltros()" class="text-xs bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-400 cursor-pointer">
      <option value="nombre">↑ Nombre</option>
      <option value="tipo">↑ Tipo</option>
      <option value="tamano">↓ Tamaño</option>
      <option value="fecha">↓ Fecha</option>
    </select>
    <!-- Vista -->
    <div class="flex items-center gap-1 border border-slate-200 rounded-lg overflow-hidden">
      <button id="btn-vista-lista" onclick="cambiarVista('lista')" title="Vista lista"
        class="px-2 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 transition">
        <i data-lucide="list" class="w-3.5 h-3.5"></i>
      </button>
      <button id="btn-vista-grid" onclick="cambiarVista('grid')" title="Vista cuadrícula"
        class="px-2 py-1.5 text-slate-500 hover:bg-slate-50 transition">
        <i data-lucide="layout-grid" class="w-3.5 h-3.5"></i>
      </button>
    </div>
    <button onclick="maximizarVentana()" title="Pantalla completa" class="text-slate-400 hover:text-slate-700 transition">
      <i data-lucide="maximize-2" class="w-4 h-4"></i>
    </button>
  </header>

  <!-- CONTENIDO CON SCROLL -->
  <div class="flex-1 overflow-y-auto p-4 space-y-4">

    <!-- ===== VISTA INICIO ===== -->
    <section id="vista-inicio" class="space-y-4">

      <!-- Hero Banner con Logo -->
      <div class="relative rounded-2xl overflow-hidden bg-gradient-to-r from-purple-900 via-purple-800 to-indigo-900 p-5 shadow-lg flex items-center justify-between">
        <div>
          <img src="{logo_data}" alt="Pelitos Veterinaria" class="h-14 object-contain mb-2" style="filter:brightness(0) invert(1);">
          <p class="text-purple-200 text-xs font-medium">Tu biblioteca empresarial veterinaria</p>
          <p class="text-white/70 text-[10px] mt-0.5">Documentos organizados para un crecimiento sostenible</p>
        </div>
        <div class="text-right text-white hidden md:block">
          <p class="text-sm font-bold">Cuidamos vidas,</p>
          <p class="text-sm font-bold">impulsamos sueños <span class="text-pink-300">❤️</span></p>
          <button onclick="abrirDirectorio()" class="mt-3 bg-amber-400 hover:bg-amber-300 text-amber-900 font-bold text-xs px-4 py-2 rounded-lg shadow transition flex items-center gap-2 ml-auto">
            <i data-lucide="folder-open" class="w-4 h-4"></i> Explorar mis archivos
          </button>
        </div>
        <!-- Decorativo: huella -->
        <div class="absolute right-4 bottom-4 opacity-10 text-white text-7xl select-none">🐾</div>
      </div>

      <!-- Unidades de Negocio -->
      <div>
        <h3 class="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">Unidades de Negocio</h3>
        <div class="grid grid-cols-4 lg:grid-cols-7 gap-2">
          <div onclick="selUnidad('Consultorio Veterinario')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-blue-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="stethoscope" class="w-3.5 h-3.5 text-blue-600"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Consultorio Veterinario</span></div>
            <p class="text-[9px] text-slate-400 font-medium text-right">328 docs</p>
          </div>
          <div onclick="selUnidad('Estética Canina')" class="cursor-pointer bg-pink-50 p-2.5 rounded-xl border-2 border-pink-400 shadow-sm hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="scissors" class="w-3.5 h-3.5 text-pink-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Estética Canina</span></div>
            <p class="text-[9px] text-pink-600 font-bold text-right">214 docs</p>
          </div>
          <div onclick="selUnidad('Laboratorio Veterinario')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-emerald-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="flask-conical" class="w-3.5 h-3.5 text-emerald-600"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Laboratorio Veterinario</span></div>
            <p class="text-[9px] text-slate-400 font-medium text-right">156 docs</p>
          </div>
          <div onclick="selUnidad('Farmacia Veterinaria')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-orange-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="pill" class="w-3.5 h-3.5 text-orange-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Farmacia Veterinaria</span></div>
            <p class="text-[9px] text-slate-400 font-medium text-right">142 docs</p>
          </div>
          <div onclick="selUnidad('Pet Shop')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-amber-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="shopping-cart" class="w-3.5 h-3.5 text-amber-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Pet Shop</span></div>
            <p class="text-[9px] text-slate-400 font-medium text-right">118 docs</p>
          </div>
          <div onclick="selUnidad('Pelitos Móvil')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-sky-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="truck" class="w-3.5 h-3.5 text-sky-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Pelitos Móvil</span></div>
            <p class="text-[9px] text-slate-400 font-medium text-right">87 docs</p>
          </div>
          <div onclick="selUnidad('Hospedaje de Mascotas')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-purple-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="house" class="w-3.5 h-3.5 text-purple-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Hospedaje de Mascotas</span></div>
            <p class="text-[9px] text-slate-400 font-medium text-right">64 docs</p>
          </div>
        </div>
      </div>

      <!-- Servicios Compartidos -->
      <div>
        <h3 class="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">Servicios Compartidos</h3>
        <div class="grid grid-cols-3 lg:grid-cols-6 gap-2">
          <div onclick="selUnidad('Recepción y Clientes')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-blue-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="headset" class="w-3.5 h-3.5 text-blue-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Recepción y Clientes</span></div>
            <p class="text-[9px] text-slate-400 text-right">96 docs</p>
          </div>
          <div onclick="selUnidad('Recursos Humanos')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-sky-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="users" class="w-3.5 h-3.5 text-sky-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Recursos Humanos</span></div>
            <p class="text-[9px] text-slate-400 text-right">73 docs</p>
          </div>
          <div onclick="selUnidad('Marketing Corporativo')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-purple-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="megaphone" class="w-3.5 h-3.5 text-purple-600"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Marketing Corporativo</span></div>
            <p class="text-[9px] text-slate-400 text-right">142 docs</p>
          </div>
          <div onclick="selUnidad('Compras y Logística')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-amber-500 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="package" class="w-3.5 h-3.5 text-amber-600"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Compras y Logística</span></div>
            <p class="text-[9px] text-slate-400 text-right">61 docs</p>
          </div>
          <div onclick="selUnidad('Tecnología y Software')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-blue-500 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="laptop" class="w-3.5 h-3.5 text-blue-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Tecnología y Software</span></div>
            <p class="text-[9px] text-slate-400 text-right">52 docs</p>
          </div>
          <div onclick="selUnidad('Calidad y Auditoría')" class="cursor-pointer bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm hover:border-emerald-400 hover:shadow transition flex flex-col gap-1">
            <div class="flex items-center gap-1.5"><i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-500"></i><span class="text-[10px] font-bold text-slate-800 leading-tight">Calidad y Auditoría</span></div>
            <p class="text-[9px] text-slate-400 text-right">38 docs</p>
          </div>
        </div>
      </div>

      <!-- Panel Explorar Archivos Windows CTA -->
      <div id="panel-cta-explorador" class="bg-white rounded-2xl border-2 border-dashed border-purple-300 p-8 flex flex-col items-center justify-center text-center shadow-inner cursor-pointer hover:border-purple-500 hover:bg-purple-50/50 transition" onclick="abrirDirectorio()">
        <div class="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-300/50 mb-3">
          <i data-lucide="folder-open" class="w-8 h-8 text-white"></i>
        </div>
        <h3 class="text-sm font-bold text-slate-800 mb-1">Explorar archivos de Windows</h3>
        <p class="text-xs text-slate-500 max-w-sm">Haz clic para seleccionar una carpeta de tu computadora.<br>Soporta <strong>PDF, Word, Excel, PowerPoint, Imágenes, Videos, Audio, ZIP, Texto, Código</strong> y cualquier otro tipo de archivo.</p>
        <p class="text-[10px] text-purple-500 mt-2 font-semibold animate-pulse-slow">▶ Haz clic aquí o en "Abrir Carpeta" en la barra superior</p>
      </div>

    </section>

    <!-- ===== VISTA EXPLORADOR (se rellena con FS Access API) ===== -->
    <section id="vista-explorador" class="hidden space-y-3">

      <!-- Breadcrumb -->
      <div id="breadcrumb-bar" class="flex items-center gap-1 text-xs text-slate-500 flex-wrap bg-white border border-slate-200 rounded-xl px-3 py-2 shadow-sm">
        <i data-lucide="hard-drive" class="w-3.5 h-3.5 text-slate-400 shrink-0"></i>
        <span class="text-slate-400 font-medium">Cargando...</span>
      </div>

      <!-- Stats rápidos -->
      <div class="grid grid-cols-4 gap-2">
        <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-total" class="text-lg font-black text-purple-700">0</p>
          <p class="text-[10px] text-slate-500">Total archivos</p>
        </div>
        <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-carpetas" class="text-lg font-black text-amber-600">0</p>
          <p class="text-[10px] text-slate-500">Carpetas</p>
        </div>
        <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-tamano" class="text-lg font-black text-emerald-700">0</p>
          <p class="text-[10px] text-slate-500">Tamaño total</p>
        </div>
        <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-sm text-center">
          <p id="stat-tipos" class="text-lg font-black text-blue-600">0</p>
          <p class="text-[10px] text-slate-500">Tipos distintos</p>
        </div>
      </div>

      <!-- Panel 3 columnas -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex min-h-[460px]" style="max-height:calc(100vh - 330px)">

        <!-- ÁRBOL DE DIRECTORIOS -->
        <div class="w-52 border-r border-slate-100 p-2 overflow-y-auto bg-slate-50/50 shrink-0">
          <p class="text-[9px] font-bold text-slate-400 uppercase tracking-wider px-1 mb-1.5">Árbol de directorios</p>
          <div id="arbol-dir" class="text-[11px] space-y-0.5">
            <p class="text-slate-400 px-2 py-4 text-center text-[10px]">Sin datos</p>
          </div>
        </div>

        <!-- TABLA DE ARCHIVOS -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Sub-header de tabla -->
          <div class="border-b border-slate-100 px-3 py-2 flex items-center gap-3 bg-white shrink-0">
            <span id="label-ruta-actual" class="text-[10px] text-slate-500 font-mono truncate flex-1">Seleccione una carpeta</span>
            <button onclick="subirNivel()" title="Subir un nivel" class="text-slate-400 hover:text-purple-600 transition">
              <i data-lucide="arrow-up" class="w-3.5 h-3.5"></i>
            </button>
            <button onclick="actualizarDirectorio()" title="Actualizar" class="text-slate-400 hover:text-purple-600 transition">
              <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i>
            </button>
            <button onclick="abrirDirectorio()" title="Cambiar carpeta" class="text-slate-400 hover:text-purple-600 transition">
              <i data-lucide="folder-open" class="w-3.5 h-3.5"></i>
            </button>
          </div>
          <div class="overflow-auto flex-1">
            <table class="w-full text-left border-collapse" id="tabla-arch">
              <thead class="bg-slate-50 border-b border-slate-100 sticky top-0 z-10 text-[10px] text-slate-500">
                <tr>
                  <th class="py-2 px-2 w-6"><input type="checkbox" id="chk-all" onclick="selTodos(this)" class="rounded text-purple-600 focus:ring-0 w-3 h-3"></th>
                  <th class="py-2 px-2 font-semibold cursor-pointer hover:text-slate-800 select-none" onclick="ordenarPor('nombre')">Nombre ↕</th>
                  <th class="py-2 px-2 font-semibold">Tipo</th>
                  <th class="py-2 px-2 font-semibold cursor-pointer hover:text-slate-800 select-none" onclick="ordenarPor('fecha')">Modificado ↕</th>
                  <th class="py-2 px-2 font-semibold cursor-pointer hover:text-slate-800 select-none text-right" onclick="ordenarPor('tamano')">Tamaño ↕</th>
                  <th class="py-2 px-2 font-semibold text-center">Acciones</th>
                </tr>
              </thead>
              <tbody id="tabla-body" class="divide-y divide-slate-50 text-[11px]">
                <tr><td colspan="6" class="text-center py-12 text-slate-400">
                  <i data-lucide="folder-open" class="w-8 h-8 mx-auto mb-2 opacity-40"></i>
                  <p class="text-xs">Aún no has abierto ninguna carpeta.</p>
                  <button onclick="abrirDirectorio()" class="mt-2 text-purple-600 hover:underline text-xs font-semibold">Haz clic aquí para comenzar →</button>
                </td></tr>
              </tbody>
            </table>
          </div>
          <!-- Status bar -->
          <div class="border-t border-slate-100 px-3 py-1.5 flex items-center justify-between text-[10px] text-slate-400 bg-slate-50 shrink-0">
            <span id="status-bar">0 elementos</span>
            <span id="status-sel">0 seleccionados</span>
          </div>
        </div>

        <!-- INSPECTOR DE DETALLE -->
        <div class="w-52 border-l border-slate-100 flex flex-col shrink-0 overflow-y-auto bg-white" id="inspector-panel">
          <div class="p-3 border-b border-slate-100">
            <p class="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Inspector</p>
          </div>
          <div id="inspector-body" class="p-3 flex-1 text-[10px] space-y-3">
            <div class="text-center text-slate-300 py-8">
              <i data-lucide="file-search" class="w-8 h-8 mx-auto mb-2"></i>
              <p>Selecciona un archivo</p>
            </div>
          </div>
          <div id="inspector-actions" class="p-2 border-t border-slate-100 space-y-1.5 hidden">
            <button id="btn-abrir-doc" onclick="abrirDocumento()" class="w-full bg-[#5B21B6] hover:bg-[#4C1D95] text-white text-[10px] font-bold py-1.5 px-2 rounded-lg shadow transition flex items-center justify-center gap-1">
              <i data-lucide="eye" class="w-3 h-3"></i> Abrir
            </button>
            <div class="grid grid-cols-2 gap-1">
              <button onclick="copiarRutaInspector()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-[9px] font-medium py-1 px-1 rounded-lg flex items-center justify-center gap-1">
                <i data-lucide="copy" class="w-2.5 h-2.5"></i> Copiar ruta
              </button>
              <button onclick="toggleFavoritoInspector()" id="btn-fav-inspector" class="bg-slate-100 hover:bg-amber-50 text-slate-700 text-[9px] font-medium py-1 px-1 rounded-lg flex items-center justify-center gap-1">
                <i data-lucide="star" class="w-2.5 h-2.5 text-amber-500"></i> Favorito
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- Vista Grid (oculta por defecto) -->
      <div id="vista-grid" class="hidden">
        <div id="grid-archivos" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2"></div>
      </div>

    </section>

  </div><!-- /content scroll -->

</main>

<!-- ===== TOAST ===== -->
<div id="toast" class="fixed bottom-5 right-5 bg-[#16002B] text-white text-xs px-4 py-2.5 rounded-xl shadow-2xl z-50 transform translate-y-16 opacity-0 transition-all duration-200 flex items-center gap-2 max-w-xs">
  <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400 shrink-0"></i>
  <span id="toast-msg">OK</span>
</div>

<!-- ===== LOADING OVERLAY ===== -->
<div id="loading-overlay" class="fixed inset-0 bg-purple-950/60 backdrop-blur-sm z-50 hidden flex items-center justify-center">
  <div class="bg-white rounded-2xl p-6 flex flex-col items-center gap-3 shadow-2xl">
    <div class="w-10 h-10 border-4 border-purple-200 border-t-purple-700 rounded-full animate-spin"></div>
    <p id="loading-msg" class="text-sm font-semibold text-slate-700">Leyendo archivos...</p>
    <p id="loading-sub" class="text-xs text-slate-400">Por favor espera</p>
  </div>
</div>

<script>
// ============================================================
//  PELITOS DOCS - Explorador de Archivos Windows
//  File System Access API + vista lista / grid + inspector
// ============================================================

// Estado global
const state = {{
  dirHandle: null,       // DirectoryHandle raíz
  currentHandle: null,   // DirectoryHandle actual
  currentEntries: [],    // Entradas del directorio actual
  filtrados: [],         // Entradas filtradas para mostrar
  seleccionado: null,    // Entrada seleccionada
  seleccionados: new Set(), // Multi-selección
  navStack: [],          // Stack de navegación (historial)
  favoritos: new Set(),
  recientes: [],
  vistaActual: 'lista',  // 'lista' | 'grid'
  columnaOrden: 'nombre',
  ordenAsc: true,
  navActiva: 'inicio',
}};

// Mapa de extensiones → metadata
const EXT_META = {{
  // Documentos Microsoft Office
  pdf:   {{ label:'PDF',        badge:'ext-pdf',   icon:'file-text',    color:'text-red-600'     }},
  doc:   {{ label:'Word',       badge:'ext-doc',   icon:'file-text',    color:'text-blue-600'    }},
  docx:  {{ label:'Word',       badge:'ext-doc',   icon:'file-text',    color:'text-blue-600'    }},
  xls:   {{ label:'Excel',      badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  xlsx:  {{ label:'Excel',      badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  xlsm:  {{ label:'Excel',      badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-600'}},
  csv:   {{ label:'CSV',        badge:'ext-xls',   icon:'file-spreadsheet', color:'text-emerald-700'}},
  ppt:   {{ label:'PowerPoint', badge:'ext-ppt',   icon:'presentation', color:'text-orange-600'  }},
  pptx:  {{ label:'PowerPoint', badge:'ext-ppt',   icon:'presentation', color:'text-orange-600'  }},
  // Imágenes
  jpg:   {{ label:'Imagen JPG', badge:'ext-img',   icon:'image',        color:'text-pink-600'    }},
  jpeg:  {{ label:'Imagen JPG', badge:'ext-img',   icon:'image',        color:'text-pink-600'    }},
  png:   {{ label:'Imagen PNG', badge:'ext-img',   icon:'image',        color:'text-pink-600'    }},
  gif:   {{ label:'GIF',        badge:'ext-img',   icon:'image',        color:'text-pink-500'    }},
  bmp:   {{ label:'Imagen BMP', badge:'ext-img',   icon:'image',        color:'text-pink-500'    }},
  svg:   {{ label:'SVG',        badge:'ext-img',   icon:'image',        color:'text-purple-600'  }},
  webp:  {{ label:'WebP',       badge:'ext-img',   icon:'image',        color:'text-pink-500'    }},
  tiff:  {{ label:'TIFF',       badge:'ext-img',   icon:'image',        color:'text-pink-500'    }},
  // Videos
  mp4:   {{ label:'Video MP4',  badge:'ext-vid',   icon:'video',        color:'text-purple-600'  }},
  mov:   {{ label:'Video MOV',  badge:'ext-vid',   icon:'video',        color:'text-purple-600'  }},
  avi:   {{ label:'Video AVI',  badge:'ext-vid',   icon:'video',        color:'text-purple-500'  }},
  mkv:   {{ label:'Video MKV',  badge:'ext-vid',   icon:'video',        color:'text-purple-500'  }},
  wmv:   {{ label:'Video WMV',  badge:'ext-vid',   icon:'video',        color:'text-purple-500'  }},
  webm:  {{ label:'Video WebM', badge:'ext-vid',   icon:'video',        color:'text-purple-500'  }},
  // Audio
  mp3:   {{ label:'Audio MP3',  badge:'ext-mp3',   icon:'music',        color:'text-violet-600'  }},
  wav:   {{ label:'Audio WAV',  badge:'ext-mp3',   icon:'music',        color:'text-violet-600'  }},
  flac:  {{ label:'Audio FLAC', badge:'ext-mp3',   icon:'music',        color:'text-violet-600'  }},
  ogg:   {{ label:'Audio OGG',  badge:'ext-mp3',   icon:'music',        color:'text-violet-600'  }},
  m4a:   {{ label:'Audio M4A',  badge:'ext-mp3',   icon:'music',        color:'text-violet-600'  }},
  // Comprimidos
  zip:   {{ label:'ZIP',        badge:'ext-zip',   icon:'archive',      color:'text-orange-600'  }},
  rar:   {{ label:'RAR',        badge:'ext-zip',   icon:'archive',      color:'text-orange-600'  }},
  '7z':  {{ label:'7-Zip',      badge:'ext-zip',   icon:'archive',      color:'text-orange-600'  }},
  tar:   {{ label:'TAR',        badge:'ext-zip',   icon:'archive',      color:'text-orange-600'  }},
  gz:    {{ label:'GZIP',       badge:'ext-zip',   icon:'archive',      color:'text-orange-600'  }},
  // Texto y código
  txt:   {{ label:'Texto',      badge:'ext-txt',   icon:'file-text',    color:'text-slate-600'   }},
  md:    {{ label:'Markdown',   badge:'ext-txt',   icon:'file-text',    color:'text-slate-600'   }},
  json:  {{ label:'JSON',       badge:'ext-js',    icon:'braces',       color:'text-yellow-700'  }},
  xml:   {{ label:'XML',        badge:'ext-txt',   icon:'file-code',    color:'text-slate-600'   }},
  html:  {{ label:'HTML',       badge:'ext-html',  icon:'file-code',    color:'text-rose-600'    }},
  htm:   {{ label:'HTML',       badge:'ext-html',  icon:'file-code',    color:'text-rose-600'    }},
  css:   {{ label:'CSS',        badge:'ext-html',  icon:'file-code',    color:'text-blue-500'    }},
  js:    {{ label:'JavaScript', badge:'ext-js',    icon:'file-code',    color:'text-yellow-700'  }},
  ts:    {{ label:'TypeScript', badge:'ext-js',    icon:'file-code',    color:'text-blue-600'    }},
  py:    {{ label:'Python',     badge:'ext-py',    icon:'file-code',    color:'text-green-700'   }},
  java:  {{ label:'Java',       badge:'ext-py',    icon:'file-code',    color:'text-red-700'     }},
  cpp:   {{ label:'C++',        badge:'ext-py',    icon:'file-code',    color:'text-slate-700'   }},
  cs:    {{ label:'C#',         badge:'ext-py',    icon:'file-code',    color:'text-purple-700'  }},
  go:    {{ label:'Go',         badge:'ext-py',    icon:'file-code',    color:'text-sky-700'     }},
  rb:    {{ label:'Ruby',       badge:'ext-py',    icon:'file-code',    color:'text-red-600'     }},
  sql:   {{ label:'SQL',        badge:'ext-py',    icon:'database',     color:'text-orange-700'  }},
  sh:    {{ label:'Script',     badge:'ext-py',    icon:'terminal',     color:'text-slate-700'   }},
  bat:   {{ label:'Batch',      badge:'ext-py',    icon:'terminal',     color:'text-slate-700'   }},
  exe:   {{ label:'Ejecutable', badge:'ext-default',icon:'cpu',         color:'text-slate-700'   }},
  dll:   {{ label:'DLL',        badge:'ext-default',icon:'cpu',         color:'text-slate-700'   }},
  // Diseño
  psd:   {{ label:'Photoshop',  badge:'ext-img',   icon:'image',        color:'text-blue-700'    }},
  ai:    {{ label:'Illustrator',badge:'ext-img',   icon:'image',        color:'text-orange-700'  }},
  fig:   {{ label:'Figma',      badge:'ext-img',   icon:'image',        color:'text-purple-700'  }},
}};

function getExtMeta(nombre, esDir) {{
  if (esDir) return {{ label:'Carpeta', badge:'folder-badge', icon:'folder', color:'text-amber-500' }};
  const ext = nombre.split('.').pop().toLowerCase();
  return EXT_META[ext] || {{ label: ext.toUpperCase() || 'Archivo', badge:'ext-default', icon:'file', color:'text-slate-500' }};
}}

function formatSize(bytes) {{
  if (bytes == null) return '-';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB';
  if (bytes < 1024*1024*1024) return (bytes/1024/1024).toFixed(1) + ' MB';
  return (bytes/1024/1024/1024).toFixed(2) + ' GB';
}}

function formatDate(ts) {{
  if (!ts) return '-';
  const d = new Date(ts);
  return d.toLocaleDateString('es-PE', {{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}});
}}

// ---- Explorador FS Access API ----
async function abrirDirectorio() {{
  if (!('showDirectoryPicker' in window)) {{
    toast('Tu navegador no soporta File System Access API. Usa Edge o Chrome.', true);
    return;
  }}
  try {{
    const dirHandle = await window.showDirectoryPicker({{ mode:'read' }});
    state.dirHandle = dirHandle;
    state.currentHandle = dirHandle;
    state.navStack = [dirHandle];
    await cargarEntradas(dirHandle);
    navActivar('explorador');
  }} catch(e) {{
    if (e.name !== 'AbortError') toast('Error al abrir carpeta: ' + e.message, true);
  }}
}}

async function cargarEntradas(dirHandle) {{
  mostrarLoading('Leyendo archivos...');
  try {{
    const entries = [];
    let totalSize = 0;
    for await (const [name, handle] of dirHandle.entries()) {{
      let size = null, lastMod = null;
      if (handle.kind === 'file') {{
        try {{
          const file = await handle.getFile();
          size = file.size;
          lastMod = file.lastModified;
          totalSize += size;
        }} catch(e) {{}}
      }}
      entries.push({{ name, handle, kind: handle.kind, size, lastMod }});
    }}
    // Carpetas primero, luego archivos, ambos ordenados A-Z
    entries.sort((a,b) => {{
      if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
      return a.name.localeCompare(b.name, 'es', {{sensitivity:'base'}});
    }});
    state.currentEntries = entries;
    state.seleccionado = null;
    state.seleccionados = new Set();
    renderTabla(entries);
    renderArbol(dirHandle);
    actualizarStats(entries, totalSize);
    actualizarBreadcrumb();
    actualizarInspector(null);
    document.getElementById('label-ruta-actual').innerText = dirHandle.name + '/';
  }} catch(e) {{
    toast('Error: ' + e.message, true);
  }}
  ocultarLoading();
}}

function actualizarStats(entries, totalSize) {{
  const carpetas = entries.filter(e => e.kind === 'directory').length;
  const archivos = entries.filter(e => e.kind === 'file').length;
  const tipos = new Set(entries.filter(e => e.kind==='file').map(e => e.name.split('.').pop().toLowerCase())).size;
  document.getElementById('stat-total').innerText = archivos;
  document.getElementById('stat-carpetas').innerText = carpetas;
  document.getElementById('stat-tamano').innerText = formatSize(totalSize);
  document.getElementById('stat-tipos').innerText = tipos;
  document.getElementById('status-bar').innerText = entries.length + ' elementos (' + archivos + ' archivos, ' + carpetas + ' carpetas)';
}}

function renderTabla(entries) {{
  const tbody = document.getElementById('tabla-body');
  tbody.innerHTML = '';
  if (entries.length === 0) {{
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-10 text-slate-400 text-xs">Carpeta vacía</td></tr>`;
    return;
  }}

  // Añadir ".." para subir nivel si no estamos en raíz
  if (state.navStack.length > 1) {{
    const trUp = document.createElement('tr');
    trUp.className = 'cursor-pointer hover:bg-slate-50 transition';
    trUp.ondblclick = subirNivel;
    trUp.innerHTML = `
      <td class="py-2 px-2"></td>
      <td class="py-2 px-2" colspan="5">
        <div class="flex items-center gap-2 text-slate-400 text-[11px] hover:text-purple-600">
          <i data-lucide="corner-left-up" class="w-3.5 h-3.5"></i>
          <span class="font-medium">.. (subir un nivel)</span>
        </div>
      </td>`;
    tbody.appendChild(trUp);
  }}

  entries.forEach((entry, idx) => {{
    const meta = getExtMeta(entry.name, entry.kind === 'directory');
    const isSelected = state.seleccionados.has(idx);
    const tr = document.createElement('tr');
    tr.className = `cursor-pointer transition hover:bg-slate-50 ${{isSelected ? 'row-selected' : ''}}`;
    tr.onclick = (e) => seleccionar(idx, e);
    tr.ondblclick = () => abrirEntrada(idx);

    tr.innerHTML = `
      <td class="py-2 px-2">
        <input type="checkbox" ${{isSelected ? 'checked' : ''}} class="rounded text-purple-600 focus:ring-0 w-3 h-3"
          onclick="event.stopPropagation(); toggleSel(${{idx}})">
      </td>
      <td class="py-2 px-2">
        <div class="flex items-center gap-2">
          <i data-lucide="${{meta.icon}}" class="w-4 h-4 ${{meta.color}} shrink-0"></i>
          <span class="font-medium text-slate-800 truncate max-w-xs" title="${{entry.name}}">${{entry.name}}</span>
          ${{state.favoritos.has(entry.name) ? '<i data-lucide="star" class="w-3 h-3 text-amber-400 shrink-0 fill-amber-400"></i>' : ''}}
        </div>
      </td>
      <td class="py-2 px-2">
        <span class="ext-badge ${{meta.badge}}">${{meta.label}}</span>
      </td>
      <td class="py-2 px-2 text-slate-400">${{formatDate(entry.lastMod)}}</td>
      <td class="py-2 px-2 text-slate-400 font-mono text-right">${{entry.kind === 'directory' ? '<span class="text-amber-600 font-medium">Carpeta</span>' : formatSize(entry.size)}}</td>
      <td class="py-2 px-2 text-center">
        <button onclick="event.stopPropagation(); accionRapida(${{idx}})" class="text-slate-300 hover:text-purple-600 transition" title="Acciones">
          <i data-lucide="more-horizontal" class="w-3.5 h-3.5"></i>
        </button>
      </td>`;
    tbody.appendChild(tr);
  }});

  if (window.lucide) lucide.createIcons();
}}

function renderArbol(dirHandle) {{
  const arbol = document.getElementById('arbol-dir');
  // Solo mostramos la ruta de navegación (stack)
  arbol.innerHTML = '';
  state.navStack.forEach((h, idx) => {{
    const div = document.createElement('div');
    div.className = `flex items-center gap-1.5 py-1 px-1.5 rounded cursor-pointer hover:bg-slate-200/60 ${{idx === state.navStack.length-1 ? 'tree-active' : 'text-slate-600'}}`;
    div.style.paddingLeft = (8 + idx*10) + 'px';
    div.innerHTML = `<i data-lucide="${{idx===0?'hard-drive':'folder'}}" class="w-3 h-3 ${{idx===state.navStack.length-1?'text-amber-600':'text-amber-500'}} shrink-0"></i>
      <span class="truncate text-[10px]">${{h.name}}</span>`;
    div.onclick = () => navArbol(idx);
    arbol.appendChild(div);
  }});
  if (window.lucide) lucide.createIcons();
}}

async function navArbol(idx) {{
  if (idx === state.navStack.length-1) return;
  state.navStack = state.navStack.slice(0, idx+1);
  state.currentHandle = state.navStack[idx];
  await cargarEntradas(state.currentHandle);
}}

async function abrirEntrada(idx) {{
  const entry = state.currentEntries[idx];
  if (!entry) return;
  if (entry.kind === 'directory') {{
    state.navStack.push(entry.handle);
    state.currentHandle = entry.handle;
    await cargarEntradas(entry.handle);
  }} else {{
    // Intento de abrir el archivo
    try {{
      const file = await entry.handle.getFile();
      const url = URL.createObjectURL(file);
      window.open(url, '_blank');
      addReciente(entry);
      toast('Abriendo: ' + entry.name);
    }} catch(e) {{
      toast('No se pudo abrir el archivo: ' + e.message, true);
    }}
  }}
}}

async function subirNivel() {{
  if (state.navStack.length <= 1) return;
  state.navStack.pop();
  state.currentHandle = state.navStack[state.navStack.length - 1];
  await cargarEntradas(state.currentHandle);
}}

async function actualizarDirectorio() {{
  if (!state.currentHandle) return;
  await cargarEntradas(state.currentHandle);
  toast('Directorio actualizado');
}}

function seleccionar(idx, event) {{
  if (event && event.ctrlKey) {{
    if (state.seleccionados.has(idx)) state.seleccionados.delete(idx);
    else state.seleccionados.add(idx);
  }} else {{
    state.seleccionados = new Set([idx]);
  }}
  state.seleccionado = idx;
  actualizarInspector(state.currentEntries[idx]);
  renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
  document.getElementById('status-sel').innerText = state.seleccionados.size + ' seleccionados';
}}

function toggleSel(idx) {{
  if (state.seleccionados.has(idx)) state.seleccionados.delete(idx);
  else state.seleccionados.add(idx);
  document.getElementById('status-sel').innerText = state.seleccionados.size + ' seleccionados';
}}

function selTodos(chk) {{
  const entries = state.filtrados.length ? state.filtrados : state.currentEntries;
  if (chk.checked) {{
    entries.forEach((_, i) => state.seleccionados.add(i));
  }} else {{
    state.seleccionados.clear();
  }}
  renderTabla(entries);
  document.getElementById('status-sel').innerText = state.seleccionados.size + ' seleccionados';
}}

function actualizarInspector(entry) {{
  const body = document.getElementById('inspector-body');
  const actions = document.getElementById('inspector-actions');
  if (!entry) {{
    body.innerHTML = `<div class="text-center text-slate-300 py-8"><i data-lucide="file-search" class="w-8 h-8 mx-auto mb-2"></i><p>Selecciona un archivo o carpeta</p></div>`;
    actions.classList.add('hidden');
    if (window.lucide) lucide.createIcons();
    return;
  }}
  const meta = getExtMeta(entry.name, entry.kind === 'directory');
  const isFav = state.favoritos.has(entry.name);

  body.innerHTML = `
    <!-- Ícono grande -->
    <div class="flex flex-col items-center py-3 border-b border-slate-100">
      <div class="w-14 h-14 rounded-xl flex items-center justify-center bg-slate-100 mb-2">
        <i data-lucide="${{meta.icon}}" class="w-8 h-8 ${{meta.color}}"></i>
      </div>
      <p class="font-bold text-slate-800 text-center text-[11px] break-all leading-tight">${{entry.name}}</p>
      <span class="ext-badge ${{meta.badge}} mt-1">${{meta.label}}</span>
    </div>
    <!-- Metadatos -->
    <div class="space-y-1.5 text-[10px]">
      <div class="flex justify-between gap-1">
        <span class="text-slate-400">Tipo:</span>
        <span class="font-semibold text-slate-700">${{meta.label}}</span>
      </div>
      <div class="flex justify-between gap-1">
        <span class="text-slate-400">Tamaño:</span>
        <span class="font-semibold text-slate-700">${{entry.kind==='directory'?'—':formatSize(entry.size)}}</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-slate-400">Modificado:</span>
        <span class="font-medium text-slate-600">${{formatDate(entry.lastMod)}}</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-slate-400">Directorio actual:</span>
        <span class="font-mono text-[9px] text-slate-600 bg-slate-100 px-1 py-0.5 rounded truncate">${{state.currentHandle?.name || ''}}</span>
      </div>
      ${{isFav ? '<div class="flex items-center gap-1 text-amber-600 font-semibold"><i data-lucide=\\"star\\" class=\\"w-3 h-3 fill-amber-400\\"></i> En favoritos</div>' : ''}}
    </div>`;

  actions.classList.remove('hidden');
  document.getElementById('btn-fav-inspector').innerHTML = `
    <i data-lucide="star" class="w-2.5 h-2.5 ${{isFav ? 'text-amber-400 fill-amber-400' : 'text-slate-400'}}"></i>
    ${{isFav ? 'Quitar' : 'Favorito'}}`;

  if (window.lucide) lucide.createIcons();
}}

async function abrirDocumento() {{
  if (state.seleccionado == null) return;
  await abrirEntrada(state.seleccionado);
}}

function copiarRutaInspector() {{
  const handle = state.currentHandle;
  const entry = state.currentEntries[state.seleccionado];
  const ruta = (handle?.name || '') + '\\\\' + (entry?.name || '');
  navigator.clipboard.writeText(ruta).then(() => toast('Ruta copiada: ' + ruta));
}}

function toggleFavoritoInspector() {{
  if (state.seleccionado == null) return;
  const entry = state.currentEntries[state.seleccionado];
  if (!entry) return;
  if (state.favoritos.has(entry.name)) {{
    state.favoritos.delete(entry.name);
    toast('Removido de favoritos');
  }} else {{
    state.favoritos.add(entry.name);
    toast('Agregado a favoritos: ' + entry.name);
  }}
  actualizarInspector(entry);
  renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
}}

function accionRapida(idx) {{
  seleccionar(idx, null);
  toast('Seleccionado: ' + state.currentEntries[idx]?.name);
}}

// ---- Filtros y búsqueda ----
function buscarEnTabla(q) {{
  aplicarFiltros();
}}

function aplicarFiltros() {{
  const q = document.getElementById('buscador-top').value.toLowerCase().trim();
  const tipo = document.getElementById('filtro-tipo-top').value;
  const orden = document.getElementById('ordenar-por').value;

  let resultado = state.currentEntries.filter(entry => {{
    const matchQ = !q || entry.name.toLowerCase().includes(q);
    let matchTipo = true;
    if (tipo === 'folder') matchTipo = entry.kind === 'directory';
    else if (tipo && entry.kind === 'file') {{
      const ext = entry.name.split('.').pop().toLowerCase();
      const m = EXT_META[ext];
      if (tipo === 'pdf') matchTipo = ext === 'pdf';
      else if (tipo === 'doc') matchTipo = ['doc','docx'].includes(ext);
      else if (tipo === 'xls') matchTipo = ['xls','xlsx','xlsm','csv'].includes(ext);
      else if (tipo === 'ppt') matchTipo = ['ppt','pptx'].includes(ext);
      else if (tipo === 'img') matchTipo = m?.badge === 'ext-img';
      else if (tipo === 'vid') matchTipo = m?.badge === 'ext-vid';
      else if (tipo === 'mp3') matchTipo = m?.badge === 'ext-mp3';
      else if (tipo === 'zip') matchTipo = m?.badge === 'ext-zip';
      else if (tipo === 'txt') matchTipo = m?.badge === 'ext-txt';
      else if (tipo === 'code') matchTipo = ['ext-py','ext-js','ext-html'].includes(m?.badge);
    }}
    return matchQ && matchTipo;
  }});

  // Ordenar
  resultado.sort((a,b) => {{
    if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
    let va, vb;
    if (orden === 'nombre') {{ va = a.name.toLowerCase(); vb = b.name.toLowerCase(); }}
    else if (orden === 'tipo') {{ va = a.name.split('.').pop(); vb = b.name.split('.').pop(); }}
    else if (orden === 'tamano') {{ va = a.size || 0; vb = b.size || 0; }}
    else if (orden === 'fecha') {{ va = a.lastMod || 0; vb = b.lastMod || 0; }}
    if (va < vb) return -1;
    if (va > vb) return 1;
    return 0;
  }});

  state.filtrados = resultado;
  renderTabla(resultado);
  if (state.vistaActual === 'grid') renderGrid(resultado);
  document.getElementById('status-bar').innerText = resultado.length + ' de ' + state.currentEntries.length + ' elementos';
}}

function ordenarPor(col) {{
  document.getElementById('ordenar-por').value = col === 'nombre' ? 'nombre' : col;
  aplicarFiltros();
}}

// ---- Vista Grid ----
function cambiarVista(tipo) {{
  state.vistaActual = tipo;
  const tablaContainer = document.querySelector('#tabla-arch').closest('.overflow-auto');
  const gridContainer = document.getElementById('vista-grid');

  if (tipo === 'lista') {{
    tablaContainer.classList.remove('hidden');
    gridContainer.classList.add('hidden');
    document.getElementById('btn-vista-lista').className = 'px-2 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 transition';
    document.getElementById('btn-vista-grid').className = 'px-2 py-1.5 text-slate-500 hover:bg-slate-50 transition';
    renderTabla(state.filtrados.length ? state.filtrados : state.currentEntries);
  }} else {{
    tablaContainer.classList.add('hidden');
    gridContainer.classList.remove('hidden');
    document.getElementById('btn-vista-lista').className = 'px-2 py-1.5 text-slate-500 hover:bg-slate-50 transition';
    document.getElementById('btn-vista-grid').className = 'px-2 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 transition';
    renderGrid(state.filtrados.length ? state.filtrados : state.currentEntries);
  }}
}}

function renderGrid(entries) {{
  const grid = document.getElementById('grid-archivos');
  grid.innerHTML = '';
  entries.forEach((entry, idx) => {{
    const meta = getExtMeta(entry.name, entry.kind==='directory');
    const div = document.createElement('div');
    div.className = 'cursor-pointer bg-white border border-slate-200 rounded-xl p-2 flex flex-col items-center text-center hover:border-purple-400 hover:shadow transition select-none';
    div.ondblclick = () => abrirEntrada(idx);
    div.onclick = () => seleccionar(idx, null);
    div.innerHTML = `
      <div class="w-10 h-10 flex items-center justify-center rounded-lg bg-slate-50 mb-1">
        <i data-lucide="${{meta.icon}}" class="w-6 h-6 ${{meta.color}}"></i>
      </div>
      <p class="text-[9px] text-slate-700 font-medium break-all leading-tight max-h-8 overflow-hidden" title="${{entry.name}}">${{entry.name}}</p>
      <span class="ext-badge ${{meta.badge}} mt-1">${{meta.label}}</span>
      ${{entry.kind==='file' ? '<p class="text-[8px] text-slate-400 mt-0.5">'+formatSize(entry.size)+'</p>' : ''}}`;
    grid.appendChild(div);
  }});
  if (window.lucide) lucide.createIcons();
}}

// ---- Breadcrumb ----
function actualizarBreadcrumb() {{
  const bar = document.getElementById('breadcrumb-bar');
  bar.innerHTML = '';
  state.navStack.forEach((h, idx) => {{
    if (idx > 0) {{
      const sep = document.createElement('i');
      sep.setAttribute('data-lucide', 'chevron-right');
      sep.className = 'w-3 h-3 text-slate-300';
      bar.appendChild(sep);
    }}
    const span = document.createElement('span');
    const isCurrent = idx === state.navStack.length - 1;
    span.className = `cursor-pointer ${{isCurrent ? 'text-purple-700 font-bold' : 'text-slate-500 hover:text-purple-600 hover:underline'}}`;
    span.textContent = h.name;
    span.onclick = () => navArbol(idx);
    bar.appendChild(span);
  }});
  if (window.lucide) lucide.createIcons();
}}

// ---- Recientes ----
function addReciente(entry) {{
  state.recientes = [entry, ...state.recientes.filter(r => r.name !== entry.name)].slice(0, 20);
}}

// ---- Navegación de secciones ----
function navActivar(sec) {{
  state.navActiva = sec;
  const vistas = {{ inicio:'vista-inicio', explorador:'vista-explorador' }};
  Object.values(vistas).forEach(id => document.getElementById(id)?.classList.add('hidden'));
  const target = vistas[sec] || 'vista-inicio';
  document.getElementById(target)?.classList.remove('hidden');

  // Actualizar sidebar
  ['inicio','explorador','buscar','favoritos','recientes'].forEach(n => {{
    const el = document.getElementById('nav-' + n);
    if (!el) return;
    el.className = n === sec
      ? 'sidebar-active w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px]'
      : 'w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px] text-slate-300 hover:bg-purple-900/50 hover:text-white';
  }});

  if (sec === 'explorador' && state.dirHandle) {{
    renderTabla(state.currentEntries);
    renderArbol(state.currentHandle);
    actualizarBreadcrumb();
  }}
  if (window.lucide) lucide.createIcons();
}}

function selUnidad(unidad) {{
  toast('Cargando documentos de: ' + unidad);
}}

// ---- UI Helpers ----
function mostrarLoading(msg, sub) {{
  document.getElementById('loading-msg').innerText = msg || 'Cargando...';
  document.getElementById('loading-sub').innerText = sub || 'Por favor espera';
  document.getElementById('loading-overlay').classList.remove('hidden');
  document.getElementById('loading-overlay').classList.add('flex');
}}

function ocultarLoading() {{
  document.getElementById('loading-overlay').classList.add('hidden');
  document.getElementById('loading-overlay').classList.remove('flex');
}}

function toast(msg, isError) {{
  const t = document.getElementById('toast');
  const m = document.getElementById('toast-msg');
  m.innerText = msg;
  t.style.background = isError ? '#7F1D1D' : '#16002B';
  t.classList.remove('translate-y-16','opacity-0');
  t.classList.add('translate-y-0','opacity-100');
  setTimeout(() => {{
    t.classList.remove('translate-y-0','opacity-100');
    t.classList.add('translate-y-16','opacity-0');
  }}, 3000);
}}

function maximizarVentana() {{
  if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(()=>{{}});
  else document.exitFullscreen().catch(()=>{{}});
}}

// ---- Inicializar ----
window.addEventListener('DOMContentLoaded', () => {{
  if (window.lucide) lucide.createIcons();
  // Verificar si el navegador soporta File System Access API
  if (!('showDirectoryPicker' in window)) {{
    const btn = document.querySelector('[onclick="abrirDirectorio()"]');
    if (btn) btn.title = 'Requiere Edge o Chrome';
  }}
}});
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"index.html generado: {len(HTML):,} chars")
