"""Nodos de ejecución para el grafo de LangGraph del Agente de Gimnasio."""

from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.state import GymState
from tools import TOOLS_GIMNASIO


# Modelo Pydantic para el clasificador/enrutador estructurado
class ClasificacionRuta(BaseModel):
    ruta: Literal["conceptual", "agente"] = Field(
        description="Ruta elegida: 'conceptual' para explicaciones teóricas sin herramientas, 'agente' para consultas que requieren herramientas."
    )
    motivo: str = Field(
        description="Razón por la cual se eligió la ruta."
    )


# Inicialización del modelo LLM base
modelo = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)

# Prompts de sistema
ENRUTADOR_SYSTEM_PROMPT = (
    "Analiza la solicitud del usuario del gimnasio y determina la mejor ruta: "
    "1. 'conceptual': Duda teórica general sobre ejercicios, nutrición o descanso sin requerir herramientas. "
    "2. 'agente': Consultas específicas sobre rutinas, ejercicios particulares o datos que exijan invocar herramientas."
)

CONCEPTUAL_SYSTEM_PROMPT = (
    "Eres un entrenador personal e instructor de gimnasio experto. "
    "Responde a las dudas teóricas sobre ejercicios, técnica, hipertrofia o nutrición "
    "de forma clara, motivadora y profesional."
)

AGENTE_SYSTEM_PROMPT = (
    "Eres el asistente principal de gimnasio. Cuentas con herramientas especializadas "
    "para consultar ejercicios, rutinas, nutrición y recomendaciones. Utilízalas según corresponda."
)


# Nodo 1: Clasificador estructurado
def enrutador_node(state: GymState) -> dict:
    modelo_estructurado = modelo.with_structured_output(ClasificacionRuta)
    mensajes = [SystemMessage(content=ENRUTADOR_SYSTEM_PROMPT)] + state["messages"]
    decision = modelo_estructurado.invoke(mensajes)
    
    return {
        "ruta": decision.ruta,
        "motivo": decision.motivo,
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["enrutador"]
    }


# Nodo 2: Respuesta teórica sin herramientas
def conceptual_node(state: GymState) -> dict:
    respuesta = modelo.invoke([SystemMessage(content=CONCEPTUAL_SYSTEM_PROMPT), *state["messages"]])
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["nodo_conceptual"]
    }


# Nodo 3: Razonamiento con herramientas vinculadas
def agente_gimnasio_node(state: GymState) -> dict:
    modelo_con_tools = modelo.bind_tools(TOOLS_GIMNASIO)
    respuesta = modelo_con_tools.invoke([SystemMessage(content=AGENTE_SYSTEM_PROMPT), *state["messages"]])
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["agente_gimnasio"]
    }


# Nodo 4: Ejecución nativa con ToolNode
_ejecutor_tools = ToolNode(TOOLS_GIMNASIO)

def herramientas_node(state: GymState) -> dict:
    resultado = _ejecutor_tools.invoke(state)
    return {
        "messages": resultado["messages"],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["herramientas"]
    }