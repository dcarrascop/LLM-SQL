import gdown
from sqlalchemy import create_engine, text
import streamlit as st
import pandas as pd
import os

# Descargar el archivo desde Google Drive si no existe
db_file = 'licencias.db'
if not os.path.exists(db_file):
    url = 'https://drive.google.com/uc?id=17bXAOXt6nsP0Ch8KwZISiFK6vN4rvopV'  # Reemplaza con tu enlace de Google Drive
    gdown.download(url, db_file, quiet=False)

# Cargar la base de datos
engine = create_engine(f'sqlite:///{db_file}')

# Ejecutar una consulta básica y mostrar los primeros 5 registros
with engine.connect() as connection:
    try:
        result = connection.execute(text("SELECT * FROM licencias LIMIT 5"))
        # Convertir el resultado a un DataFrame para mostrarlo en Streamlit
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        st.write(df)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
