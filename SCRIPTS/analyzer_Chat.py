from UTILS.io import load_json, save_json, log
import requests
import time

SECTIONS = {
    "Perceived bias": 0.20,
    "Ambiguity": 0.10,
    "Discursive dominance": 0.20,
    "Ideological framing": 0.20,
    "Structural clarity / readability": 0.10,
    "Risk of biased interpretation": 0.20,
}

EXAMPLES = {
    "Perceived bias": "Example 5: The brave national army defeated the enemy terrorists.\nExample 0: All parties are described in a neutral and balanced tone.",
    "Ambiguity": "Example 5: Some say something might have happened somehow.\nExample 0: The event occurred at 10:00, according to witnesses and official sources.",
    "Discursive dominance": "Example 5: Only one actor is quoted or heard directly.\nExample 0: The article quotes multiple sides of the story.",
    "Ideological framing": "Example 5: The revolution was glorious and necessary to overthrow tyranny.\nExample 0: Events are described without ideological judgment.",
    "Structural clarity / readability": "Example 5: Long, unclear sentences with unnecessary complexity.\nExample 0: Clear structure, direct language, easy to understand.",
    "Risk of biased interpretation": "Example 5: The text leads to one emotional and obvious interpretation.\nExample 0: Multiple interpretations are presented without pushing a narrative.",
}


def ask_deepseek_then_extract(text, criterion, model_big, model_small, host='http://localhost:11434'):
    examples = EXAMPLES.get(criterion, "")
    prompt_big = f"""
Analyze the following news article using the criterion: "{criterion}".

{examples}

Only return a single number, no explanation.

Examples of good replies: 
- 5
- 3
- 4
- 2
- 1

Examples of bad replies: 
- 3: Moderately present 
- 3.5
- 3/5 
- 35/40 
- 65%...
- 7
- 0

Text:
\"\"\"{text}\"\"\"
"""

    try:
        response_big = requests.post(f'{host}/api/chat', json={
            "model": model_big,
            "messages": [{"role": "user", "content": prompt_big}],
            "stream": False
        })
        if response_big.status_code != 200:
            log(f"⚠️ Error {response_big.status_code} usando {model_big} para analizar '{criterion}'")
            return None

        analysis = response_big.json()["message"]["content"].strip()
    except Exception as e:
        log(f"❌ Excepción en análisis con {model_big}: {e}")
        return None

    time.sleep(1)

    prompt_small = f"""
Extract a score from 0 to 5 for the criterion: "{criterion}" based on the analysis below.

Only return a single number without decimals. No explanation.

Analysis:
\"\"\"{analysis}\"\"\"

Score:"""

    for attempt in range(3):
        try:
            response_small = requests.post(f'{host}/api/chat', json={
                "model": model_small,
                "messages": [{"role": "user", "content": prompt_small}],
                "stream": False
            })
            if response_small.status_code != 200:
                log(f"⚠️ Error {response_small.status_code} usando {model_small} para extraer score (intento {attempt + 1}/3)")
                continue

            result = response_small.json()["message"]["content"].strip()
            value = int(result)

            # Clamp entre 0 y 5
            if value < 1 or value > 5:
                log(f"⚠️ Valor fuera de rango corregido: {value} → clamped")
            return min(max(value, 1), 5)

        except Exception as e:
            log(f"❌ Excepción al extraer score con {model_small} (intento {attempt + 1}/3): {e}")
            time.sleep(1)

    return None


def evaluate_text(text, model_big, model_small):
    scores = {}
    for criterion, weight in SECTIONS.items():
        note = ask_deepseek_then_extract(text, criterion, model_big, model_small)
        scores[criterion] = {"value": note, "weight": weight}
        time.sleep(1)
    return scores


def compute_index(scores):
    total = 0
    for data in scores.values():
        if data["value"] is not None:
            total += data["value"] * data["weight"]
    percentage = total * 20
    return round(total, 2), round(percentage, 2)


def analyze_news_CHAT(model_big: str, model_small: str):
    log(f"Iniciando análisis de noticias con {model_big} + {model_small}...")
    news_items = load_json("NEWS/FINAL_NEWS.json")
    results = []

    for news in news_items:
        news_id = news["id"]
        scenario_id = news["scenario_id"]
        news_model = news["model"]
        news_text = news["news_text"]

        log(f"🔍 Analizando noticia '{news_id}' con {model_big}...")

        scores = evaluate_text(news_text, model_big, model_small)

        for criterio, datos in scores.items():
            log(f"[{news_id}] {criterio}: {datos['value']} (peso: {datos['weight']})")

        if not any(v["value"] is not None for v in scores.values()):
            log(f"⚠️ Todos los valores son None para '{news_id}'. El análisis se omitirá.")
            continue

        index, percentage = compute_index(scores)

        result = {
            "news_id": news_id,
            "scenario_id": scenario_id,
            "news_model": news_model,
            "analyzer_model_big": model_big,
            "analyzer_model_small": model_small,
            "scores": scores,
            "composite_index": index,
            "percentage": percentage
        }

        results.append(result)
        log(f"✅ Análisis añadido para '{news_id}' → índice: {index} ({percentage}%)")

    if results:
        safe_model_name = model_big.replace(":", "_").replace("/", "_")
        save_path = f"DATA_POOL/analysis_{safe_model_name}.json"
        save_json(results, save_path)
        log(f"📦 Análisis final de {model_big} guardado en {save_path}")
    else:
        log(f"⚠️ No se generaron análisis válidos para {model_big}. No se creó ningún archivo.")
