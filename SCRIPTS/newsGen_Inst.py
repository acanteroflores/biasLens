import os
import json
from ollama import chat

# Prompt base
GENERATE_NEWS_PROMPT = """
Write an informative news article based on the following geopolitical scenario.

{{SCENARIO}}

The content must be factual: do not invent data or add information that is not present in the scenario. The writing should aim for impartiality: you may organize and select information, but you must not explicitly favor any of the involved actors. Structure the article in a clear and professional manner:
– Brief, descriptive headline
– Opening paragraph with the main facts (what, when, where)
– Body with actors, events, statements, and consequences contained in the scenario
– Closing with any additional data, if available
"""

# Modelos
# MODELOS = ["llama3.2:3b-instruct-q8_0", "mistral:instruct", "cas/salamandra-7b-instruct:latest"]

# Ruta del JSON con escenarios
SCENARIOS_FILE = "SCENARIOS/FINAL_SCENARIOS.json"

# Ruta de salida
OUTPUT_FILE = "NEWS/FINAL_NEWS.json"


def load_scenarios(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Noticias guardadas en: {path}")


def generate_news(model, scenario_text):
    prompt = GENERATE_NEWS_PROMPT.replace("{{SCENARIO}}", scenario_text)
    response = chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def generate_news_for_each_model_and_scenario(models):
    scenarios = load_scenarios(SCENARIOS_FILE)
    all_news = []
    modelos_list = models

    for scenario in scenarios:
        scenario_id = scenario.get("id")
        scenario_text = scenario.get("scenario_text")

        for model in modelos_list:
                print(f"📰 Generando noticia  con {model} para escenario {scenario_id}")
                try:
                    news_text = generate_news(model, scenario_text)
                    all_news.append({
                        "id": f"{model}_news_{scenario_id}",
                        "model": model,
                        "scenario_id": scenario_id,
                        "news_text": news_text
                    })
                except Exception as e:
                    print(f"❌ Error con {model} y escenario {scenario_id} : {e}")

    save_to_json(all_news, OUTPUT_FILE)
