from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os
import streamlit as st

#load_dotenv()
openai_nvapi_key = st.secrets["OPENAI_NVAPI_KEY"]
#openai_nvapi_key = os.getenv("OPENAI_NVAPI_KEY")

## Construct the system prompt
prompt_template = """
### [INST]

Eres un experto en marketing y creación de contenido para redes sociales.
Tu tarea es crear un mensaje promocional diferente con la siguiente 
Descripción del Producto:
------
{product_desc}
------
El mensaje promocional DEBE usar el siguiente formato:
'''
Título: un mensaje poderoso y corto que describa de qué se trata este producto, el objetivo es captar la atención del usuario.
Mensaje: sé creativo con el mensaje promocional, pero hazlo corto y listo para las redes sociales.
Etiquetas: los hashtags que normalmente usarían las personas en las redes sociales.
'''
El objetivo cuando creas estos tipos de post es llamar la atención del usuario que lo lee.
NO proporciones URIs falsas, limitate a crear mensajes atractivos para el consumidor.
¡Comienza!
[/INST]
"""
prompt = PromptTemplate(
input_variables=['product_desc'],
template=prompt_template,
)

# Structured output using LMFE
class StructuredOutput(BaseModel):
    Title: str = Field(description= "Title of the promotion message")
    Message: str = Field(description= "The actual promotion message")
    Tags: List[str] = Field(description= "Hash tags for social media, usually starts with #")

llm_with_output_structure = ChatNVIDIA(model='meta/llama-3.1-405b-instruct', api_key= openai_nvapi_key).with_structured_output(StructuredOutput)

# Build the content_creator agent
content_creator = ( prompt | llm_with_output_structure )
