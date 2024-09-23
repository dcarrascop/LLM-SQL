import gdown
from sqlalchemy import create_engine, text
import streamlit as st
import pandas as pd
import os

# Descargar el archivo desde Google Drive si no existe
db_file = 'licencias.db'
if not os.path.exists(db_file):
    url = 'https://drive.google.com/uc?id=17bXAOXt6nsP0Ch8KwZISiFK6vN4rvopV'
    gdown.download(url, db_file, quiet=False)

import os

if os.path.exists(db_file):
    st.write(f"Tamaño del archivo: {os.path.getsize(db_file)} bytes")
else:
    st.error("El archivo no existe.")

try:
    engine = create_engine(f'sqlite:///{db_file}')
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        if tables:
            st.write("Tablas disponibles en la base de datos:", tables)
        else:
            st.error("No se encontraron tablas en la base de datos.")
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
