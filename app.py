"""Interfaz principal del agente de gimnasio (v03, LangGraph).

Gestiona la visualización del estado del usuario, la trazabilidad de nodos
recorridos en LangGraph, el Thread ID activo, el diagrama del grafo, el historial
de conversación y la interacción mediante el gestor de sesión de LangGraph.
"""

import streamlit as st

from config.settings import validar_configuracion
from core.session import ejecutar_agente, obtener_o_crear_thread_id, obtener_grafo
from core.state import (
    agregar_mensaje,
    actualizar_estado_usuario,
    inicializar_estado,
    reiniciar_estado,
)


st.set_page_config(
    page_title="Agente de Gimnasio",
    page_icon="🏋️",
    layout="wide"
)


try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()


inicializar_estado()
thread_id = obtener_o_crear_thread_id()
grafo = obtener_grafo()


st.title("🏋️ Agente de Gimnasio v03")
st.caption("Rutinas, ejercicios y alimentación")
st.write(
    "Evolución a LangGraph: Grafo de Estados, Reducers, MemorySaver, "
    "Threads y Trazabilidad en tiempo real."
)


# ==========================================
# BARRA LATERAL (PERFIL Y TRAZABILIDAD)
# ==========================================
with st.sidebar:
    st.subheader("Estado del usuario")

    usuario = st.session_state.usuario

    st.write("**Nombre:**", usuario["nombre"])
    st.write("**Objetivo:**", usuario["objetivo"])
    st.write("**Nivel:**", usuario["nivel"])
    st.write("**Días disponibles/semana:**", usuario["dias_disponibles"])
    st.write("**Peso (kg):**", usuario["peso_kg"])
    st.write("**Altura (cm):**", usuario["altura_cm"])
    st.write("**Edad:**", usuario["edad"])
    st.write("**Sexo:**", usuario["sexo"])

    st.markdown("**Molestias / restricciones:**")
    if usuario["restricciones"]:
        for restriccion in usuario["restricciones"]:
            st.write("⚠️", restriccion)
    else:
        st.write("Ninguna registrada")

    st.divider()

    st.subheader("🔍 Trazabilidad LangGraph")
    st.caption(f"**Thread ID:** `{thread_id}`")

    # Mostrar secuencia de nodos recorridos en la última ejecución
    if "pasos_ejecutados" in st.session_state and st.session_state.pasos_ejecutados:
        pasos_str = " ➔ ".join(["START"] + st.session_state.pasos_ejecutados + ["END"])
        st.success(f"**Nodos recorridos:**\n{pasos_str}")
    else:
        st.info("Sin ejecuciones aún")

    # Visualización del Diagrama Mermaid
    st.subheader("📐 Arquitectura del Grafo")
    try:
        mermaid_png = grafo.get_graph().draw_mermaid_png()
        st.image(mermaid_png, caption="Grafo de Estados de LangGraph")
    except Exception:
        st.caption("Grafo compilado y activo.")

    st.divider()

    if st.button("Reiniciar conversación"):
        reiniciar_estado()
        if "pasos_ejecutados" in st.session_state:
            del st.session_state["pasos_ejecutados"]
        st.rerun()


# ==========================================
# HISTORIAL Y CHAT PRINCIPAL
# ==========================================
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])


prompt = st.chat_input("Pregunta sobre tu rutina, un ejercicio o tu alimentación...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_estado_usuario(prompt)
    agregar_mensaje("user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Procesando consulta con LangGraph..."):
            try:
                # Invocación mediante el gestor de sesión con Thread ID
                resultado = ejecutar_agente(prompt)

                # Extraer la lista de nodos ejecutados para la barra lateral
                st.session_state.pasos_ejecutados = resultado.get("pasos_ejecutados", [])

                # Extraer la respuesta del último mensaje del modelo
                respuesta = resultado["messages"][-1].content
            except Exception as error:
                respuesta = f"Ocurrió un error al procesar la solicitud: {error}"

            st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)

    st.rerun()