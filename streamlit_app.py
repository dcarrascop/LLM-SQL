import streamlit as st
import requests
import os
from sqlalchemy import create_engine
import openai
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.prompts.base import Prompt
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# URL directa de Google Drive para el archivo licencias.db
db_url = "https://drive.google.com/uc?id=17bXAOXt6nsP0Ch8KwZISiFK6vN4rvopV&export=download"
db_path = "licencias.db"

# Descargar el archivo desde Google Drive solo si no existe localmente
if not os.path.exists(db_path):
    st.write("Descargando base de datos...")
    response = requests.get(db_url)
    with open(db_path, 'wb') as f:
        f.write(response.content)
    st.write("Base de datos descargada exitosamente.")

# Crear conexión con la base de datos
engine = create_engine(f'sqlite:///{db_path}')

# Verificar si la tabla 'licencias' existe antes de inicializar SQLDatabase
with engine.connect() as connection:
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    st.write("Tablas en la base de datos:", tables)

# Configurar la clave API de OpenAI desde secrets
openai_api_key = st.secrets["openai"]["api_key"]
openai.api_key = openai_api_key

# Definir el esquema de la base de datos con descripciones de las columnas
schema = """
Tabla: licencias
Columnas:
ID	CAMPO	TIPO DE DATO	DESCRIPCIÓN DEL CAMPO	VALORES POSIBLES
1	CODIGO_ISAPRE	Numérico	Número de identificación de la aseguradora de salud.
2	FECHA_INFORMACION	Texto	Trimestre al que pertenece el registro. Ejemplo: 2024t1.	
3	RUN_TRABAJADOR	Numérico	Rol Único Nacional (RUN) del trabajador (encriptado). Corresponde al afiliado o cotizante.	
4	FECHA_EMISION_LICENCIA	Texto	Fecha de emisión de la licencia médica.	
5	NUMERO_DE_DIAS	Numérico	Número de días asignados en la licencia médica.	
6	FECHA_INICIO_REPOSO	Texto	Fecha de inicio del reposo.	
7	EDAD_TRABAJADOR	Texto	Edad del trabajador en quinquenios.	
8	SEXO_TRABAJADOR	Texto	Género del trabajador.	Masculino, Femenino
9	ACTIVIDAD_LABORAL	Texto	Actividad laboral del trabajador.	Agricultura, servicios agrícolas, silvicultura y pesca; Minas, petróleos y canteras; Industrias manufactureras; Construcción; Electricidad, gas y agua; Comercio; Transporte; y más
10	OCUPACION	Texto	Ocupación del trabajador.	Ejecutivo o Directivo; Profesor; Otro Profesional; Técnico; Vendedor; Administrativo; Operario, Trabajador Manual; Trabajador de Casa Particular; Otro
11	TIPO_DE_LICENCIA	Texto	Tipo de licencia médica.	Enfermedad o accidente común; Prórroga medicina preventiva; Licencia maternal pre y post natal; Enfermedad grave hijo menor de 1 año; Accidente del trabajo o del trayecto; y más
12	CARACTERISTICAS_DEL_REPOSO	Texto	Características del reposo.	Reposo total; Reposo parcial A (mañana); Reposo parcial B (tarde); Reposo parcial C (noche)
13	RUN_PROFESIONAL	Numérico	Rol Único Nacional del profesional (encriptado).	
14	TIPO_PROFESIONAL	Texto	Tipo de profesional.	Médico; Dentista; Matrona
15	TIPO_LICENCIA_SEGUN_CONTRALORIA	Texto	Tipo de licencia según la contraloría.	Enfermedad o accidente común; Prórroga medicina preventiva; Licencia maternal pre y post natal; Enfermedad grave hijo menor de 1 año; Accidente del trabajo o del trayecto; y más
16	NUMERO_DE_DIAS_AUTORIZADOS	Numérico	Número de días autorizados.	
17	DIAGNOSTICO_PRINCIPAL	Texto	Diagnóstico principal.	
18	TIPO_DE_RESOLUCION	Texto	Tipo de resolución.	Autorícese; Rechácese; Amplíese; Redúcese
19	PERIODO	Texto	Periodo de la licencia médica.	Primera; Continuación
20	REPOSO_AUTORIZADO	Texto	Reposo autorizado.	Reposo total; Reposo parcial A (mañana); Reposo parcial B (tarde); Reposo parcial C (noche)
21	DERECHO_A_SUBSIDIO	Texto	Derecho a subsidio.	Con derecho a subsidio (Ley 18.469 o art. 30 Ley 16.744); Con derecho a subsidio de cargo del empleador o entidad responsable (Art. 56 del DS N°3/84); Sin derecho a subsidio
22	FECHA_RECEPCION_ISAPRE	Texto	Fecha de recepción en la isapre.	
23	FECHA_RESOLUCION_ISAPRE	Texto	Fecha de resolución de la isapre.	
24	FECHA_RECEPCION_EMPLEADOR	Texto	Fecha de recepción por el empleador.	
25	REGION	Numérico	Región donde trabaja el empleado.	
26	CALIDAD_TRABAJADOR	Texto	Calidad del trabajador.	Trabajador sector público afecto a Ley 18.834; Trabajador sector público no afecto a Ley 18.834; Trabajador dependiente sector privado; Trabajador independiente
27	ENTIDAD_PAGADORA	Texto	Entidad responsable del pago.	Servicio de salud; Isapre; CCAF; Empleador; Mutual; INP
28	NUMERO_DIAS_A_PAGAR	Numérico	Número total de días con derecho a subsidio que la isapre debe pagar.	
29	MONTO_SUBSIDIO_LIQUIDO	Numérico	Monto total en pesos a pagar al trabajador por concepto de subsidio.	
30	MONTO_APORTE_PREVISIONAL_ISAPRE	Numérico	Monto total en pesos a pagar a la isapre afiliada del trabajador por concepto de cotizaciones de salud.	
31	FECHA_DE_INICIO_DEL_PAGO	Texto	Fecha en que la isapre da inicio al pago previsional.	
32	RECUPERABILIDAD	Texto	Recuperabilidad del trabajador.	Sí; No
33	FECHA_DE_CONCEPCION	Numérico	Fecha de concepción (solo año).	
34	MONTO_APORTE_PREVISIONAL_DE_PENSIONES	Numérico	Monto total en pesos a pagar a las entidades previsionales del trabajador.	
35	OTROS_DIAGNOSTICOS	Texto	Otros diagnósticos según la CIE-10.	
36	RUN_IDENTIFICACION_DEL_HIJO	Numérico	Rol Único Nacional del hijo (encriptado).	
37	LUGAR_DE_REPOSO	Texto	Lugar de reposo.	Su domicilio; Hospital; Otro domicilio; Combinaciones de los valores anteriores
38	CAUSA_RECHAZO_O_MODIFICACION	Texto	Causa de rechazo o modificación.	Reposo injustificado; Diagnóstico irrecuperable; Fuera de plazo; Incumplimiento reposo; Otro
39	NUMERO_DIAS_PREVIOS_AUTORIZADOS	Numérico	Días previos autorizados.
40	FECHA_PRIMERA_AFILIACION_ENTIDAD_PREVISIONAL	Texto	Fecha de primera afiliación a la entidad previsional.
41	FECHA_CONTRATO_DE_TRABAJO	Texto	Fecha del contrato de trabajo.	Se indica el trimestre al que pertenece.
42	MONTO_BASE_CALCULO_SUBSIDIO	Numérico	Monto base de cálculo del subsidio en pesos.
43	RUT_EMPLEADOR	Numérico	Rol Único Tributario (RUT) del empleador (encriptado).
44	FECHA_NACIMIENTO_HIJO	Numérico	Fecha de nacimiento del hijo (solo año).
"""

