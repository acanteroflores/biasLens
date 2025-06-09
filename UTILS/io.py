import os
import json
from datetime import datetime
import subprocess


# Crea una carpeta si no existe
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Guarda un diccionario/lista como JSON
def save_json(data, filepath):
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Carga un JSON y lo devuelve como objeto Python
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# Añade una línea de log con timestamp
def log(message, logfile='data/logs/run_log.txt'):
    ensure_dir(os.path.dirname(logfile))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print(line)  # También lo imprime por consola para feedback en tiempo real


def query_ollama(model_name, prompt):
    result = subprocess.run(
        ["ollama", "run", model_name],
        input=prompt.encode('utf-8'),
        capture_output=True
    )
    return result.stdout.decode('utf-8').strip()


def append_json(data, output_path):
    # Leer datos actuales (si existen)
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as archivo:
            try:
                datos_existentes = json.load(archivo)
                if not isinstance(datos_existentes, list):
                    datos_existentes = [datos_existentes]
            except json.JSONDecodeError:
                datos_existentes = []
    else:
        datos_existentes = []

    # Añadir nuevos datos (puede ser una lista o un solo objeto)
    if isinstance(data, list):
        datos_existentes.extend(data)
    else:
        datos_existentes.append(data)

    # Escribir todo de nuevo
    with open(output_path, "w", encoding="utf-8") as archivo:
        json.dump(datos_existentes, archivo, indent=4, ensure_ascii=False)
