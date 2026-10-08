"""
Práctica: Mi Primer Agente de IA
Agente de soporte: Google Forms -> Python -> Gemini -> Google Sheets
"""

import json
import os
import time

import schedule
import gspread
from google import genai
from google.genai import types

# ---------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------
ARCHIVO_CREDENCIALES = "client_secrets.json"
NOMBRE_HOJA = "Respuestas de Quejas (Base de Datos)"  # Nombre exacto de tu hoja
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "PEGA_AQUI_TU_API_KEY")
INTERVALO_MINUTOS = 15

# Índices de columnas (empiezan en 1 para gspread)
COL_CLASIFICACION = 4  # D
COL_SENTIMIENTO = 5    # E
COL_EJECUTADO = 6      # F

MODELO = "gemini-2.5-flash"
MARCADOR_API_KEY = "PEGA_AQUI_TU_API_KEY"

# Cliente de Gemini (se inicializa en el bloque principal)
cliente_gemini = None


# ---------------------------------------------------------------
# FUNCIÓN: Conectar con Google Sheets
# ---------------------------------------------------------------
def conectar_sheets():
    """Autentica con OAuth 2.0 y devuelve la primera hoja del libro."""
    gc = gspread.oauth(credentials_filename=ARCHIVO_CREDENCIALES)
    libro = gc.open(NOMBRE_HOJA)
    return libro.sheet1


# ---------------------------------------------------------------
# FUNCIÓN: Analizar con Gemini
# ---------------------------------------------------------------
def analizar_con_gemini(comentario):
    """Clasifica el comentario y detecta el sentimiento. Devuelve un dict."""
    instruccion_sistema = (
        "Eres un analista de soporte al cliente. Tu única tarea es devolver "
        "una respuesta en formato JSON, sin texto adicional ni explicaciones."
    )

    instruccion_usuario = (
        f'Analiza el siguiente comentario de un cliente:\n\n"{comentario}"\n\n'
        "Clasifícalo en UNA de estas categorías: Ventas, Soporte Técnico o Logística.\n"
        "Detecta el sentimiento: Positivo, Negativo o Neutro.\n\n"
        "Responde únicamente con este JSON:\n"
        '{"clasificacion": "<categoría>", "sentimiento": "<sentimiento>"}'
    )

    respuesta = cliente_gemini.models.generate_content(
        model=MODELO,
        contents=instruccion_usuario,
        config=types.GenerateContentConfig(system_instruction=instruccion_sistema),
    )

    # Limpiar posibles bloques de código ``` o ```json
    texto = respuesta.text.strip()
    if texto.startswith("```"):
        texto = texto.removeprefix("```json").removeprefix("```")
        texto = texto.removesuffix("```").strip()

    datos = json.loads(texto)
    return {
        "clasificacion": datos["clasificacion"],
        "sentimiento": datos["sentimiento"],
    }


# ---------------------------------------------------------------
# FUNCIÓN: Agente principal
# ---------------------------------------------------------------
def ejecutar_agente():
    """Ciclo completo: conectar, leer, filtrar, analizar y escribir."""
    print("\n--- Revisando nuevas quejas ---")

    # 1. Conectar
    try:
        hoja = conectar_sheets()
    except Exception as e:
        print(f"Error al conectar con Google Sheets: {e}")
        return

    # 2. Leer (omitir encabezados)
    filas = hoja.get_all_values()[1:]

    procesadas = 0
    for numero_fila, fila in enumerate(filas, start=2):
        # Completar la fila si viene más corta de lo esperado
        fila = fila + [""] * (COL_EJECUTADO - len(fila))

        # 3. Filtrar: omitir las que ya tienen "SI" en la columna F
        if fila[COL_EJECUTADO - 1].strip().upper() == "SI":
            continue

        nombre = fila[1].strip() or "Anónimo"
        comentario = fila[2].strip()

        # Omitir filas sin comentario
        if not comentario:
            continue

        # 4. Analizar
        try:
            resultado = analizar_con_gemini(comentario)
            print(
                f"Cliente: {nombre} | "
                f"Clasificación: {resultado['clasificacion']} | "
                f"Sentimiento: {resultado['sentimiento']}"
            )

            # 5. Escribir en la hoja
            hoja.update_cell(numero_fila, COL_CLASIFICACION, resultado["clasificacion"])
            hoja.update_cell(numero_fila, COL_SENTIMIENTO, resultado["sentimiento"])
            hoja.update_cell(numero_fila, COL_EJECUTADO, "SI")
            print(f"  -> Fila {numero_fila} guardada en Google Sheets.")
            procesadas += 1

        # 6. Manejo de errores: continuar con la siguiente fila
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error: Gemini no devolvió un JSON válido en la fila {numero_fila}: {e}")
            continue
        except Exception as e:
            print(f"Error procesando la fila {numero_fila}: {e}")
            continue

    if procesadas == 0:
        print("No hay quejas nuevas por procesar.")
    else:
        print(f"Listo: {procesadas} fila(s) procesada(s).")


# ---------------------------------------------------------------
# PUNTO DE ENTRADA
# ---------------------------------------------------------------
if __name__ == "__main__":
    # Validar la API Key
    if GEMINI_API_KEY == MARCADOR_API_KEY or not GEMINI_API_KEY.strip():
        print("ERROR: Debes reemplazar GEMINI_API_KEY con tu clave real de Gemini.")
        raise SystemExit(1)

    # Validar el archivo de credenciales
    if not os.path.exists(ARCHIVO_CREDENCIALES):
        print(f"ERROR: No se encontró '{ARCHIVO_CREDENCIALES}' en la carpeta del script.")
        raise SystemExit(1)

    # Inicializar el cliente de Gemini (global)
    cliente_gemini = genai.Client(api_key=GEMINI_API_KEY.strip())

    print(f"Agente de soporte iniciado. Revisará la hoja cada {INTERVALO_MINUTOS} minutos.")
    print("Presiona Ctrl+C para detenerlo.")

    # Ejecutar de inmediato
    ejecutar_agente()

    # Programar ejecuciones automáticas
    schedule.every(INTERVALO_MINUTOS).minutes.do(ejecutar_agente)

    # Mantener el script corriendo
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nAgente detenido.")
