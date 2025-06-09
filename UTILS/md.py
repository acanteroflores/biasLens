import json
import os
import re


def limpiar_nombre(nombre):
    # Sustituye caracteres inválidos por espacios
    nombre_limpio = re.sub(r'[\\/*?:"<>|\'`]', ' ', nombre)
    # Elimina espacios al principio y al final, y colapsa espacios múltiples en uno solo
    return re.sub(r'\s+', ' ', nombre_limpio).strip()


def md_model(archivo_json, campo_titulo, campo_cuerpo, carpeta_salida="markdowns"):
    """
    Carga un JSON desde archivo, y genera un markdown por cada entrada usando dos campos especificados.

    :param archivo_json: Ruta al archivo JSON.
    :param campo_titulo: Campo que se usará como nombre del archivo y título del markdown.
    :param campo_cuerpo: Campo que se usará como cuerpo del markdown.
    :param carpeta_salida: Carpeta donde se guardarán los .md generados.
    """

    # Cargar JSON
    with open(archivo_json, "r", encoding="utf-8") as f:
        entries = json.load(f)

    N = 1

    # Asegurarse que sea una lista de entradas
    if not isinstance(entries, list):
        raise ValueError("⚠️ El JSON debe ser una lista de objetos (array de entries).")

    # Crear carpeta si no existe
    os.makedirs(carpeta_salida, exist_ok=True)

    for i, entry in enumerate(entries):
        titulo = entry.get(campo_titulo)
        cuerpo = entry.get(campo_cuerpo)

        if not titulo or not cuerpo:
            print(f"⚠️ Entrada {i} ignorada: falta campo '{campo_titulo}' o '{campo_cuerpo}'")
            continue

        # Normalizar nombre del archivo
        nombre_archivo = f"{titulo}".strip().replace(" ", "_").replace("/", "-") + f"{N}" + ".md"
        ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)
        N = N + 1

        # Crear contenido
        contenido_md = f"# {titulo}\n\n{cuerpo}"

        # Guardar archivo
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido_md)

        print(f"✅ Guardado: {ruta_archivo}")


def md_title(archivo_json, campo_cuerpo, carpeta_salida="markdowns"):
    """
    Crea un Markdown por cada entrada del JSON, usando la primera línea del contenido como título y nombre del archivo.

    :param archivo_json: Ruta al archivo JSON.
    :param campo_cuerpo: Campo que se usará como contenido del Markdown.
    :param carpeta_salida: Carpeta donde guardar los archivos .md
    """

    # Cargar JSON
    with open(archivo_json, "r", encoding="utf-8") as f:
        entries = json.load(f)

    if not isinstance(entries, list):
        raise ValueError("⚠️ El JSON debe ser una lista de objetos (array).")

    os.makedirs(carpeta_salida, exist_ok=True)

    for i, entry in enumerate(entries):
        cuerpo = entry.get(campo_cuerpo)

        if not cuerpo:
            print(f"⚠️ Entrada {i} ignorada: no se encontró el campo '{campo_cuerpo}'")
            continue

        # Extraer primera línea del cuerpo como título
        primera_linea = cuerpo.strip().splitlines()[0]
        titulo = primera_linea.strip()

        # Normalizar nombre de archivo
        nombre_archivo = titulo.replace(" ", "_").replace("/", "-").replace("?", "").replace(":", "").strip()
        nombre_archivo = nombre_archivo[:100]  # Limita a 100 caracteres
        nombre_archivo = limpiar_nombre(nombre_archivo)
        ruta_archivo = os.path.join(carpeta_salida, f"{nombre_archivo}.md")

        # Contenido final
        contenido_md = f"# {titulo}\n\n{cuerpo}"

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido_md)

        print(f"✅ Guardado: {ruta_archivo}")


# md_model("FINAL_NEWS.json", "model", "news_text", "markdown")
# md_title("FINAL_NEWS.json", "news_text", "markdown_title")