# Definir ejemplos para few-shot prompting
ejemplos = [
    {
        "input": "¿Cuántos afiliados distintos existen?",
        "sql_cmd": "SELECT COUNT(DISTINCT RUN_TRABAJADOR) AS total_afiliados FROM licencias;",
        "result": "[(184117,)]",
        "answer": "Existen 184,117 afiliados distintos."
    },
    {
        "input": "¿Cuántas licencias médicas fueron emitidas en el trimestre 2024t1?",
        "sql_cmd": "SELECT COUNT(*) AS total_licencias FROM licencias WHERE FECHA_INFORMACION = '2024t1';",
        "result": "[(331076,)]",
        "answer": "En el primer trimestre de 2024, se emitieron un total de 331,076 licencias médicas."
    },
    {
        "input": "¿Cuáles son los primeros 3 diagnósticos con mayor cantidad de licencias? Cuántos afiliados tiene cada diagnóstico?",
        "sql_cmd": "SELECT licencias.DIAGNOSTICO_PRINCIPAL, COUNT(*) AS total_licencias, COUNT(DISTINCT licencias.RUN_TRABAJADOR) AS total_afiliados FROM licencias GROUP BY licencias.DIAGNOSTICO_PRINCIPAL ORDER BY total_licencias DESC LIMIT 3;",
        "result": """
        ('F00-F99', 80380, 43365)
        ('M00-M99', 42513, 28146)
        ('J00-J99', 38683, 32844)""",
        "answer": """Los tres diagnósticos con mayor cantidad de licencias son:

        1. F00-F99: 80,380 licencias y 43.365 afiliados
        2. M00-M99: 42,513 licencias y 28.146 afiliados
        3. J00-J99: 38,683 licencias y 32.844 afiliados"""
    }
]

