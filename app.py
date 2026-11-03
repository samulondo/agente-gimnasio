"""Interfaz principal del agente de gimnasio (v03, LangGraph).

Gestiona la visualización del estado del usuario, la trazabilidad de nodos
recorridos en LangGraph, el Thread ID activo, el diagrama del grafo, el historial
de conversación y la interacción mediante el gestor de sesión de LangGraph.
"""

import streamlit as st
import time

from config.settings import validar_configuracion
from core.session import ejecutar_agente, obtener_o_crear_thread_id, obtener_grafo
from core.state import (
    agregar_mensaje,
    actualizar_estado_usuario,
    inicializar_estado,
    reiniciar_estado,
)


st.set_page_config(
    page_title="Agente de Gimnasio | v03",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>

/* Fondo principal */
.stApp {
    background: #090909 !important;
    color: #FFFFFF !important;
}

/* Barra lateral */
[data-testid="stSidebar"] {
    background: #111111 !important;
}

/* Encabezados */
h1, h2, h3 {
    color: #FF7A00 !important;
}

/* Texto */
p, label, span {
    color: #EAEAEA;
}

/* Cajas de chat */
[data-testid="stChatMessage"] {
    background-color: #151515;
    border: 1px solid #292929;
    border-radius: 15px;
    padding: 15px;
}

/* Entrada del chat */
[data-testid="stChatInput"] {
    background-color: #151515;
    border: 1px solid #FF7A00;
    border-radius: 12px;
}

/* Tarjetas */
.tarjeta-gym {
    background: linear-gradient(145deg, #171717, #101010);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #292929;
    border-bottom: 3px solid #FF7A00;
    transition: 0.3s;
}

/* Efecto al pasar el mouse */
.tarjeta-gym:hover {
    border: 1px solid #FF7A00;
    transform: translateY(-4px);
}

/* Botones */
.stButton > button {
    background: #FF7A00;
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: bold;
}

/* Botones al pasar el mouse */
.stButton > button:hover {
    background: #FF9500;
    color: white;
}

/* Ocultar decoración de Streamlit */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)



try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()


inicializar_estado()
thread_id = obtener_o_crear_thread_id()
grafo = obtener_grafo()


col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image(
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48",
        width=450
    )


st.markdown("""
<div style="text-align:center; padding:10px;">
    <h1 style="color:#FF7A00;">🔥 GYM AI</h1>
    <p style="color:#AAAAAA;">
        Tu entrenador personal inteligente
    </p>
    <hr style="border:1px solid #FF7A00;">
</div>
""", unsafe_allow_html=True)


st.title("🏋️ GYM AI")
st.caption("Tu asistente inteligente de entrenamiento y nutrición")



col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏋️ Crear rutina", use_container_width=True):
        st.session_state["pregunta_rapida"] = (
            "Crea una rutina de hipertrofia para principiantes"
        )

with col2:
    if st.button("💪 Consultar ejercicio", use_container_width=True):
        st.session_state["pregunta_rapida"] = (
            "Explícame cómo ejecutar correctamente un ejercicio"
        )

with col3:
    if st.button("🥗 Consultar nutrición", use_container_width=True):
        st.session_state["pregunta_rapida"] = (
            "Dame recomendaciones de nutrición para ganar músculo"
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



prompt = st.chat_input(
    "Pregunta sobre tu rutina, un ejercicio o tu alimentación..."
)

# Si se presionó un botón, utilizar su pregunta automáticamente
if not prompt:
    prompt = st.session_state.pop("pregunta_rapida", None)


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
                ultimo = resultado["messages"][-1]
                contenido = getattr(ultimo, "content", "")
                if isinstance(contenido, str):
                    respuesta = contenido
                elif isinstance(contenido, list):
                    respuesta = "\\n".join(
                        str(bloque.get("text", "")) if isinstance(bloque, dict) else str(bloque)
                        for bloque in contenido
                    ).strip()
                else:
                    respuesta = str(contenido)
                if not respuesta:
                    respuesta = "No pude generar una respuesta. Inténtalo de nuevo."
            except Exception as error:
                # Evita dejar la interfaz inutilizable cuando Gemini está temporalmente indisponible.
                detalle = str(error)
                if "503" in detalle or "UNAVAILABLE" in detalle.upper():
                    respuesta = (
                        "El modelo de Gemini está temporalmente ocupado (error 503). "
                        "Espera unos segundos y vuelve a intentarlo. Tu conversación sigue disponible."
                    )
                elif "429" in detalle or "RESOURCE_EXHAUSTED" in detalle.upper():
                    respuesta = (
                        "Se alcanzó temporalmente el límite de solicitudes de Gemini. "
                        "Espera un momento y vuelve a intentarlo."
                    )
                else:
                    respuesta = (
                        "Ocurrió un error al procesar la solicitud. "
                        "Verifica la configuración de GEMINI_API_KEY en Render e inténtalo de nuevo."
                    )
                st.session_state.ultimo_error = detalle
                st.error(f"Error técnico: {detalle}")

            st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)

    st.rerun()