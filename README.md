# Agente de Soporte con Gemini y Google Sheets 🤖📊

Este proyecto es un agente de Inteligencia Artificial que procesa y analiza automáticamente comentarios y quejas de clientes recibidos a través de Google Forms / Google Sheets.

## 🚀 Características
- **Conexión Automática a Google Sheets**: Lee respuestas directamente desde la hoja de cálculo.
- **Análisis con Gemini AI**: Clasifica cada comentario en categorías (*Ventas*, *Soporte Técnico*, *Logística*) y determina el sentimiento (*Positivo*, *Negativo*, *Neutro*).
- **Actualización de Hoja de Cálculo**: Registra la clasificación, sentimiento y marca la fila como procesada.
- **Ejecución Programada**: Se ejecuta automáticamente de manera periódica (cada 15 minutos por defecto).

## 🛠️ Requisitos Previos

1. Python 3.9 o superior.
2. Cuenta de Google Cloud Console con la API de Google Sheets / Google Drive habilitada y credenciales OAuth 2.0 descargadas (`client_secrets.json`).
3. API Key de Google Gemini (`GEMINI_API_KEY`).

## 📦 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd "Agente Soporte"
   ```

2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura tus credenciales:
   - Copia `client_secrets.json.example` a `client_secrets.json` y completa con tus credenciales de Google OAuth.
   - Establece tu clave API de Gemini en una variable de entorno:
     ```bash
     # En PowerShell (Windows)
     $env:GEMINI_API_KEY="tu_api_key_aqui"

     # En Bash / Linux / macOS
     export GEMINI_API_KEY="tu_api_key_aqui"
     ```

## ⚙️ Uso

Ejecuta el script principal:
```bash
python agente_soporte.py
```
