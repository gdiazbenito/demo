from langgraph.graph import END, StateGraph
from typing import TypedDict
from pydantic import BaseModel
from content_creator import content_creator
from digital_artist import digital_artist


# Define la estructura del estado
class StateSchema(TypedDict):
    input_to_agent: str
    agent_choice: str
    agent_use_tool_respond: str


# Clase de estado para el flujo
class State(BaseModel):
    input_to_agent: str
    agent_choice: str = None
    agent_use_tool_respond: str = None

# Asignación del agente
def human_assign_to_agent(state):
    """
    Asigna un agente seleccionado previamente en el estado.
    """
    if not state.agent_choice:
        return {"agent_choice": "content_creator"}
    return {"agent_choice": state.agent_choice}


# Ejecución del agente seleccionado
def agent_execute_task(state):
    """
    Ejecuta la tarea según el agente seleccionado.
    """
    input_to_agent = state.input_to_agent
    choosen_agent = state.agent_choice

    # Ejecuta el agente correspondiente
    if choosen_agent == "content_creator":
        structured_respond = content_creator.invoke({"product_desc": input_to_agent})
        respond = '\n'.join([
            f"**Title:** {structured_respond.Title}",
            f"**Message:** {structured_respond.Message}",
            f"**Tags:** {' '.join(structured_respond.Tags)}"
        ])
    elif choosen_agent == "digital_artist":
        respond = digital_artist.invoke(input_to_agent)
    else:
        respond = "Por favor, seleccione un agente válido: 'ContentCreator' o 'DigitalArtist'."
    
    return {"input_to_agent": input_to_agent, "agent_choice": choosen_agent, "agent_use_tool_respond": respond}


# Define el flujo de trabajo
workflow = StateGraph(State)

# Nodo inicial
workflow.add_node("start", human_assign_to_agent)

# Nodo final
workflow.add_node("end", agent_execute_task)

# Configuración del flujo
workflow.set_entry_point("start")
workflow.add_edge("start", "end")
workflow.add_edge("end", END)

# Compilación del flujo en un Runnable
app = workflow.compile()