# Crear el template de prompt para few-shot prompting
few_shot_prompt = "\n".join([
    f"Pregunta: {ejemplo['input']}\nSQLQuery: {ejemplo['sql_cmd']}\nSQLResult: {ejemplo['result']}\nAnswer: {ejemplo['answer']}\n"
    for ejemplo in ejemplos
])

# Crear el template del prompt con los ejemplos añadidos
TEXT_TO_SQL_TMPL = (
    few_shot_prompt +  # Añadir los ejemplos al principio del prompt
    "Dada una pregunta en lenguaje natural, primero crea una consulta en dialecto SQL "
    "sintácticamente correcta para ejecutar, luego observa los resultados de la consulta y devuelve la respuesta. "
    "Puedes ordenar los resultados por una columna relevante para devolver los ejemplos más "
    "interesantes en la base de datos.\n"
    "Nunca consultes todas las columnas de una tabla específica, solo selecciona unas pocas columnas relevantes según la pregunta.\n"
    "Asegúrate de usar solo los nombres de las columnas que se ven en la descripción del esquema. "
    "Ten cuidado de no consultar columnas que no existen. "
    "Presta atención a qué columna está en qué tabla. "
    "Si se pregunta por la cantidad de afiliados o cotizantes, se debe hacer un conteo distinto del campo RUN_TRABAJADOR."
    "Si se pregunta por una fecha específica, se debe usar el campo FECHA_INFORMACION que contiene los trimestres."
    "Si piden la información por edad, ordenar las edades de menor a mayor"
    "Si no se especifica un orden, dejarlo en orden descendente"
    "Si se pide información de una determinada isapre, los CODIGO_ISAPRE corresponden a (67: Colmena Golden Cross S.A.,78: Cruz Blanca S.A.,80: Vida Tres S.A.,81: Nueva Masvida S.A.,99: Banmédica S.A.,107: Consalud S.A.,108: Esencial S.A.,63: Isalud Ltda.,76: Fundación,94: Cruz Del Norte Ltda.)"
    "Para mostrar el nombre de la ISAPRE en vez del código, usa un CASE WHEN o un DECODE en SQL, por ejemplo:\n"
    "CASE\n"
    "    WHEN CODIGO_ISAPRE = 67 THEN 'Colmena Golden Cross S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 78 THEN 'Cruz Blanca S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 80 THEN 'Vida Tres S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 81 THEN 'Nueva Masvida S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 99 THEN 'Banmédica S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 107 THEN 'Consalud S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 108 THEN 'Esencial S.A.'\n"
    "    WHEN CODIGO_ISAPRE = 63 THEN 'Isalud Ltda.'\n"
    "    WHEN CODIGO_ISAPRE = 76 THEN 'Fundación'\n"
    "    WHEN CODIGO_ISAPRE = 94 THEN 'Cruz Del Norte Ltda.'\n"
    "    ELSE 'Desconocido'\n"
    "END AS NOMBRE_ISAPRE\n"
    "Si se pide expresamente el código de la Isapre, usar simplemente CODIGO_ISAPRE."
    "Asegúrate de usar este mapeo cuando se pregunte por los nombres de las ISAPRES en lugar de los códigos.\n"
    "También, califica los nombres de las columnas con el nombre de la tabla cuando sea necesario.\n"
    "Usa el siguiente formato:\n"
    "Pregunta: Aquí la pregunta\n"
    "SQLQuery: Consulta SQL para ejecutar\n"
    "SQLResult: Resultado de la consulta SQL\n"
    "Answer: Respuesta final aquí\n"
    "Usa solo las tablas listadas a continuación.\n"
    "{schema}\n"
    "Pregunta: {query_str}\n"
    "SQLQuery: "
)

# Crear el prompt
TEXT_TO_SQL_PROMPT = Prompt(
    TEXT_TO_SQL_TMPL,
    prompt_type=PromptType.TEXT_TO_SQL,
)

