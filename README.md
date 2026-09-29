# Agente de Gimnasio (v2 · LangChain)

Agente conversacional construido con Streamlit, LangChain y Gemini que
ayuda con rutinas de entrenamiento, técnica de ejercicios y alimentación
deportiva. Evoluciona la v1 (SDK nativo `google-genai`) hacia una
composición agéntica con **Router Chain**, **Response Chain**, un
**Agent multi-tool** y **trazabilidad en vivo** en la interfaz.

## Arquitectura v2

```
Usuario → Streamlit UI → Regex State (perfil del usuario)
        → Router Chain (Pydantic: "chain" o "agent")
             ├── chain → Response Chain (LCEL directa, sin herramientas)
             └── agent → Agent multi-tool (create_agent + 6 tools)
        → Respuesta + Trazabilidad en el panel lateral
```

## Estructura del proyecto

```
app.py                          Interfaz de Streamlit (chat + panel lateral + trazabilidad)
config/settings.py              Carga de variables de entorno y validación
prompts/gym_prompt.py           Prompts centralizados (router, chain, agent)
chains/router_chain.py          Clasificador Pydantic: chain vs agent
chains/response_chain.py        Respuesta directa LCEL para preguntas conceptuales
chains/recomendacion_chain.py   Chain anidada: prioriza y adapta una rutina
core/agent.py                   Orquestador: despacha a Chain o Agent
core/state.py                   Estado de sesión, memoria y trazabilidad
tools/fecha_tool.py             Herramienta: fecha y día actual
tools/rutina_tool.py            Herramienta: consultar rutinas de entrenamiento
tools/ejercicio_tool.py         Herramienta: consultar ejercicios y su técnica
tools/nutricion_tool.py         Herramientas: guía nutricional y cálculo de macros
tools/recomendacion_tool.py     Herramienta con Chain anidada: recomendación priorizada
data/rutinas.json               Rutinas por objetivo, nivel y días por semana
data/ejercicios.json            Base de ejercicios con técnica y alternativas
data/nutricion.json             Guías nutricionales por objetivo
render.yaml                     Configuración de despliegue en Render
```

## Panel lateral

- **Estado del usuario**: nombre, objetivo, nivel, días disponibles, peso,
  altura, edad, sexo y molestias/restricciones, extraídos automáticamente
  del texto del usuario (`core/state.py`).
- **Última ejecución**: la ruta elegida por el Router Chain ("Chain" o
  "Agent"), el motivo de esa clasificación, y las herramientas invocadas
  en esa respuesta (si las hubo).

## Las 6 herramientas del Agent

- **obtener_fecha**: fecha, día de la semana y hora actual.
- **consultar_rutina(objetivo, nivel, dias)**: busca la rutina más adecuada.
- **consultar_ejercicio(consulta)**: técnica y alternativas de un ejercicio.
- **consultar_nutricion(objetivo)**: guía general de alimentación.
- **calcular_macros(...)**: TMB, gasto calórico y macros diarios (Mifflin-St Jeor).
- **generar_recomendacion_priorizada(...)**: *Chain anidada* — busca la
  rutina adecuada y luego usa una Chain de LangChain para priorizarla y
  adaptarla considerando molestias o restricciones del usuario.

## Cómo ejecutarlo localmente

1. Instala las dependencias (incluye LangChain):
   ```
   pip install -r requirements.txt
   ```
2. Copia `.env.example` a `.env` y coloca tu API key de Gemini:
   ```
   GEMINI_API_KEY=tu_api_key_aqui
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. Ejecuta la aplicación:
   ```
   streamlit run app.py
   ```

## Despliegue

El archivo `render.yaml` despliega la aplicación en Render como servicio
web gratuito. Configura `GEMINI_API_KEY` como variable de entorno secreta
en el dashboard del servicio.

## Correspondencia con el diseño conceptual

Esta implementación es una versión simplificada de la arquitectura
conceptual diseñada previamente (presentación, orquestación del agente,
herramientas/servicios y datos, con despliegue en contenedores sobre un
proveedor cloud). Para este prototipo académico:

- Streamlit cumple el rol de la capa de presentación (en lugar de una
  app React Native o Next.js independiente).
- `core/agent.py`, `chains/` y `prompts/` cumplen el rol de la capa de
  orquestación del agente (Router Chain, Response Chain, y el Agent
  multi-tool con Gemini).
- Los archivos JSON en `data/` cumplen el rol simplificado de la capa de
  datos, en lugar de una base de datos gestionada como PostgreSQL.
- El despliegue se realiza directamente en Render como un único servicio
  web, sin balanceador de carga, contenedores Docker independientes ni
  monitoreo dedicado, dado el alcance y tiempo disponibles para el
  prototipo.

El flujo de trabajo (interpretar solicitud, consultar contexto, decidir
e invocar herramientas, y responder) y los componentes lógicos definidos
en el diseño sí están implementados y son coherentes con lo propuesto;
la Router Chain materializa explícitamente la decisión de "¿necesita
herramientas o no?" del diagrama de flujo original.

## Nota importante

Este agente ofrece guías generales de entrenamiento y nutrición. No
reemplaza a un médico, fisioterapeuta o nutricionista, especialmente ante
dolor, lesiones o condiciones de salud particulares.
