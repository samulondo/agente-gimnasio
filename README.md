# Agente de Gimnasio

Agente conversacional construido con Streamlit y Gemini que ayuda con
rutinas de entrenamiento, técnica de ejercicios y alimentación deportiva.
Sigue la misma estructura del agente académico de referencia (contexto +
memoria + estado + herramientas), aplicada al dominio de gimnasio.

## Estructura del proyecto

```
app.py                      Interfaz de Streamlit (chat + panel lateral)
config/settings.py          Carga de variables de entorno y validación
core/agent.py                Contexto del agente e integración con Gemini
core/state.py                Estado de sesión, memoria y extracción de datos
tools/rutina_tool.py         Herramienta: consultar rutinas de entrenamiento
tools/ejercicio_tool.py      Herramienta: consultar ejercicios y su técnica
tools/nutricion_tool.py      Herramientas: guía nutricional y cálculo de macros
data/rutinas.json            Rutinas por objetivo, nivel y días por semana
data/ejercicios.json         Base de ejercicios con técnica y alternativas
data/nutricion.json          Guías nutricionales por objetivo
render.yaml                  Configuración de despliegue en Render
```

## Panel lateral (datos del usuario)

El panel izquierdo (`st.sidebar`) muestra y actualiza en cada mensaje:
nombre, objetivo (hipertrofia, pérdida de grasa, fuerza, resistencia,
mantenimiento), nivel (principiante, intermedio, avanzado), días
disponibles por semana, peso, altura, edad, sexo y cualquier molestia o
restricción que el usuario mencione (por ejemplo, dolor en una
articulación). Estos datos se extraen automáticamente del texto del
usuario (`core/state.py`) y se usan como contexto para el agente.

## Herramientas disponibles para el agente

- **consultar_rutina(objetivo, nivel, dias)**: busca en `data/rutinas.json`
  la rutina más adecuada.
- **consultar_ejercicio(consulta)**: busca en `data/ejercicios.json` por
  nombre, grupo muscular o equipo, y devuelve técnica y alternativas.
- **consultar_nutricion(objetivo)**: devuelve la guía general de
  `data/nutricion.json` (ajuste calórico, macros de referencia, tips,
  alimentos recomendados).
- **calcular_macros(peso_kg, altura_cm, edad, sexo, nivel_actividad,
  objetivo)**: calcula TMB, gasto calórico total y macros diarios
  (proteína, grasa, carbohidratos) con la fórmula de Mifflin-St Jeor.

## Cómo ejecutarlo localmente

1. Crea un entorno virtual e instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
2. Copia `.env.example` a `.env` y coloca tu API key de Gemini:
   ```
   GEMINI_API_KEY=tu_api_key_aqui
   ```
3. Ejecuta la aplicación:
   ```
   streamlit run app.py
   ```

## Despliegue

El archivo `render.yaml` permite desplegar la aplicación en Render como
servicio web gratuito. Configura `GEMINI_API_KEY` como variable de entorno
secreta en el dashboard del servicio.

## Nota importante

Este agente ofrece guías generales de entrenamiento y nutrición. No
reemplaza a un médico, fisioterapeuta o nutricionista, especialmente ante
dolor, lesiones o condiciones de salud particulares.
