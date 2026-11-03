# Agente de Gimnasio v03 — LangGraph

Aplicación conversacional desarrollada con Streamlit, LangChain, LangGraph y Gemini para orientar sobre rutinas, ejercicios y alimentación deportiva.

## Arquitectura

```text
START → enrutador
          ├── conceptual → END
          └── agente_gimnasio
                 ├── tool calls → herramientas → agente_gimnasio
                 └── respuesta final → END
```

- `StateGraph` define el flujo.
- `GymState` usa `add_messages` como reducer para incorporar mensajes al historial.
- `ToolNode` ejecuta las herramientas solicitadas por el modelo.
- `MemorySaver` conserva el estado durante la conversación.
- `thread_id` identifica el hilo de conversación.
- La interfaz muestra el perfil, el identificador del hilo y la ruta de nodos ejecutados.

## Requisitos

- Python 3.11
- Una clave de API de Google Gemini

## Ejecución local

1. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   ```
2. Actívalo en Windows:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia `.env.example` a `.env` y configura:
   ```dotenv
   GEMINI_API_KEY=tu_clave_real
   GEMINI_MODEL=gemini-3.8-flash
   ```
5. Ejecuta:
   ```bash
   streamlit run app.py
   ```

No subas `.env` ni compartas tu clave API. El repositorio incluye `.env.example` para documentar las variables necesarias.

## Despliegue en Render

El archivo `render.yaml` define el servicio web. En el panel de Render, configura `GEMINI_API_KEY` como variable secreta. Después de subir los cambios a GitHub, realiza un nuevo despliegue.

## Herramientas

Las herramientas están en `tools/` y consultan datos JSON o calculan estimaciones generales de nutrición. El agente debe utilizar herramientas para consultar datos concretos, en lugar de inventarlos.

## Limitaciones y seguridad

Las recomendaciones son informativas y no sustituyen a profesionales de salud, nutrición o fisioterapia. Ante dolor o lesión, no se debe recomendar entrenar a través del dolor. `MemorySaver` conserva el estado en memoria del proceso: no garantiza persistencia entre reinicios o nuevos despliegues.


## Pruebas locales y observabilidad (P4)

- La interfaz registra duración total de la invocación, cantidad de mensajes del estado y nodos recorridos.
- El panel lateral muestra los nodos de la última ejecución y las herramientas solicitadas por el modelo.
- Cuando ocurre una excepción, el chat presenta un mensaje comprensible y un expander de diagnóstico técnico. No publiques capturas que expongan secretos.
- La duración se mide en la aplicación; el consumo de tokens solo puede reportarse si el proveedor devuelve metadatos de uso.

### Checklist de validación manual

1. Pregunta conceptual: `¿Qué es la hipertrofia muscular?` (ruta conceptual).
2. Consulta con herramientas: `Consulta una rutina de hipertrofia para principiante de 4 días` (ruta agente y herramienta de rutinas).
3. Ejercicio: `¿Cómo se realiza la sentadilla?` (consulta de ejercicios).
4. Memoria: pregunta por un dato que se haya indicado en el mismo hilo.
5. Reinicio: pulsa Reiniciar conversación y verifica que el historial visual se vacíe.
6. Repite las pruebas en la URL pública de Render.

Registra para cada prueba: fecha, pregunta, resultado esperado, resultado obtenido, tiempo observado, nodos/herramientas y corrección aplicada si hubo fallo.
