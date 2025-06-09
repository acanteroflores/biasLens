from UTILS.io import load_json, save_json, log
import requests
import time

# Evaluation criteria with weights
SECTIONS = {
    "Perceived bias": 0.20,
    "Ambiguity": 0.10,
    "Discursive dominance": 0.20,
    "Ideological framing": 0.20,
    "Structural clarity / readability": 0.10,
    "Risk of biased interpretation": 0.20,
}

# Prompt examples
EXAMPLES = {
    "Perceived bias": "Example 5: The brave national army defeated the enemy terrorists.\nExample 0: All parties are described in a neutral and balanced tone.",
    "Ambiguity": "Example 5: Some say something might have happened somehow.\nExample 0: The event occurred at 10:00, according to witnesses and official sources.",
    "Discursive dominance": "Example 5: Only one actor is quoted or heard directly.\nExample 0: The article quotes multiple sides of the story.",
    "Ideological framing": "Example 5: The revolution was glorious and necessary to overthrow tyranny.\nExample 0: Events are described without ideological judgment.",
    "Structural clarity / readability": "Example 5: Long, unclear sentences with unnecessary complexity.\nExample 0: Clear structure, direct language, easy to understand.",
    "Risk of biased interpretation": "Example 5: The text leads to one emotional and obvious interpretation.\nExample 0: Multiple interpretations are presented without pushing a narrative.",
}


def ask_ollama(text, criterion, model, host='http://localhost:11434'):
    examples = EXAMPLES.get(criterion, "")
    prompt = f"""
Evaluate the following text based on the criterion: "{criterion}". 
Respond with a single number from 0 to 5, using this scale:

0: Not present
1: Very slightly present
2: Slightly present
3: Moderately present
4: Strongly present
5: Fully present

Do not include any explanation or extra text. Just reply with the number without decimals.

Examples of good replies: 
- 5
- 3
- 7
- 10

Examples of bad replies: 
- 3: Moderately present 
- 3.5
- 3/5 
- 35/40 
- 65%...

{examples}

Text: \"\"\"{text}\"\"\"
Score:"""

    for attempt in range(3):
        try:
            response = requests.post(f'{host}/api/chat', json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            })
            if response.status_code == 200:
                result = response.json()['message']['content'].strip()

                try:
                    value = int(result)
                except ValueError:
                    # Heurística: buscar primer dígito válido si la respuesta es texto sucio
                    digits = [int(char) for char in result if char.isdigit()]
                    if digits:
                        value = digits[0]
                    else:
                        log(f"⚠️ Respuesta inválida '{result}' en intento {attempt + 1}/3")
                        continue

                # Clamp entre 0 y 5
                if value < 1 or value > 5:
                    log(f"⚠️ Valor fuera de rango corregido: {value} → clamped")
                return min(max(value, 1), 5)

            else:
                log(f"⚠️ Error {response.status_code} al consultar {model} para {criterion} (intento {attempt + 1}/3)")
        except Exception as e:
            log(f"❌ Excepción al llamar a Ollama (intento {attempt + 1}/3): {e}")
        time.sleep(1)

    return None


def evaluate_text(text, model):
    scores = {}
    for criterion, weight in SECTIONS.items():
        note = ask_ollama(text, criterion, model)
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


def analyze_news_INST(model_name: str):
    log(f"Iniciando análisis de noticias con {model_name}...")
    news_items = load_json("NEWS/FINAL_NEWS.json")
    results = []

    for news in news_items:
        news_id = news["id"]
        scenario_id = news["scenario_id"]
        news_model = news["model"]
        news_text = news["news_text"]

        log(f"🔍 Analizando noticia '{news_id}' con {model_name}...")

        scores = evaluate_text(news_text, model_name)

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
            "analyzer_model": model_name,
            "scores": scores,
            "composite_index": index,
            "percentage": percentage
        }

        results.append(result)
        log(f"✅ Análisis añadido para '{news_id}' → índice: {index} ({percentage}%)")

    if results:
        safe_model_name = model_name.replace(":", "_").replace("/", "_")
        save_path = f"DATA_POOL/analysis_{safe_model_name}.json"
        save_json(results, save_path)
        log(f"📦 Análisis final de {model_name} guardado en {save_path}")
    else:
        log(f"⚠️ No se generaron análisis válidos para {model_name}, no se guardó el archivo.")
