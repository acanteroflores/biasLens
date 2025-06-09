import os
import json
import pandas as pd

# === CONFIGURACIÓN DE RUTAS ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "DATA_POOL")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "FLOURISH_EXPORTS")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "FLOURISH_SUMMARY_ALL.csv")

# === RECOGER TODOS LOS ARCHIVOS DE ANÁLISIS ===
rows = []
for filename in os.listdir(INPUT_FOLDER):
    if not filename.startswith("analysis_") or not filename.endswith(".json"):
        continue
    path = os.path.join(INPUT_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)
        for item in content:
            for criterio, datos in item["scores"].items():
                rows.append({
                    "Modelo": item.get("analyzer_model", "desconocido"),
                    "Criterio": criterio,
                    "Valor": datos["value"]
                })

# === AGRUPACIÓN Y EXPORTACIÓN ===
if not rows:
    print("⚠️ No se cargaron datos.")
else:
    df = pd.DataFrame(rows)
    resumen = df.groupby("Criterio").agg(
        Media_puntos=('Valor', 'mean'),
        Desviacion_estandar=('Valor', 'std'),
        Minimo=('Valor', 'min'),
        Maximo=('Valor', 'max'),
        Mediana=('Valor', 'median')
    ).reset_index()
    resumen["Media_%"] = (resumen["Media_puntos"] / 5) * 100
    resumen.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Exportado a {OUTPUT_FILE}")
