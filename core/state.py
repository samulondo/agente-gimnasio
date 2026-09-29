"""Gestión del estado de sesión, memoria y trazabilidad en Streamlit.

Este módulo administra la información básica del usuario del gimnasio
(objetivo, nivel, días disponibles, datos antropométricos y posibles
restricciones), el historial de mensajes, y el registro de la última
ejecución del agente (ruta elegida por el enrutador, motivo y
herramientas invocadas) para mostrarlo en el panel de trazabilidad.
"""

import re

import streamlit as st


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

ULTIMA_EJECUCION_INICIAL = {
    "ruta": "Sin ejecución",
    "motivo": "",
    "tools": [],
}

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

NIVELES = ["principiante", "intermedio", "avanzado"]

PALABRAS_NO_NOMBRE = {
    "hombre", "mujer", "masculino", "femenino",
    "principiante", "intermedio", "avanzado",
}

PALABRAS_RESTRICCION = ["dolor", "lesion", "lesión", "lesionado", "lesionada", "molestia"]


def inicializar_estado() -> None:
    """Inicializa las variables necesarias en el estado de sesión."""
    if "usuario" not in st.session_state:
        st.session_state.usuario = {**USUARIO_INICIAL, "restricciones": []}

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if "ultima_ejecucion" not in st.session_state:
        st.session_state.ultima_ejecucion = {**ULTIMA_EJECUCION_INICIAL, "tools": []}


def actualizar_estado_usuario(texto: str) -> None:
    """Actualiza los datos del usuario identificados en un texto."""
    texto_lower = texto.lower()
    usuario = st.session_state.usuario

    patron_nombre = r"(?:soy|me llamo)\s+([A-Za-zÁÉÍÓÚáéíóúÑñ]+)"
    for coincidencia in re.finditer(patron_nombre, texto, re.IGNORECASE):
        posible_nombre = coincidencia.group(1)
        if posible_nombre.lower() not in PALABRAS_NO_NOMBRE:
            usuario["nombre"] = posible_nombre.capitalize()
            break

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
    """Agrega un mensaje al historial de conversación de la sesión."""
    st.session_state.mensajes.append({"role": role, "content": content})


def obtener_memoria(limite: int = 6) -> str:
    """Construye una representación textual de los mensajes recientes."""
    mensajes = st.session_state.mensajes[-limite:]

    return "\n".join(
        f"{mensaje['role']}: {mensaje['content']}" for mensaje in mensajes
    )


def registrar_ejecucion(resultado: dict) -> None:
    """Guarda la ruta, el motivo y las herramientas de la última ejecución.

    Args:
        resultado: Diccionario devuelto por `core.agent.responder`, con
            las llaves "ruta", "motivo" y "tools".
    """
    st.session_state.ultima_ejecucion = {
        "ruta": resultado.get("ruta", "Desconocida"),
        "motivo": resultado.get("motivo", ""),
        "tools": resultado.get("tools", []),
    }


def reiniciar_estado() -> None:
    """Restablece la información de la sesión a sus valores iniciales."""
    st.session_state.mensajes = []
    st.session_state.usuario = {**USUARIO_INICIAL, "restricciones": []}
    st.session_state.ultima_ejecucion = {**ULTIMA_EJECUCION_INICIAL, "tools": []}