# Configura el LLM y la base de datos
llm = OpenAI(temperature=0.1, model="gpt-4o-mini")
sql_database = SQLDatabase(engine, include_tables=["licencias"])

# Crear el motor de consultas en lenguaje natural
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["licencias"],
    llm=llm,
    text_to_sql_prompt=TEXT_TO_SQL_PROMPT
)

#########SREAMLIT#########

# Interfaz de usuario en Streamlit
st.title('Consulta en Lenguaje Natural a SQL')

# Sección para mostrar información general sobre la base de datos
with st.expander("Descripción de la base de datos y columnas disponibles"):
    st.write("""
    La base de datos contiene información sobre licencias médicas emitidas durante el primer trimestre de 2024. 
    Esta base de datos incluye datos tanto del trabajador como del profesional que emite la licencia, 
    además de detalles sobre el diagnóstico, días autorizados, y más.

    **A continuación se describen las columnas disponibles en la tabla `licencias`:**
    """)
    
    # Descripción de las columnas
    columnas = {
        "CODIGO_ISAPRE": "Número de identificación de la aseguradora de salud.",
        "FECHA_INFORMACION": "Trimestre al que pertenece el registro. Ejemplo: 2024t1.",
        "RUN_TRABAJADOR": "Rol Único Nacional (RUN) del trabajador (encriptado).",
        "FECHA_EMISION_LICENCIA": "Fecha de emisión de la licencia médica.",
        "NUMERO_DE_DIAS": "Número de días asignados en la licencia médica.",
        "FECHA_INICIO_REPOSO": "Fecha de inicio del reposo.",
        "EDAD_TRABAJADOR": "Edad del trabajador en quinquenios.",
        "SEXO_TRABAJADOR": "Género del trabajador (Masculino/Femenino).",
        "ACTIVIDAD_LABORAL": "Actividad laboral del trabajador.",
        "OCUPACION": "Ocupación del trabajador.",
        "TIPO_DE_LICENCIA": "Tipo de licencia médica.",
        "CARACTERISTICAS_DEL_REPOSO": "Características del reposo.",
        "RUN_PROFESIONAL": "Rol Único Nacional del profesional (encriptado).",
        "TIPO_PROFESIONAL": "Tipo de profesional (Medico, Dentista, Matrona).",
        "TIPO_LICENCIA_SEGUN_CONTRALORIA": "Tipo de licencia según la contraloría.",
        "NUMERO_DE_DIAS_AUTORIZADOS": "Número de días autorizados.",
        "DIAGNOSTICO_PRINCIPAL": "Diagnóstico principal.",
        "TIPO_DE_RESOLUCION": "Tipo de resolución (Autoricese, Rechacese, Amplíese, Reducese).",
        "PERIODO": "Periodo (Primera, Continuación).",
        "REPOSO_AUTORIZADO": "Reposo autorizado (Total, Parcial A, Parcial B, Parcial C).",
        "DERECHO_A_SUBSIDIO": "Derecho a subsidio.",
        "FECHA_RECEPCION_ISAPRE": "Fecha de recepción en la isapre.",
        "FECHA_RESOLUCION_ISAPRE": "Fecha de resolución de la isapre.",
        "FECHA_RECEPCION_EMPLEADOR": "Fecha de recepción por el empleador.",
        "REGION": "Región donde trabaja el empleado.",
        "CALIDAD_TRABAJADOR": "Calidad del trabajador.",
        "ENTIDAD_PAGADORA": "Entidad responsable del pago.",
        "NUMERO_DIAS_A_PAGAR": "Número total de días con derecho a subsidio.",
        "MONTO_SUBSIDIO_LIQUIDO": "Monto total en pesos a pagar al trabajador por subsidio.",
        "MONTO_APORTE_PREVISIONAL_ISAPRE": "Monto total en pesos a pagar a la isapre.",
        "FECHA_DE_INICIO_DEL_PAGO": "Fecha de inicio del pago previsional.",
        "RECUPERABILIDAD": "Recuperabilidad (Si/No).",
        "FECHA_DE_CONCEPCION": "Fecha de concepción (solo año).",
        "MONTO_APORTE_PREVISIONAL_DE_PENSIONES": "Monto total en pesos a pagar a las entidades previsionales.",
        "OTROS_DIAGNOSTICOS": "Otros diagnósticos según la CIE-10.",
        "RUN_IDENTIFICACION_DEL_HIJO": "Rol Único Nacional del hijo (encriptado).",
        "LUGAR_DE_REPOSO": "Lugar de reposo.",
        "CAUSA_RECHAZO_O_MODIFICACION": "Causa de rechazo o modificación.",
        "NUMERO_DIAS_PREVIOS_AUTORIZADOS": "Días previos autorizados.",
        "FECHA_PRIMERA_AFILIACION_ENTIDAD_PREVISIONAL": "Fecha de primera afiliación a la entidad previsional.",
        "FECHA_CONTRATO_DE_TRABAJO": "Fecha del contrato de trabajo.",
        "MONTO_BASE_CALCULO_SUBSIDIO": "Monto base de cálculo del subsidio.",
        "RUT_EMPLEADOR": "Rol Único Tributario (RUT) del empleador (encriptado).",
        "FECHA_NACIMIENTO_HIJO": "Fecha de nacimiento del hijo (solo año)."
    }

    # Mostrar las columnas en un formato más ordenado
    for columna, descripcion in columnas.items():
        st.write(f"**{columna}**: {descripcion}")

