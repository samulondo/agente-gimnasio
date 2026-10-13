"""Construcción y compilación del flujo de trabajo (StateGraph) del Agente de Gimnasio."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import GymState
from core.nodes import (
    enrutador_node,
    conceptual_node,
    agente_gimnasio_node,
    herramientas_node,
)


def crear_grafo_gimnasio():
    """Construye y compila el grafo de estados con persistencia en memoria."""
    builder = StateGraph(GymState)
    
    # Registro de Nodos
    builder.add_node("enrutador", enrutador_node)
    builder.add_node("nodo_conceptual", conceptual_node)
    builder.add_node("agente_gimnasio", agente_gimnasio_node)
    builder.add_node("herramientas", herramientas_node)

    # Arista inicial
    builder.add_edge(START, "enrutador")

    # Bifurcación del enrutador según la decisión del clasificador
    builder.add_conditional_edges(
        "enrutador",
        lambda s: "nodo_conceptual" if s.get("ruta") == "conceptual" else "agente_gimnasio"
    )

    # Función condicional: ¿Llamar a herramientas o terminar?
    def evaluar_tools(state: GymState):
        ultimo = state["messages"][-1]
        if hasattr(ultimo, "tool_calls") and ultimo.tool_calls:
            return "herramientas"
        return END

    builder.add_conditional_edges(
        "agente_gimnasio",
        evaluar_tools,
        {"herramientas": "herramientas", END: END}
    )

    # Bucle Cíclico: de herramientas retorna al agente de gimnasio
    builder.add_edge("herramientas", "agente_gimnasio")

    # La ruta conceptual finaliza la ejecución
    builder.add_edge("nodo_conceptual", END)

    # Compilación con checkpointer para persistencia de contexto
    return builder.compile(checkpointer=MemorySaver())