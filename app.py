"""Interfaz principal del agente de gimnasio (v2, LangChain).

Gestiona la visualización del estado del usuario, el panel de
trazabilidad de la última ejecución (ruta, motivo y herramientas
utilizadas), el historial de conversación y la interacción entre el
usuario y el agente basado en LangChain + Gemini.
"""

import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    agregar_mensaje,
    actualizar_estado_usuario,
    inicializar_estado,
    obtener_memoria,
    registrar_ejecucion,
    reiniciar_estado,
)


st.set_page_config(
    page_title="Agente de Gimnasio",
    page_icon="🏋️",
)


try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()


inicializar_estado()


st.title("🏋️ Agente de Gimnasio")
st.caption("Rutinas, ejercicios y alimentación")
st.write(
    "Versión con LangChain: Router Chain, Response Chain, Agent "
    "multi-tool y trazabilidad en tiempo real."
)


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
    st.subheader("Última ejecución")

    ejecucion = st.session_state.ultima_ejecucion
    st.write("**Ruta:**", ejecucion["ruta"])

    if ejecucion["motivo"]:
        st.caption(ejecucion["motivo"])

    if ejecucion["tools"]:
        st.write("**Tools utilizadas:**")
        for nombre in ejecucion["tools"]:
            st.write(f"- {nombre}")
    else:
        st.write("**Tools utilizadas:** ninguna")

    st.divider()

    if st.button("Reiniciar conversación"):
        reiniciar_estado()
        st.rerun()


for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])


prompt = st.chat_input("Pregunta sobre tu rutina, un ejercicio o tu alimentación...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_estado_usuario(prompt)
    agregar_mensaje("user", prompt)

    try:
        resultado = responder(
            mensaje_usuario=prompt,
            usuario=st.session_state.usuario,
            memoria=obtener_memoria(),
        )
        respuesta = resultado["respuesta"]
        registrar_ejecucion(resultado)
    except Exception as error:
        respuesta = f"Ocurrió un error al procesar la solicitud: {error}"

    with st.chat_message("assistant"):
        st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)

    st.rerun()
