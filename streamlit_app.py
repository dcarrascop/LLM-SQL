import streamlit as st
import sqlite3
import requests
import os
import pandas as pd

# Database URL and local file path
db_url = 'https://uccl0-my.sharepoint.com/:u:/r/personal/di_carrasco_uc_cl/Documents/licencias.db?csf=1&web=1&e=JhjWnN'
db_file = 'licencias.db'

# Function to download the SQLite database
def download_file(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        st.success(f"Database file {filename} downloaded successfully.")
    except Exception as e:
        st.error(f"Error downloading the file: {e}")

# Download the database if it doesn't exist
if not os.path.exists(db_file):
    st.info("Downloading database...")
    download_file(db_url, db_file)

# Function to create a connection to SQLite
@st.cache_resource  # Cache the connection
def init_connection():
    return sqlite3.connect(db_file)

# Initialize the connection
conn = init_connection()

# Function to run a SQL query
@st.cache_data  # Cache the results
def run_query(query):
    df = pd.read_sql_query(query, conn)
    return df

# Test Query
query = "SELECT * FROM licencias LIMIT 5"

# Display data
try:
    st.write("Running query...")
    df = run_query(query)
    st.dataframe(df)
except Exception as e:
    st.error(f"Error executing the query: {e}")

# Close the connection (optional)
# conn.close()
