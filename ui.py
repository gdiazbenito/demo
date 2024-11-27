import streamlit as st
from human_streamlit import app, State

# Configuración inicial de la interfaz
st.set_page_config(page_title="Social Media Post", layout="wide")

# Título y descripción
st.title("Social Media Posts AI Generator")
st.markdown("""
Esta aplicación permite utilizar agentes AI para generar contenido promocional y arte digital.
Seleccione un agente y proporcione los datos necesarios para ejecutar las tareas.
""")

# Entrada del usuario
with st.sidebar:
    st.header("Entrada del Usuario")
    user_input = st.text_area("Proporcione una descripción del producto o tarea:", "")
    if user_input:
        st.success("Entrada capturada correctamente.")

# Opciones de agente
st.sidebar.header("Selecciona un Agente")
selected_agent = st.radio(
    "*Seleccione el agente que desea utilizar:*",
    ["content_creator", "digital_artist"],
    index=0
)

# Botón para ejecutar el flujo
if st.sidebar.button("Ejecutar flujo"):
    if not user_input:
        st.error("Debe ingresar una descripción antes de ejecutar el flujo.")
    else:
        # Definimos el estado inicial para el flujo
        initial_state = State(
            input_to_agent=user_input,
            agent_choice=selected_agent,
            agent_use_tool_respond=""
        )
        
        # Ejecutamos el flujo
        with st.spinner("Ejecutando el flujo..."):
            try:
                final_state = app.invoke(initial_state)
                st.success("Flujo ejecutado con éxito.")

                # Mostrar resultados
                st.subheader("Resultados")
                st.markdown(f"**Agente Seleccionado:** {final_state.get("agent_choice")}")
                if selected_agent == "digital_artist":
                    image_stream = final_state.get("agent_use_tool_respond")
                    if image_stream:
                        st.image(image_stream, caption= "Imagen Generada", use_container_width=True)
                    else:
                        st.error("No se ha conseguido generar la imagen. Prueba otra vez!")
                else:
                    st.markdown(f"**Respuesta:**\n{final_state.get("agent_use_tool_respond")}")
            except Exception as e:
                st.error(f"Se produjo un error: {e}")

# Nota adicional
st.markdown("""
---
*Contenido generado por IA.*
""")

def add_footer():
    st.markdown(
        """
        <style>
        footer {
            visibility: hidden;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f1f1f1;
            padding: 10px 10px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        </style>
        <div class="footer">
            © footer.
        </div>
        """,
        unsafe_allow_html=True,
    )

# 2024 Deloitte AI Framework | Proprietary Content. All rights reserved

add_footer()
