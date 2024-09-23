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
