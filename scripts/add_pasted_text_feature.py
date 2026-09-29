import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
index_path = BASE_DIR / "index.html"

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Agregar el cuadro de texto en la pestaña Importador
ui_markup = """
        <!-- Pegar texto CSV / Reportes directamente -->
        <div class="bg-white p-5 rounded-xl border border-slate-200 space-y-3 shadow-sm">
          <div class="flex items-center gap-2">
            <i data-lucide="clipboard-paste" class="w-5 h-5 text-teal-600"></i>
            <h4 class="font-bold text-sm text-slate-800">📋 Pegar Texto CSV / Reporte de VetPraxis Directamente</h4>
          </div>
          <p class="text-xs text-slate-500">
            Copie y pegue aquí directamente cualquier tabla o texto de VetPraxis (Clientes, Mascotas, Atenciones Clínicas o Ventas). La página detectará automáticamente las columnas y las integrará al instante:
          </p>
          <textarea id="textarea-pegar-csv" rows="6" placeholder="Pegue aquí el texto copiado de VetPraxis (ej: FECHA DE REGISTRO,NOMBRES Y APELLIDOS,DOCUMENTO...)" class="w-full text-xs font-mono border border-slate-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-teal-500"></textarea>
          <div class="flex justify-between items-center">
            <span class="text-xs text-slate-400">Reconoce clientes, mascotas, atenciones y facturación sin necesidad de guardar archivo.</span>
            <button onclick="procesarTextoPegadoDirecto()" class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-4 py-2 rounded-lg text-xs shadow transition flex items-center gap-1.5">
              <i data-lucide="zap" class="w-4 h-4"></i> Procesar y Leer Texto Pegado
            </button>
          </div>
        </div>
"""

# Insertar antes de '<!-- Guía de Formatos -->'
if "<!-- Guía de Formatos -->" in content:
    content = content.replace("<!-- Guía de Formatos -->", ui_markup + "\n        <!-- Guía de Formatos -->")

