from SCRIPTS.newsGen_Chat import generate_chatmodel_news
from SCRIPTS.newsGen_Inst import generate_news_for_each_model_and_scenario
from SCRIPTS.analyzer_Inst import analyze_news_INST
from SCRIPTS.analyzer_Chat import analyze_news_CHAT
from SCRIPTS.scenarioGen_Inst import generate_scenarios_INST
from SCRIPTS.scenarioGen_Chat import generate_escenarios_CHAT
from SCRIPTS.analyzer_GPT import analyze_news_GPT
from SCRIPT.GPT import newsGPT, scenarioGPT
from UTILS.io import load_json, log
from UTILS.md import *
import sys

# =========================
# ⚙️ Parámetros principales
# =========================
modelos_INST = [
    "llama3.2:3b-instruct-q8_0",
    "mistral:instruct",
    "cas/salamandra-7b-instruct:latest"
]

modelos_CHAT = [
    "deepseek-r1:1.5b"
]

# INSTRUCTOR para el filtrado de los modelo CHAT
instructor = "mistral:instruct"   # Usado como modelo de reescritura y extracción

# Número de escenarios por modelo
n_scenarios = 2

# =========================
# 🧠 Generación de escenarios
# =========================
log("🚀 Generando escenarios...")

# Modelos INST
generate_scenarios_INST(modelos_INST, n_scenarios)

# Modelos CHAT
for model in modelos_CHAT:
    generate_escenarios_CHAT(model, instructor, n_scenarios)

# ChatGPT
scenarioGPT()

# =========================
# 📰 Generación de noticias
# =========================
log("📰 Generando noticias...")

# Modelos INST
generate_news_for_each_model_and_scenario(modelos_INST)

# Modelos CHAT
for model in modelos_CHAT:
    generate_chatmodel_news(model, instructor)

scenarios = "SCENARIOS/FINAL_SCENARIOS.json"

# ChatGPT
newsGPT(scenarios, "scenario_text")

# =========================
# ✅ Validación previa al análisis
# =========================
news_data = load_json("NEWS/FINAL_NEWS.json")
if not news_data or len(news_data) == 0:
    print("❌ ERROR: FINAL_NEWS.json está vacío o mal formateado. Aborta el análisis.")
    sys.exit(1)


# =========================
# 📔 Generación de Markdowns
# =========================
# md_model("NEWS/FINAL_NEWS.json", "model", "news_text", "NEWS/markdown")
# md_title("NEWS/FINAL_NEWS.json", "news_text", "NEWS/markdown_title")


# =========================
# 🔍 Análisis de noticias
# =========================
log("🔍 Iniciando análisis de noticias...")

# Modelos INST
for model in modelos_INST:
    analyze_news_INST(model)

# Modelos CHAT
for model in modelos_CHAT:
    analyze_news_CHAT(model, instructor)

# ChatGPT
analyze_news_GPT()

# =========================
# 📊 Resumen para Flourish
# =========================
import subprocess

print("\n📊 Generando CSVs de resumen para Flourish...\n")

subprocess.run(["python", "SCRIPTS/summarize_analysis_inst.py"])
subprocess.run(["python", "SCRIPTS/summarize_analysis_chat.py"])
subprocess.run(["python", "SCRIPTS/summarize_analysis_all.py"])

print("\n✅ CSVs exportados correctamente: INST, CHAT y ALL\n")


print("\n✅✅✅ ALL COMPLETED ✅✅✅\n")
