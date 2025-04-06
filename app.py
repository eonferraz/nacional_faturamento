import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, date
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Faturamento", layout="wide")

# Paleta de cores
cores = {
    "azul_escuro": "#13253D",
    "cinza_claro": "#CECECE",
    "azul_claro": "#5A7497",
    "grafite_escuro": "#1A1F22",
    "verde_claro": "#8FCB9B",
    "vermelho_claro": "#DE3C4B"
}

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {cores['grafite_escuro']};
        }}
        .block-container {{
            background-color: {cores['grafite_escuro']};
        }}
    </style>
""", unsafe_allow_html=True)

# Função para formatar moeda
@st.cache_data
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Conexão com o banco SQL Azure
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
    df['data_faturamento'] = pd.to_datetime(df['data_faturamento'], errors='coerce')
    return df

# Layout superior
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("nacional-escuro.svg", use_container_width=False, width=100)
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: {cores['azul_escuro']};'>FATURAMENTO</h1>", unsafe_allow_html=True)
    with col3:
        df = carregar_dados()
        faturamento_total = df['receita'].sum()
        st.markdown(f"<div style='text-align: right; background-color: white; padding: 10px; border-radius: 10px;'>"
                    f"<span style='font-size: 24px; color: {cores['azul_escuro']};'>"
                    f"{formatar_moeda(faturamento_total)}</span></div>", unsafe_allow_html=True)

# Filtro lateral
with st.sidebar:
    st.markdown("## Filtros")
    data_inicio = st.date_input("Data de início", date(datetime.today().year, 1, 1))
    data_fim = st.date_input("Data de fim", date.today())

df_filtrado = df[(df['data_faturamento'] >= pd.to_datetime(data_inicio)) & (df['data_faturamento'] <= pd.to_datetime(data_fim))]

# Gráfico de faturamento mensal
df_mes = df_filtrado.groupby(['mes', 'operacao'], as_index=False)['receita'].sum()
meses_ordem = list(range(1, 13))
df_mes['mes'] = pd.Categorical(df_mes['mes'], categories=meses_ordem, ordered=True)
df_mes = df_mes.sort_values('mes')
fig_coluna = px.bar(df_mes, x='mes', y='receita', color='operacao', barmode='stack',
                   labels={'mes': 'Mês', 'receita': 'Faturamento'},
                   text_auto='.2s', height=400)
fig_coluna.update_layout(title=None, showlegend=True, legend_orientation='h',
                         plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

# Gráfico de rosca - % por operação
df_pie = df_filtrado.groupby('operacao', as_index=False)['receita'].sum()
df_pie['pct'] = df_pie['receita'] / df_pie['receita'].sum()
df_pie['label'] = df_pie.apply(lambda row: f"{row['operacao']}<br>{formatar_moeda(row['receita'])} ({row['pct']:.1%})", axis=1)
fig_pie = px.pie(df_pie, values='receita', names='label', hole=0.5, height=400)
fig_pie.update_traces(textinfo='none')
fig_pie.update_layout(title=None, showlegend=False)

# Layout da primeira faixa de gráficos
with st.container():
    col1, col2 = st.columns([7, 3])
    with col1:
        st.markdown(f"<h2 style='color:{cores['azul_claro']}'>Faturamento Mensal</h2>", unsafe_allow_html=True)
        st.plotly_chart(fig_coluna, use_container_width=True)
    with col2:
        st.markdown(f"<h2 style='color:{cores['azul_claro']}'>Distribuição por Operação</h2>", unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True)