# 2. Agregar la función JS para parsear texto pegado
js_function = """
    // Función para parsear texto CSV con soporte de comillas
    function parseCSVLine(line) {
      const result = [];
      let start = 0;
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const c = line[i];
        if (c === '"') {
          inQuotes = !inQuotes;
        } else if (c === ',' && !inQuotes) {
          let field = line.substring(start, i).trim();
          if (field.startsWith('"') && field.endsWith('"')) {
            field = field.substring(1, field.length - 1).replace(/""/g, '"');
          }
          result.push(field);
          start = i + 1;
        }
      }
      let lastField = line.substring(start).trim();
      if (lastField.startsWith('"') && lastField.endsWith('"')) {
        lastField = lastField.substring(1, lastField.length - 1).replace(/""/g, '"');
      }
      result.push(lastField);
      return result;
    }

    function procesarTextoPegadoDirecto() {
      const rawText = document.getElementById('textarea-pegar-csv').value;
      if (!rawText || !rawText.trim()) {
        alert("Por favor pegue el texto de su reporte en el cuadro antes de procesar.");
        return;
      }

      const lines = rawText.split(/\\r?\\n/).filter(l => l.trim().length > 0);
      let currentSection = null;
      let currentHeaders = [];
      let countCli = 0, countMas = 0, countAtn = 0, countVnt = 0;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Detección de encabezados
        if (line.includes("NOMBRES Y APELLIDOS") && line.includes("DOCUMENTO")) {
          currentSection = "clientes";
          currentHeaders = parseCSVLine(line).map(h => h.toUpperCase().trim());
          continue;
        } else if (line.includes("N° HISTORIA CLÍNICA") || line.includes("Nº HISTORIA CLÍNICA") || (line.includes("NOMBRE") && line.includes("ESPECIE") && line.includes("PROPIETARIO"))) {
          currentSection = "mascotas";
          currentHeaders = parseCSVLine(line).map(h => h.toUpperCase().trim());
          continue;
        } else if (line.includes("FECHA DE ATENCIÓN") || line.includes("TIPO DE ATENCIÓN")) {
          currentSection = "atenciones";
          currentHeaders = parseCSVLine(line).map(h => h.toUpperCase().trim());
          continue;
        } else if (line.includes("FECHA DE EMISIÓN") || line.includes("BOLETA") || line.includes("FACTURA")) {
          currentSection = "ventas";
          currentHeaders = parseCSVLine(line).map(h => h.toUpperCase().trim());
          continue;
        } else if (line.includes("REPORTE DE HISTORIAS") || line.includes("PELITOS VETERINARIA")) {
          continue; // Línea de metadata
        }

        if (!currentSection || !currentHeaders.length) continue;

        const row = parseCSVLine(line);
        if (row.length < 2) continue;

        const obj = {};
        currentHeaders.forEach((h, idx) => {
          obj[h] = row[idx] || '';
        });

        if (currentSection === "clientes") {
          let nom = obj["NOMBRES Y APELLIDOS"] || obj["NOMBRE"] || obj["CLIENTE"] || '';
          if (nom.includes(',')) {
            const p = nom.split(',');
            nom = `${p[1] || ''} ${p[0] || ''}`.trim();
          }
          const doc = (obj["DOCUMENTO"] || obj["DNI"] || '').trim();
          const cel = (obj["TELÉFONOS"] || obj["CELULAR"] || '').replace(/\\D/g, '').substring(0, 9);
          const dir = (obj["DIRECCIÓN"] || '').replace(/\\|/g, '').trim();

          if (nom || doc) {
            DB.clientes.push({ id: DB.clientes.length + 1, documento: doc, nombre: nom, celular: cel, direccion: dir });
            countCli++;
          }
        } else if (currentSection === "mascotas") {
          const hc = (obj["N° HISTORIA CLÍNICA"] || obj["Nº HISTORIA CLÍNICA"] || obj["HC"] || '').trim();
          const nom = (obj["NOMBRE"] || obj["MASCOTA"] || '').trim();
          const esp = (obj["ESPECIE"] || '').trim();
          const raz = (obj["RAZA"] || '').trim();
          const sex = (obj["SEXO"] || '').trim();
          let prop = obj["PROPIETARIO"] || '';
          if (prop.includes(',')) {
            const p = prop.split(',');
            prop = `${p[1] || ''} ${p[0] || ''}`.trim();
          }
          const cel = (obj["CELULAR DEL PROPIETARIO"] || obj["CELULAR"] || '').replace(/\\D/g, '').substring(0, 9);
          const est = (obj["ESTERILIZACIÓN"] || '').trim();

          if (nom || hc) {
            DB.mascotas.push({ hc: hc, nombre: nom, especie: esp, raza: raz, sexo: sex, propietario: prop, celular: cel, esterilizado: est });
            countMas++;
          }
        } else if (currentSection === "atenciones") {
          const fec = (obj["FECHA DE ATENCIÓN"] || obj["FECHA"] || '').trim();
          const tip = (obj["TIPO DE ATENCIÓN"] || obj["TIPO"] || 'Consulta').trim();
          const hc = (obj["HC"] || '').trim();
          const pac = (obj["PACIENTE"] || obj["MASCOTA"] || '').trim();
          const dx = (obj["DIAGNÓSTICO"] || obj["EXAMEN CLÍNICO EXTENDIDO"] || '').trim();
          const mot = (obj["MOTIVO DE ATENCIÓN"] || obj["ANAMNESIS"] || '').trim();
          const tx = (obj["TRATAMIENTO"] || '').trim();

          if (hc || fec) {
            DB.atenciones.push({ fecha: fec, tipo: tip, hc: hc, paciente: pac, motivo: mot, diagnostico: dx || mot, tratamiento: tx });
            countAtn++;
          }
        } else if (currentSection === "ventas") {
          const fec = (obj["FECHA DE EMISIÓN"] || obj["FECHA"] || '').trim();
          const comp = (obj["DOCUMENTO"] || obj["BOLETA/FACTURA"] || `${obj["SERIE"] || ''}-${obj["NÚMERO"] || ''}`).replace("BOLETA DE VENTA ELECTRONICA: ", "").trim();
          let cli = obj["CLIENTE"] || obj["DENOMINACIÓN"] || '';
          if (cli.includes(',')) {
            const p = cli.split(',');
            cli = `${p[1] || ''} ${p[0] || ''}`.trim();
          }
          const itm = (obj["CONCEPTO"] || obj["PRODUCTO / SERVICIO"] || obj["ITEM"] || 'Venta General').trim();
          const tot = parseFloat(String(obj["TOTAL"] || '0').replace(/[^0-9.]/g, '')) || 0;

          DB.ventas.push({ fecha: fec, comprobante: comp, cliente: cli, item: itm, total: tot });
          countVnt++;
        }
      }

      guardarDB();
      actualizarDashboard();
      document.getElementById('textarea-pegar-csv').value = '';

      alert(`¡Texto procesado con éxito!\\n\\n• Clientes agregados: ${countCli}\\n• Mascotas agregadas: ${countMas}\\n• Atenciones clínicas: ${countAtn}\\n• Registros de venta: ${countVnt}`);
      
      if (countCli > 0) cambiarTab('clientes');
      else if (countMas > 0) cambiarTab('mascotas');
      else if (countAtn > 0) cambiarTab('atenciones');
      else if (countVnt > 0) cambiarTab('ventas');
    }
"""

if "function procesarArchivoSubido" in content:
    content = content.replace("function procesarArchivoSubido", js_function + "\n    function procesarArchivoSubido")

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html actualizado con la funcionalidad de pegar texto directo.")
