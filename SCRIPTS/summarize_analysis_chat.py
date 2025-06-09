import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "DATA_POOL")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "FLOURISH_EXPORTS")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "FLOURISH_SUMMARY_CHAT.csv")

MODELOS_CHAT = ["deepseek-r1_1.5b", "chatgpt-4.1-nano"]

rows = []
for modelo in MODELOS_CHAT:
    path = os.path.join(INPUT_FOLDER, f"analysis_{modelo}.json")
    print(f"🔍 Buscando archivo: {path}")
    if not os.path.exists(path):
        print(f"❌ No encontrado: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)
        for item in content:
            for criterio, datos in item["scores"].items():
                rows.append({"Modelo": modelo, "Criterio": criterio, "Valor": datos["value"]})

if not rows:
    print("⚠️ No se cargaron datos.")
else:
    df = pd.DataFrame(rows)
    summary = df.groupby(["Modelo", "Criterio"]).agg(
        Media_puntos=('Valor', 'mean'),
        Desviacion_estandar=('Valor', 'std'),
        Minimo=('Valor', 'min'),
        Maximo=('Valor', 'max'),
        Mediana=('Valor', 'median')
    ).reset_index()
    summary["Media_%"] = (summary["Media_puntos"] / 5) * 100
    summary.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Exportado a {OUTPUT_FILE}")
