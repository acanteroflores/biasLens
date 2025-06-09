import ollama
import os
from UTILS.io import save_json, log, append_json

# === PROMPT BASE Y ESTRUCTURA ===
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
– Reaction of each country  
  * China  
  * United States  
  * France  
  * Russia  
– Official statements  
  * China  
  * United States  
  * France  
  * Russia  
– Reaction of uninvolved countries  
– Extra data  
– Estimated level of public interest (%)  
– Estimated plausibility of the scenario (%)  
– Degree of interpretive ambiguity (%)  
– Perceived risk of escalation or conflict (%)
"""

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

# === Modelos disponibles ===
AVAILABLE_MODELS = ["cas/salamandra-7b-instruct:latest", "llama3.2:3b-instruct-q8_0", "mistral:instruct"]


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


def generate_scenarios_INST(model_list, num_escenarios):

    for selected_model in model_list:
        # log(f"🔮 Generando {num_escenarios} escenarios con el modelo: {selected_model}")

        escenarios = []
        for i in range(num_escenarios):
            log(f"🧠 Generando escenario {i + 1}/{num_escenarios} para el modelo {selected_model}...")
            text = query_ollama(selected_model, GENERATE_SCENARIO_PROMPT)
            escenarios.append({
                "id": f"{selected_model}_scenario_{i + 1}",
                "model": selected_model,
                "scenario_text": text
            })

        output_dir = "SCENARIOS"
        os.makedirs(output_dir, exist_ok=True)
        append_json(escenarios, "SCENARIOS/FINAL_SCENARIOS.json")
        log(f"✅ Escenarios del modelo {selected_model} guardados")