# Lista de tipos de licencia disponibles
tipos_de_licencia = [
    "Accidente del Trabajo",
    "Enf. Hijo Menor",
    "Enf. o Acc. no del Trabajo",
    "Enfermedad Profesional",
    "Licencia Maternal",
    "Patologia del Embarazo",
    "Prorroga Medicina Preventiva",
    "Licencia maternal pre y post natal"
]

# Ejemplos de consultas predefinidas
ejemplos_consultas = [
    "¿Cuántos afiliados distintos existen?",
    "¿Cuántas licencias médicas fueron emitidas en el primer trimestre del 2024?",
    "¿Cuáles son los primeros 3 diagnósticos con mayor cantidad de licencias?"
]

# Multiselect para seleccionar uno o más tipos de licencia médica
tipos_seleccionados = st.multiselect(
    "Selecciona uno o más tipos de licencia médica (opcional):",
    tipos_de_licencia,
    placeholder="Selecciona una opción"
)

# Selectbox para elegir un ejemplo de consulta
opcion = st.selectbox("Selecciona un ejemplo de consulta o escribe la tuya propia:", ["Escribir mi propia consulta"] + ejemplos_consultas)

# Crear formulario para la pregunta en lenguaje natural
with st.form(key='consulta_form'):
    # Si el usuario elige "Escribir mi propia consulta", mostrar el input
    if opcion == "Escribir mi propia consulta":
        query_str = st.text_input("Escribe tu consulta en lenguaje natural:")
    else:
        query_str = opcion  # Si selecciona un ejemplo, usamos ese ejemplo como la consulta

    # Crear dos columnas para alinear el botón de generar y el botón CLEAR
    col1, col2 = st.columns([2, 1])

    # Botón para generar y ejecutar la consulta en la primera columna
    with col1:
        submit_button = st.form_submit_button(label="Generar y Ejecutar Consulta")
    
    # Botón para limpiar la selección en la segunda columna
    with col2:
        clear_button = st.form_submit_button(label="CLEAR")

# Inicializar el estado de la sesión para almacenar los resultados
if 'sql_query' not in st.session_state:
    st.session_state.sql_query = None
if 'response' not in st.session_state:
    st.session_state.response = None

# Lógica para incorporar los tipos de licencia seleccionados en la consulta
if submit_button:
    if query_str:
        # Si se seleccionaron uno o más tipos de licencia, los incorporamos en la consulta
        if tipos_seleccionados:
            tipos_seleccionados_str = ", ".join([f"'{tipo}'" for tipo in tipos_seleccionados])
            query_str += f" para los tipos de licencia {tipos_seleccionados_str}"
        
        # Ejecutar la consulta (asumiendo que query_engine ya está configurado)
        response = query_engine.query(query_str)
        sql_query = response.metadata.get('sql_query', 'No se encontró la consulta SQL')

        # Almacenar la consulta y el resultado en el estado de la sesión
        st.session_state.response = response
        st.session_state.sql_query = sql_query
    else:
        st.error("Por favor, ingresa una pregunta.")

# Limpiar la selección si se presiona el botón CLEAR
if clear_button:
    st.session_state.sql_query = None
    st.session_state.response = None

# Mostrar el resultado si existe en el estado de la sesión
if st.session_state.response:
    st.write("Resultado de la consulta:")
    st.code(st.session_state.response)

# Mostrar la consulta SQL generada solo si el checkbox está activado y si hay una consulta almacenada
mostrar_sql = st.checkbox("Mostrar consulta SQL generada", value=False)
if mostrar_sql and st.session_state.sql_query:
    st.write("Consulta SQL generada:")
    st.code(st.session_state.sql_query)
