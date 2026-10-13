"""Gestor de sesión y Threads para LangGraph con Streamlit."""

import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from core.workflow import crear_grafo_gimnasio


def obtener_o_crear_thread_id() -> str:
    """Garantiza que exista un thread_id único en la sesión de Streamlit."""
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    return st.session_state.thread_id


def obtener_grafo():
    """Mantiene una instancia singleton del grafo compilado en la sesión de Streamlit."""
    if "grafo" not in st.session_state:
        st.session_state.grafo = crear_grafo_gimnasio()
    return st.session_state.grafo


def ejecutar_agente(mensaje_usuario: str) -> dict:
    """Invoca el grafo de LangGraph usando la configuración del thread_id."""
    thread_id = obtener_o_crear_thread_id()
    grafo = obtener_grafo()

    # Configuración de contexto para el checkpointer de LangGraph
    config = {"configurable": {"thread_id": thread_id}}

    # Estado inicial con el nuevo mensaje del usuario
    estado_inicial = {
        "messages": [HumanMessage(content=mensaje_usuario)],
        "usuario": st.session_state.get("usuario", {})
    }

    # Invocación con thread_id
    resultado = grafo.invoke(estado_inicial, config=config)
    return resultado