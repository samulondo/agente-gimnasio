"""Interfaz principal del agente de gimnasio desarrollado con Streamlit.

Este módulo configura y ejecuta la interfaz web del agente de gimnasio.
Gestiona la visualización del estado del usuario, el historial de
conversación y la interacción entre el usuario y el agente basado en
Gemini.

El flujo principal de la aplicación incluye:

- Validación de la configuración requerida.
- Inicialización del estado de sesión.
- Visualización de la información de entrenamiento del usuario en el
  panel lateral izquierdo, actualizada en cada mensaje.
- Renderizado del historial de conversación.
- Captura de nuevos mensajes del usuario.
- Actualización del estado y la memoria conversacional.
- Generación de respuestas mediante el agente de gimnasio.
- Reinicio de la conversación cuando el usuario lo solicita.
"""

import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    agregar_mensaje,
    actualizar_estado_usuario,
    inicializar_estado,
    obtener_memoria,
    reiniciar_estado,
)


st.set_page_config(
    page_title="Agente de Gimnasio",
    page_icon="🏋️",
)


# Valida que las variables necesarias para utilizar Gemini estén configuradas.
try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()


# Inicializa el estado persistente de la sesión de Streamlit.
inicializar_estado()


# Encabezado principal de la aplicación.
st.title("🏋️ Agente de Gimnasio")
st.caption("Rutinas, ejercicios y alimentación")
st.write(
    "MVP con Gemini, contexto, memoria, estado y herramientas de rutinas, "
    "ejercicios y nutrición."
)


# Panel lateral izquierdo con la información de entrenamiento conocida del usuario.
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

    if st.button("Reiniciar conversación"):
        reiniciar_estado()
        st.rerun()


# Renderiza el historial de mensajes almacenados en la sesión.
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])


# Captura una nueva consulta del usuario.
prompt = st.chat_input("Pregunta sobre tu rutina, un ejercicio o tu alimentación...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_estado_usuario(prompt)
    agregar_mensaje("user", prompt)

    try:
        respuesta = responder(
            mensaje_usuario=prompt,
            usuario=st.session_state.usuario,
            memoria=obtener_memoria(),
        )
    except Exception as error:
        respuesta = f"Ocurrió un error al consultar Gemini: {error}"

    with st.chat_message("assistant"):
        st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)

    st.rerun()
