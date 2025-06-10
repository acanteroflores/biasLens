import openai
import json

openai.api_key = "your_API_key"


def ask_my_assistant(assistant_id: str, prompt: str) -> str:
    # 1. Crear un hilo (thread)
    thread = openai.beta.threads.create()

    # 2. Añadir el mensaje del usuario al hilo
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # 3. Lanzar el assistant en ese hilo
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    # 4. Esperar a que termine
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break

    # 5. Obtener la respuesta
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for message in reversed(messages.data):
        if message.role == "assistant":
            return message.content[0].text.value.strip()

    return "[Sin respuesta del assistant]"


import json

ass_id = "asst_UXqJmMCelSeXHw1TZczozDT9"


def newsGPT(path_json: str, campo: str):
    import json
    """
    Abre un JSON, extrae un campo de cada entrada y lo pasa como argumento a una función.

    :param path_json: Ruta del archivo JSON.
    :param campo: El campo que quieres extraer de cada entrada.
    :param funcion: Función que se llamará con el valor de ese campo.
    """
    with open(path_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)

    x = 1

    for entry in datos:
        if campo in entry:
            nuevo_schema = ask_my_assistant(ass_id, campo)
            print(f"Noticia generada {x}/10")
            x = x + 1

            with open("NEWS/GPTnews.json", "r", encoding="utf-8") as archivo:
                data = json.load(archivo)

            data.append(nuevo_schema)

            with open("NEWS/GPTnews.json", "w", encoding="utf-8") as archivo:
                json.dump(data, archivo, indent=2)
        else:
            print(f"⚠️ Campo '{campo}' no encontrado en entry: {entry}")

    json.dump([json.loads(e) if isinstance(e, str) else e for e in
               json.load(open("NEWS/GPTnews.json", encoding="utf-8"))] + json.load(
        open("NEWS/FINAL_NEWS.json", encoding="utf-8")), open("NEWS/FINAL_NEWS.json", "w", encoding="utf-8"), indent=2)


def scenarioGPT():
    for i in range(2):
        nuevo_schema = ask_my_assistant("asst_eViGUJDZdyMYCeWOR3JK09IC", prompt="Generate one scenario")

        with open("SCENARIOS/GPTscenarios.json", "r", encoding="utf-8") as archivo:
            data = json.load(archivo)

        data.append(nuevo_schema)

        with open("SCENARIOS/GPTscenarios.json", "w", encoding="utf-8") as archivo:
            json.dump(data, archivo, indent=2)

    json.dump(json.load(open("SCENARIOS/FINAL_SCENARIOS.json")) + [json.loads(e) if isinstance(e, str) else e for e in
                                                                   json.load(open("SCENARIOS/GPTscenarios.json"))],
              open("SCENARIOS/FINAL_SCENARIOS.json", "w"), indent=2)
