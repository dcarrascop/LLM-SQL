from sqlalchemy import create_engine, text
import streamlit as st
import pandas as pd

# Crear un motor a una base de datos de prueba
engine = create_engine('sqlite:///chinook.db')  # Archivo de base de datos de ejemplo

# Ejecutar una consulta básica y mostrar los primeros 5 registros de una tabla existente
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM albums LIMIT 5"))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    st.write(df)
