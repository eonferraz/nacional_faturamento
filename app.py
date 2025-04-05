# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import get_data
from datetime import datetime

st.set_page_config(page_title="Faturamento Nacional", layout="wide")

# Formatação de moeda brasileira
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Dados
df = get_data()

# Conversão de mês
meses = {i: f"{i:02d}" for i in range(1, 13)}
df['mes_str'] = df['mes'].map(meses)

# Header com logo, título e filtros
with st.container():
    st.markdown("""
    <div style='background-color:#FFFFFF; padding: 20px 40px; display: flex; align-items: center;'>
        <img src='nacional-escuro.svg' width='120' style='margin-right: 30px;'>
        <div>
            <h1 style='color:#13253D; margin: 0;'>FATURAMENTO</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial", value=df['data_faturamento'].min())
    with col2:
        data_fim = st.date_input("Data Final", value=df['data_faturamento'].max())

# Filtro por data
df = df[(df['data_faturamento'] >= pd.to_datetime(data_inicio)) &
        (df['data_faturamento'] <= pd.to_datetime(data_fim))]

# Segmento 1 - Faturamento mensal e por operação
st.markdown("### Faturamento Mensal e por Operação")
col1, col2 = st.columns([0.7, 0.3])

with col1:
    faturamento_mensal = df.groupby('mes_str')['receita'].sum().reset_index()
    faturamento_mensal['receita_fmt'] = faturamento_mensal['receita'].apply(formatar_moeda)
    fig_mes = px.bar(faturamento_mensal, x='mes_str', y='receita', text='receita_fmt',
                     labels={'mes_str': 'Mês', 'receita': 'Receita'}, template='simple_white')
    fig_mes.update_traces(marker_color='#13253D', textfont_size=12)
    fig_mes.update_layout(
        showlegend=False, xaxis_title=None, yaxis_title=None,
        margin=dict(t=20, b=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#1A1F22'),
    )
    fig_mes.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=30, b=10),
        height=350,
        bargap=0.15,
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                     line=dict(color="#5A7497", width=1))]
    )
    st.plotly_chart(fig_mes, use_container_width=True)

with col2:
    op = df.groupby('operacao')['receita'].sum().reset_index().sort_values(by='receita', ascending=True)
    op['receita_fmt'] = op['receita'].apply(formatar_moeda)
    fig_op = px.bar(op, x='receita', y='operacao', orientation='h', text='receita_fmt',
                    labels={'operacao': 'Operação', 'receita': 'Receita'}, template='simple_white')
    fig_op.update_traces(marker_color='#5A7497', textfont_size=12)
    fig_op.update_layout(
        showlegend=False, xaxis_title=None, yaxis_title=None,
        margin=dict(t=20, b=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
        plot_bgcolor='white', paper_bgcolor='white',
        height=350,
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                     line=dict(color="#13253D", width=1))]
    )
    st.plotly_chart(fig_op, use_container_width=True)

# Segmento 2 - Clientes
st.markdown("### Faturamento por Cliente")
col3, col4 = st.columns(2)

with col3:
    top_clientes = df.groupby('parceiro')['receita'].sum().nlargest(10).reset_index()
    top_clientes['receita_fmt'] = top_clientes['receita'].apply(formatar_moeda)
    fig_cli = px.bar(top_clientes, x='receita', y='parceiro', orientation='h', text='receita_fmt',
                     labels={'parceiro': 'Cliente', 'receita': 'Receita'}, template='simple_white')
    fig_cli.update_traces(marker_color='#13253D')
    fig_cli.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None,
                          margin=dict(t=20, b=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                          height=350,
                          shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                                       line=dict(color="#5A7497", width=1))])
    st.plotly_chart(fig_cli, use_container_width=True)

# Segmento 3 - Tabela
st.markdown("### Tabela de Vendas")
df_tabela = df[['data_faturamento', 'parceiro', 'numero_nf', 'receita']].copy()
df_tabela = df_tabela.sort_values(by='data_faturamento', ascending=False)
df_tabela.rename(columns={
    'data_faturamento': 'Data',
    'parceiro': 'Cliente',
    'numero_nf': 'NF',
    'receita': 'Receita'
}, inplace=True)
df_tabela['Receita'] = df_tabela['Receita'].apply(formatar_moeda)

st.dataframe(df_tabela, use_container_width=True, hide_index=True)

# Rodapé
st.markdown("""
---
<small style='color:#CECECE;'>Dashboard desenvolvido por Paulo Eduardo para Nacional Indústria Mecânica</small>
""", unsafe_allow_html=True)
