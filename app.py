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

@st.cache_data
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

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

df = carregar_dados()
faturamento_total = df['receita'].sum()

# Faixa superior branca com conteúdo alinhado
st.markdown("""
    <div style='background-color: white; padding: 20px;'>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image("nacional-escuro.svg", use_container_width=False, width=100)
with col2:
    st.markdown(f"<h1 style='text-align: center; color: {cores['azul_escuro']}; margin-top: 10px;'>FATURAMENTO</h1>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='text-align: right; padding: 10px; border-radius: 10px;'>"
                f"<span style='font-size: 24px; color: {cores['azul_escuro']};'>"
                f"{formatar_moeda(faturamento_total)}</span></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Filtros")
    data_inicio = st.date_input("Data de início", date(datetime.today().year, 1, 1))
    data_fim = st.date_input("Data de fim", date.today())

# Filtro por data
df_filtrado = df[(df['data_faturamento'] >= pd.to_datetime(data_inicio)) & (df['data_faturamento'] <= pd.to_datetime(data_fim))]

# Garantir 12 meses sempre no gráfico
meses_ordem = list(range(1, 13))
df_mes = df_filtrado.groupby(['mes', 'operacao'], as_index=False)['receita'].sum()
df_mes['mes'] = df_mes['mes'].fillna(0).astype(int)
operacoes_unicas = df_filtrado['operacao'].dropna().unique().tolist()
df_final = pd.DataFrame()

for op in operacoes_unicas:
    df_temp = df_mes[df_mes['operacao'] == op].copy()
    df_temp = pd.merge(pd.DataFrame({'mes': meses_ordem}), df_temp, on='mes', how='left')
    df_temp['operacao'] = op
    df_temp['receita'] = df_temp['receita'].fillna(0)
    df_final = pd.concat([df_final, df_temp], ignore_index=True)

fig_coluna = px.bar(df_final, x='mes', y='receita', color='operacao', barmode='stack',
                   labels={'mes': 'Mês', 'receita': 'Faturamento'},
                   text_auto='.2s', height=400)
fig_coluna.update_layout(title=None, showlegend=True, legend_orientation='h',
                         plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

# Gráfico de rosca - % por operação
if not df_filtrado.empty and df_filtrado['receita'].sum() > 0:
    df_pie = df_filtrado.groupby('operacao', as_index=False)['receita'].sum()
    df_pie['pct'] = df_pie['receita'] / df_pie['receita'].sum()
    df_pie['label'] = df_pie.apply(
        lambda row: f"{row['operacao']}<br>{formatar_moeda(row['receita'])} ({row['pct']:.1%})" if pd.notnull(row['operacao']) else "Sem operação",
        axis=1
    )
    fig_pie = px.pie(df_pie, values='receita', names='label', hole=0.5, height=400)
    fig_pie.update_traces(textinfo='none')
    fig_pie.update_layout(title=None, showlegend=False)
else:
    fig_pie = px.pie(values=[1], names=['Sem dados'], hole=0.5, height=400)
    fig_pie.update_layout(title=None, showlegend=False)

with st.container():
    col1, col2 = st.columns([7, 3])
    with col1:
        st.markdown("<h2 style='color:white; white-space: nowrap;'>Faturamento Mensal</h2>", unsafe_allow_html=True)
        st.plotly_chart(fig_coluna, use_container_width=True)
    with col2:
        st.markdown("<h2 style='color:white; font-size: 18px; white-space: nowrap;'>Distribuição por operação</h2>", unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True)
