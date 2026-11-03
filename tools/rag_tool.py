
"""RAG del Agente de Gimnasio: recuperación semántica desde JSON."""

import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config.settings import GEMINI_API_KEY


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

_vectorstore = None


def cargar_documentos():
    """Convierte los archivos JSON del gimnasio en documentos."""

    documentos = []

    archivos = {
        "rutinas": DATA_DIR / "rutinas.json",
        "ejercicios": DATA_DIR / "ejercicios.json",
        "nutricion": DATA_DIR / "nutricion.json",
    }

    for categoria, ruta in archivos.items():
        with ruta.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if isinstance(datos, list):
            elementos = datos
        elif isinstance(datos, dict):
            elementos = [
                {"tema": clave, **valor}
                if isinstance(valor, dict)
                else {"tema": clave, "contenido": valor}
                for clave, valor in datos.items()
            ]
        else:
            continue

        for elemento in elementos:
            contenido = json.dumps(
                elemento,
                ensure_ascii=False,
                indent=2
            )

            documentos.append(
                Document(
                    page_content=contenido,
                    metadata={"categoria": categoria}
                )
            )

    return documentos


def obtener_base_vectorial():
    """Construye la base vectorial una sola vez por proceso."""

    global _vectorstore

    if _vectorstore is None:
        documentos = cargar_documentos()

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=GEMINI_API_KEY
        )

        _vectorstore = InMemoryVectorStore.from_documents(
            documents=documentos,
            embedding=embeddings
        )

    return _vectorstore


@tool
def buscar_conocimiento_gimnasio(pregunta: str) -> str:
    """Busca información relevante en la base de conocimientos del gimnasio.

    Úsala para recuperar información de rutinas, ejercicios y nutrición
    almacenada en los documentos JSON del proyecto.

    Args:
        pregunta: Pregunta o tema que se desea investigar.

    Returns:
        Fragmentos relevantes recuperados de la base de conocimientos.
    """

    base = obtener_base_vectorial()

    resultados = base.similarity_search(
        pregunta,
        k=4
    )

    if not resultados:
        return "No se encontró información relevante en la base de conocimientos."

    respuesta = []

    for i, documento in enumerate(resultados, start=1):
        respuesta.append(
            f"RESULTADO {i}\n"
            f"Categoría: {documento.metadata.get('categoria', 'General')}\n"
            f"Contenido:\n{documento.page_content}"
        )

    return "\n\n".join(respuesta)
