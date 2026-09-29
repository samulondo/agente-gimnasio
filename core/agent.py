"""Núcleo del Agente de Gimnasio v2 con LangChain.

Decide si una solicitud se resuelve mediante una Chain determinista
(preguntas conceptuales) o mediante un Agent con múltiples Tools
(consultas que requieren datos del usuario, rutinas, ejercicios,
nutrición o una recomendación priorizada).
"""

from typing import TypedDict

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from chains.response_chain import crear_respuesta_chain
from chains.router_chain import crear_router_chain
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from prompts.gym_prompt import AGENT_SYSTEM_TEMPLATE
from tools.ejercicio_tool import consultar_ejercicio
from tools.fecha_tool import obtener_fecha
from tools.nutricion_tool import calcular_macros, consultar_nutricion
from tools.recomendacion_tool import generar_recomendacion_priorizada
from tools.rutina_tool import consultar_rutina


class Usuario(TypedDict):
    """Representa la información de entrenamiento conocida del usuario."""

    nombre: str
    objetivo: str
    nivel: str
    dias_disponibles: str
    peso_kg: str
    altura_cm: str
    edad: str
    sexo: str
    restricciones: list[str]


TOOLS = [
    obtener_fecha,
    consultar_rutina,
    consultar_ejercicio,
    consultar_nutricion,
    calcular_macros,
    generar_recomendacion_priorizada,
]


def _crear_modelo() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )


def _construir_system_prompt(usuario: Usuario, memoria: str) -> str:
    restricciones = (
        "; ".join(usuario["restricciones"]) if usuario["restricciones"] else "Ninguna registrada"
    )

    return AGENT_SYSTEM_TEMPLATE.format(
        nombre=usuario["nombre"],
        objetivo=usuario["objetivo"],
        nivel=usuario["nivel"],
        dias_disponibles=usuario["dias_disponibles"],
        peso_kg=usuario["peso_kg"],
        altura_cm=usuario["altura_cm"],
        edad=usuario["edad"],
        sexo=usuario["sexo"],
        restricciones=restricciones,
        memoria=memoria or "Sin memoria reciente.",
    )


def _extraer_texto_final(result: dict) -> str:
    """Extrae el contenido textual del último mensaje del Agent."""
    mensajes = result.get("messages", [])

    if not mensajes:
        return "No fue posible generar una respuesta."

    contenido = mensajes[-1].content

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                partes.append(str(bloque.get("text", "")))
            elif isinstance(bloque, str):
                partes.append(bloque)
        texto = "\n".join(p for p in partes if p).strip()
        return texto or "No fue posible generar una respuesta."

    return str(contenido)


def _detectar_tools_usadas(result: dict) -> list[str]:
    """Obtiene los nombres de las Tools invocadas por el modelo."""
    usadas: list[str] = []

    for mensaje in result.get("messages", []):
        tool_calls = getattr(mensaje, "tool_calls", None) or []

        for call in tool_calls:
            nombre = call.get("name")
            if nombre and nombre not in usadas:
                usadas.append(nombre)

    return usadas


def responder(mensaje_usuario: str, usuario: Usuario, memoria: str) -> dict:
    """Responde mediante Chain o Agent según la naturaleza de la consulta.

    Primero ejecuta la Router Chain para clasificar la solicitud. Si la
    ruta elegida es "chain", responde con la Response Chain (rápida y
    sin herramientas). Si es "agent", instancia un Agent multi-tool con
    el contexto del usuario y deja que Gemini decida qué herramientas
    invocar.

    Args:
        mensaje_usuario: Mensaje enviado por el usuario.
        usuario: Información de entrenamiento actual del usuario.
        memoria: Representación textual de los mensajes recientes.

    Returns:
        Diccionario con la respuesta generada, la ruta elegida
        ("Chain" o "Agent"), el motivo de esa elección y la lista de
        herramientas utilizadas (vacía si fue por Chain).
    """
    router = crear_router_chain()
    decision = router.invoke({"pregunta": mensaje_usuario})

    if decision.ruta == "chain":
        chain = crear_respuesta_chain()
        texto = chain.invoke({"pregunta": mensaje_usuario})

        return {
            "respuesta": texto,
            "ruta": "Chain",
            "motivo": decision.motivo,
            "tools": [],
        }

    model = _crear_modelo()

    agent = create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=_construir_system_prompt(usuario=usuario, memoria=memoria),
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": mensaje_usuario}]}
    )

    return {
        "respuesta": _extraer_texto_final(result),
        "ruta": "Agent",
        "motivo": decision.motivo,
        "tools": _detectar_tools_usadas(result),
    }
