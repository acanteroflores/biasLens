import ollama
from datetime import datetime
from UTILS.io import save_json, log, append_json

# === PROMPT ESTRUCTURADO DEL ESCENARIO ===
PROMPT_STRUCTURE = """
– Summary of the situation  
– Date  
– Location  
– Events  
– Perceived consequences for each participant  
  * China  
  * United States  
  * France  
  * Russia
  * Spain
– Reaction of each country  
  * China  
  * United States  
  * France  
  * Russia
  * Spain 
– Official statements  
  * China  
  * United States  
  * France  
  * Russia
  * Spain  
– Reaction of uninvolved countries  
– Extra data  
– Estimated level of public interest (%)  
– Estimated plausibility of the scenario (%)  
– Degree of interpretive ambiguity (%)  
– Perceived risk of escalation or conflict (%)
"""

# === PROMPT PARA QUE DEEPSEEK GENERE EL ESCENARIO BASE ===
GENERATE_SCENARIO_PROMPT = f"""
You are tasked with generating a fictional geopolitical scenario involving the following countries: China, the United States, France, and Russia.

The content must follow these rules:
- DO NOT include opinions, judgments, or ideological interpretations.
- ONLY present verifiable data, neutral statements, official declarations, and measurable consequences.
- If other countries appear, include them only if they are directly involved in the event.

Use the exact structure below to present the information: \n
{PROMPT_STRUCTURE}

Important: The scenario should appear plausible and realistic, but leave room for interpretation.  
Include subtle tensions, unclear motives, or conflicting sources of information to reflect the complexity of international relations.
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


def generate_escenarios_CHAT(chat, instructor, repeats):
    raw_output = []
    clean_output = []

    for i in range(repeats):
        log(f"🌍 Generando escenario {i + 1} con DeepSeek...")

        raw_scenario_text = query_ollama(chat, GENERATE_SCENARIO_PROMPT)
        scenario_id = f"{chat}_{i + 1}"

        # Guardar original de DeepSeek
        raw_output.append({
            "id": scenario_id,
            "model": chat,
            "scenario_text": raw_scenario_text
        })

        log(f"🛠️ Reformateando escenario {i + 1} con {instructor}...")

        format_prompt = f"""
You are tasked with cleaning and structuring the following scenario into the exact format below.
You MUST preserve the meaning, content and tone as generated. If any sections are incomplete, complete them faithfully.

Respond ONLY using the format below. DO NOT add introductions or explanations.

Format:
{PROMPT_STRUCTURE}

Text to structure:
{raw_scenario_text}
"""

        clean_scenario_text = query_ollama(instructor, format_prompt)

        clean_output.append({
            "id": scenario_id,
            "model": chat,
            "scenario_text": f"SCENARIO CLEANED BY {instructor}:\n{clean_scenario_text}\n\nORIGINAL TEXT:\n{raw_scenario_text}"
        })

    # Guardar ambos archivos
    save_json(raw_output, f"SCENARIOS/scenarios_{chat}_RAW.json")
    log("🟡 Escenarios RAW guardados en scenarios_deepseek.json")

    append_json(clean_output, "SCENARIOS/FINAL_SCENARIOS.json")
    log("✅ Escenarios CLEAN guardados en scenariosCLEAN_deepseek.json")


