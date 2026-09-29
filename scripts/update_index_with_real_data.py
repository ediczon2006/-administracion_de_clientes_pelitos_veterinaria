import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
data_path = BASE_DIR / "data" / "pelitos_datos_reales.json"
index_path = BASE_DIR / "index.html"

with open(data_path, "r", encoding="utf-8") as f:
    datos_reales = json.load(f)

with open(index_path, "r", encoding="utf-8") as f:
    index_html = f.read()

# Convertir datos a JSON compacto para index.html
datos_json_str = json.dumps(datos_reales, ensure_ascii=False)

# Buscar dónde está STORAGE_KEY o cargarDB en index.html
target_str = """    const STORAGE_KEY = "pelitos_crm_data_v1";
    let DB = cargarDB();

    function cargarDB() {"""

replacement_str = f"""    const STORAGE_KEY = "pelitos_crm_data_v2_reales";
    const DATOS_REALES_PELITOS = {datos_json_str};

    let DB = cargarDB();

    function cargarDB() {{
      const data = localStorage.getItem(STORAGE_KEY);
      if (data) {{
        try {{
          const parsed = JSON.parse(data);
          if (parsed && parsed.clientes && parsed.clientes.length > 0) return parsed;
        }} catch(e) {{ }}
      }}
      // Cargar los datos reales por defecto
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DATOS_REALES_PELITOS));
      return DATOS_REALES_PELITOS;
    }}"""

if target_str in index_html:
    index_html = index_html.replace(target_str, replacement_str)
    print("Reemplazo de datos iniciales realizado con éxito.")
else:
    print("No se encontró target_str exacto, buscando alternativo...")
    # Si ya se había modificado, buscar por STORAGE_KEY
    import re
    index_html = re.sub(
        r'const STORAGE_KEY = ".*?";[\s\S]*?let DB = cargarDB\(\);[\s\S]*?function cargarDB\(\) \{[\s\S]*?return \{ clientes: \[\], mascotas: \[\], atenciones: \[\], ventas: \[\], citas: \[\], seguimientos: \[\] \};\s*\}',
        replacement_str,
        index_html
    )

with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_html)

print("index.html actualizado.")
