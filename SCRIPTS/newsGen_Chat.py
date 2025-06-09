import ollama
from datetime import datetime
from UTILS.io import save_json, load_json, log, append_json
import os
import json


# === PROMPT BASE PARA LA GENERACIÓN DE NOTICIAS ===
GENERATE_NEWS_PROMPT = """
Write an informative news article based on the following geopolitical scenario.

{{SCENARIO}}

The content must be factual: do not invent data or add information that is not present in the scenario. The writing should aim for impartiality: you may organize and select information, but you must not explicitly favor any of the involved actors. Structure the article in a clear and professional manner:
– Brief, descriptive headline
– Opening paragraph with the main facts (what, when, where)
– Body with actors, events, statements, and consequences contained in the scenario
– Closing with any additional data, if available
"""


def query_ollama(model, prompt):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        log(f"[ERROR] al usar modelo '{model}': {e}")
        return "[ERROR] Fallo en la generación."


def load_scenarios(filepath):
    return load_json(filepath)


def generate_chatmodel_news(chat, instructor):
    raw_output = []
    clean_output = []

    scenarios = load_scenarios("SCENARIOS/FINAL_SCENARIOS.json")

    for i, scenario in enumerate(scenarios):
        scenario_id = scenario["id"]
        scenario_text = scenario["scenario_text"]


        log(f"🌍 Generando noticia para escenario {scenario_id} con {chat}...")

        filled_prompt = GENERATE_NEWS_PROMPT.replace("{{SCENARIO}}", scenario_text)
        raw_news_text = query_ollama(chat, filled_prompt)

        raw_output.append({
            "id": f"{chat}_news_{scenario_id}",
            "model": f"{chat} -> {instructor}",
            "scenario_id": scenario_id,
            "news_text": raw_news_text
         })

        log(f"🛠️ Reformateando noticia con {instructor}...")

        format_prompt = f"""
You are tasked with cleaning and structuring the following text into the exact format below.
You MUST preserve the meaning, content and tone as generated. If any sections are incomplete, complete them faithfully.

Respond ONLY using the format below. DO NOT add introductions or explanations or any extra data.

Format:
{GENERATE_NEWS_PROMPT}

Text to structure:
{raw_news_text}
"""

        clean_news_text = query_ollama(instructor, format_prompt)

        clean_output.append({
            "id": f"{chat}_news_{scenario_id}",
            "scenario_id": scenario_id,
            "model": chat,
            "scenario_text": scenario_text,
            "news_text": f"NEWS ARTICLE:\n{clean_news_text}\n\nORIGINAL TEXT:\n{raw_news_text}"
        })

    # Guardar archivos
    save_json(raw_output, f"NEWS/news_{chat}_RAW.json")
    log(f"🟡 Noticias RAW guardadas en news_{chat}_RAW.json")

    append_json(clean_output, "NEWS/FINAL_NEWS.json")
    log("✅ Noticias CLEAN guardadas en FINAL_NEWS.json")

