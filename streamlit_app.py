import streamlit as st
from openai import OpenAI

# Show title and description.
st.title('💬 Conversión de Lenguaje Natural a SQL')
st.write(
    "¡Escribe tu consulta aquí!"
)

input_text = st.text_input("Escribe tu consulta en lenguaje natural:")

openai.api_key = st.secrets["openai"]["api_key"]
