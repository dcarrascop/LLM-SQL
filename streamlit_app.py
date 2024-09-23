import streamlit as st
import requests
import os
from sqlalchemy import create_engine, text
import pandas as pd

# URL to your database file
db_url = 'https://uccl0-my.sharepoint.com/:u:/r/personal/di_carrasco_uc_cl/Documents/licencias.db?csf=1&web=1&e=JhjWnN'
db_file = 'licencias.db'

# Function to download the file
def download_file(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        with open(filename, 'wb') as file:
            file.write(response.content)
        st.success(f"Downloaded {filename} successfully!")
    except Exception as e:
        st.error(f"Error downloading the file: {e}")

# Check if the database file exists, else download it
if not os.path.exists(db_file):
    st.info("Downloading the database file...")
    download_file(db_url, db_file)

# Connect to the SQLite database
if os.path.exists(db_file):
    try:
        engine = create_engine(f'sqlite:///{db_file}')
        st.write(f"Connected to the database {db_file} successfully.")

        # Sample query to show the first 5 records from a table
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM licencias LIMIT 5"))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            st.write(df)
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
else:
    st.error("Database file not found.")
