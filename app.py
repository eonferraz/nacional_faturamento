import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

st.set_page_config(page_title="Exportar Faturamento", layout="wide")

@st.cache_resource
def carregar_dados():
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=benu.database.windows.net,1433;'
        'DATABASE=benu;'
        'UID=eduardo.ferraz;'
        'PWD=8h!0+a~jL8]B6~^5s5+v'
    )
    conn = pyodbc.connect(conn_str)
    query = "SELECT * FROM nacional_faturamento"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("Exportar Tabela de Faturamento")

df = carregar_dados()
st.dataframe(df, use_container_width=True)

# Botão para exportar para Excel
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Faturamento', index=False)
    writer.save()
    st.download_button(
        label="📥 Baixar Excel",
        data=buffer.getvalue(),
        file_name="faturamento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
