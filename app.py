import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard de Faturamento", layout="wide")

# 🔐 Conexão com SQL Server (Azure)
def conectar_sql_server():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=benu.database.windows.net,1433;"
        "DATABASE=benu;"
        "UID=eduardo.ferraz;"
        "PWD=Pam6i8Z9N<;}P?C5;6v7;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    return conn

@st.cache_data(ttl=600)
def carregar_dados():
    conn = conectar_sql_server()
    query = "SELECT * FROM nacional_faturamento"
    df = pd.read_sql(query, conn)
    conn.close()

    # Conversão de datas
    for col in ["data_negociacao", "data_faturamento", "data_entrada"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

# 🎯 Início do app
st.title("📊 Dashboard de Faturamento - Nacional")
df = carregar_dados()

# 📅 Filtros de ano e mês
col1, col2 = st.columns(2)
anos = sorted(df["ano"].dropna().unique(), reverse=True)
meses = sorted(df["mes"].dropna().unique())

ano_selecionado = col1.selectbox("Ano", anos, index=0)
mes_selecionado = col2.selectbox("Mês", meses, index=0)

df_filtrado = df[(df["ano"] == ano_selecionado) & (df["mes"] == mes_selecionado)]

# 📌 Indicadores
st.markdown(f"### 📅 Faturamento de {mes_selecionado:02d}/{ano_selecionado}")
col3, col4, col5 = st.columns(3)
col3.metric("Receita Total", f"R$ {df_filtrado['receita'].sum():,.2f}")
col4.metric("Total de Projetos", df_filtrado["projeto"].nunique())
col5.metric("Parceiros Únicos", df_filtrado["parceiro"].nunique())

# 📊 Gráfico por parceiro
fig_parceiros = px.bar(
    df_filtrado.groupby("parceiro")["receita"].sum().reset_index().sort_values("receita", ascending=False),
    x="parceiro", y="receita", title="Receita por Parceiro", text_auto=".2s"
)
st.plotly_chart(fig_parceiros, use_container_width=True)

# 📄 Tabela detalhada
st.subheader("📄 Detalhamento dos dados")
st.dataframe(df_filtrado)

# 📥 Exportar Excel
def gerar_excel(df):
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Faturamento")
    return output.getvalue()

st.download_button(
    label="📥 Baixar Excel",
    data=gerar_excel(df_filtrado),
    file_name=f"faturamento_{ano_selecionado}_{mes_selecionado}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
