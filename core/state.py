"""Gestión del estado de sesión y memoria del usuario en Streamlit.

Este módulo administra la información básica del usuario del gimnasio
(objetivo, nivel, días disponibles, datos antropométricos y posibles
restricciones) y el historial de mensajes almacenados en
``st.session_state``.

También incluye utilidades para identificar estos datos a partir de texto
libre, construir una memoria reciente de la conversación y reiniciar el
estado de la sesión.
"""

import re

import streamlit as st


# Estado inicial utilizado cuando aún no se ha identificado al usuario.
USUARIO_INICIAL = {
    "nombre": "No registrado",
    "objetivo": "No registrado",
    "nivel": "No registrado",
    "dias_disponibles": "No registrado",
    "peso_kg": "No registrado",
    "altura_cm": "No registrado",
    "edad": "No registrado",
    "sexo": "No registrado",
    "restricciones": [],
}


# Frases utilizadas para identificar el objetivo de entrenamiento del
# usuario a partir de texto libre.
OBJETIVOS = {
    "perder grasa": "perdida_grasa",
    "bajar de peso": "perdida_grasa",
    "quemar grasa": "perdida_grasa",
    "definir": "perdida_grasa",
    "perdida de grasa": "perdida_grasa",
    "pérdida de grasa": "perdida_grasa",
    "ganar musculo": "hipertrofia",
    "ganar músculo": "hipertrofia",
    "ganar masa muscular": "hipertrofia",
    "aumentar masa muscular": "hipertrofia",
    "hipertrofia": "hipertrofia",
    "ganar fuerza": "fuerza",
    "levantar mas peso": "fuerza",
    "levantar más peso": "fuerza",
    "fuerza maxima": "fuerza",
    "fuerza máxima": "fuerza",
    "resistencia": "resistencia",
    "mejorar mi resistencia": "resistencia",
    "cardio": "resistencia",
    "mantener": "mantenimiento",
    "mantenimiento": "mantenimiento",
}

# Niveles de experiencia reconocidos en el texto del usuario.
NIVELES = ["principiante", "intermedio", "avanzado"]

# Palabras clave que indican una posible molestia, dolor o lesión y que
# deben registrarse como restricción para el agente.
PALABRAS_RESTRICCION = ["dolor", "lesion", "lesión", "lesionado", "lesionada", "molestia"]


def inicializar_estado() -> None:
    """Inicializa las variables necesarias en el estado de sesión.

    Crea la información inicial del usuario y el historial de mensajes
    únicamente cuando dichas variables aún no existen en
    ``st.session_state``, para conservarlas entre las distintas
    ejecuciones de la aplicación Streamlit dentro de una misma sesión.
    """
    if "usuario" not in st.session_state:
        st.session_state.usuario = {
            **USUARIO_INICIAL,
            "restricciones": [],
        }

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []


def actualizar_estado_usuario(texto: str) -> None:
    """Actualiza los datos del usuario identificados en un texto.

    Analiza el mensaje recibido para detectar el nombre, el objetivo de
    entrenamiento, el nivel de experiencia, los días disponibles por
    semana, datos antropométricos (peso, altura, edad, sexo) y posibles
    restricciones (dolor o lesiones). Los valores encontrados se
    almacenan directamente en ``st.session_state.usuario``.

    Args:
        texto: Mensaje escrito por el usuario del cual se intentará
            extraer su información personal y de entrenamiento.
    """
    texto_lower = texto.lower()
    usuario = st.session_state.usuario

    patron_nombre = r"(?:soy|me llamo)\s+([A-Za-zÁÉÍÓÚáéíóúÑñ]+)"
    coincidencia = re.search(patron_nombre, texto, re.IGNORECASE)
    if coincidencia:
        usuario["nombre"] = coincidencia.group(1).capitalize()

    for frase, objetivo in OBJETIVOS.items():
        if frase in texto_lower:
            usuario["objetivo"] = objetivo
            break

    for nivel in NIVELES:
        if nivel in texto_lower:
            usuario["nivel"] = nivel
            break

    coincidencia = re.search(r"(\d+)\s*(?:d[ií]as|veces)", texto_lower)
    if coincidencia:
        usuario["dias_disponibles"] = coincidencia.group(1)

    coincidencia = re.search(r"(\d{2,3})\s*kg", texto_lower)
    if coincidencia:
        usuario["peso_kg"] = coincidencia.group(1)

    coincidencia = re.search(r"(\d{3})\s*cm", texto_lower)
    if coincidencia:
        usuario["altura_cm"] = coincidencia.group(1)
    else:
        coincidencia = re.search(r"1[.,](\d{2})\s*m\b", texto_lower)
        if coincidencia:
            usuario["altura_cm"] = str(100 + int(coincidencia.group(1)))

    coincidencia = re.search(r"(\d{1,2})\s*a[ñn]os", texto_lower)
    if coincidencia:
        usuario["edad"] = coincidencia.group(1)

    if "hombre" in texto_lower or "masculino" in texto_lower:
        usuario["sexo"] = "hombre"
    elif "mujer" in texto_lower or "femenino" in texto_lower:
        usuario["sexo"] = "mujer"

    for palabra in PALABRAS_RESTRICCION:
        if palabra in texto_lower and texto not in usuario["restricciones"]:
            usuario["restricciones"].append(texto)
            break


def agregar_mensaje(role: str, content: str) -> None:
    """Agrega un mensaje al historial de conversación de la sesión.

    Args:
        role: Rol asociado al mensaje, por ejemplo ``"user"`` o
            ``"assistant"``.
        content: Contenido textual del mensaje que se desea almacenar.
    """
    st.session_state.mensajes.append(
        {
            "role": role,
            "content": content,
        }
    )


def obtener_memoria(limite: int = 6) -> str:
    """Construye una representación textual de los mensajes recientes.

    Args:
        limite: Número máximo de mensajes recientes que se incluirán.
            Por defecto se utilizan los últimos 6 mensajes.

    Returns:
        Cadena con los mensajes recientes en formato ``"role: content"``,
        separados por saltos de línea. Devuelve una cadena vacía si no
        existen mensajes almacenados.
    """
    mensajes = st.session_state.mensajes[-limite:]

    return "\n".join(
        f"{mensaje['role']}: {mensaje['content']}"
        for mensaje in mensajes
    )


def reiniciar_estado() -> None:
    """Restablece la información de la sesión a sus valores iniciales.

    Elimina el historial de conversación y reemplaza la información del
    usuario por una nueva copia de ``USUARIO_INICIAL``.
    """
    st.session_state.mensajes = []
    st.session_state.usuario = {**USUARIO_INICIAL, "restricciones": []}
