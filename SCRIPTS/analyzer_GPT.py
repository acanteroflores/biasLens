from UTILS.io import load_json, save_json, log
import openai
import time
import os

# Carga tu API key de forma segura
openai.api_key = "your_API_key"

# ID del Assistant creado en https://platform.openai.com/assistants
ASSISTANT_ID = "insert_assistant_ID_here"

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


def ask_assistant(text, criterion):
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

{examples}

Text: \"\"\"{text}\"\"\"
Score:
"""

    for attempt in range(3):
        try:
            # Crea el thread
            thread = openai.beta.threads.create()
            # Añade el mensaje
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            # Ejecuta el assistant
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID
            )

            # Espera la respuesta (polling)
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run_status.status in ["completed", "failed"]:
                    break
                time.sleep(1)

            if run_status.status == "completed":
                messages = openai.beta.threads.messages.list(thread_id=thread.id)
                result = messages.data[0].content[0].text.value.strip()
                try:
                    return int(result)
                except ValueError:
                    for char in result:
                        if char.isdigit():
                            return int(char)
                    log(f"⚠️ Respuesta inválida '{result}'")
            else:
                log(f"❌ Falló el assistant en intento {attempt + 1}/3")
        except Exception as e:
            log(f"❌ Excepción en assistant API: {e}")
        time.sleep(2)

    return None


def evaluate_text(text):
    scores = {}
    for criterion, weight in SECTIONS.items():
        note = ask_assistant(text, criterion)
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


def analyze_news_GPT():
    log(f"🧪 Iniciando análisis con Assistant {ASSISTANT_ID}")
    news_items = load_json("NEWS/FINAL_NEWS.json")
    results = []

    for news in news_items:
        news_id = news["id"]
        scenario_id = news["scenario_id"]
        news_model = news["model"]
        news_text = news["news_text"]

        log(f"🔍 Analizando noticia '{news_id}'...")
        scores = evaluate_text(news_text)
        index, percentage = compute_index(scores)

        result = {
            "news_id": news_id,
            "scenario_id": scenario_id,
            "news_model": news_model,
            "analyzer_model": "chatgpt-4.1-nano",
            "scores": scores,
            "composite_index": index,
            "percentage": percentage
        }

        results.append(result)
        save_path = f"DATA_POOL/analysis_chatgpt-4.1-nano.json"
        save_json(results, save_path)

    log(f"✅ Resultados guardados en {save_path}")

