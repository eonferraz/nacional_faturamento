# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import get_data
from datetime import datetime

st.set_page_config(page_title="Faturamento Nacional", layout="wide")

# Logo e header
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image("nacional-branco.svg", width=140)
with col2:
    st.markdown("""
    <h1 style='color:#13253D; margin-top: 10px;'>FATURAMENTO</h1>
    """, unsafe_allow_html=True)

# Dados
df = get_data()

# Conversão e ordenação
meses = {
    1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06",
    7: "07", 8: "08", 9: "09", 10: "10", 11: "11", 12: "12"
}
df['mes_str'] = df['mes'].map(meses)

# Segmento 1
st.markdown("### Faturamento Mensal e por Operação")
col1, col2 = st.columns(2)

# Gráfico de Faturamento Mensal
with col1:
    faturamento_mensal = df.groupby('mes_str')['receita'].sum().reset_index()
    fig_mes = px.bar(faturamento_mensal, x='mes_str', y='receita',
                    text_auto='.2s',
                    labels={'mes_str': 'Mês', 'receita': 'Receita'},
                    template='simple_white')
    fig_mes.update_traces(marker_color='#13253D', textfont_size=14)
    fig_mes.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None,
                          margin=dict(t=20, b=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_mes, use_container_width=True)

# Gráfico por Operação
with col2:
    op = df.groupby('operacao')['receita'].sum().reset_index().sort_values(by='receita', ascending=False)
    fig_op = px.bar(op, x='operacao', y='receita',
                    labels={'operacao': 'Operação', 'receita': 'Receita'},
                    template='simple_white')
    fig_op.update_traces(marker_color='#5A7497')
    fig_op.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None,
                         margin=dict(t=20, b=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_op, use_container_width=True)

# Segmento 2
st.markdown("### Faturamento por Cliente e Detalhes")
col3, col4 = st.columns(2)

# Top 10 Clientes
with col3:
    top_clientes = df.groupby('parceiro')['receita'].sum().nlargest(10).reset_index()
    fig_cli = px.bar(top_clientes, x='receita', y='parceiro', orientation='h',
                    labels={'parceiro': 'Cliente', 'receita': 'Receita'},
                    template='simple_white')
    fig_cli.update_traces(marker_color='#13253D')
    fig_cli.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None,
                          margin=dict(t=20, b=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_cli, use_container_width=True)

# Segmento 3
st.markdown("### Tabela de Vendas com Heatmap")
df_tabela = df[['data_faturamento', 'parceiro', 'numero_nf', 'receita']].copy()
df_tabela = df_tabela.sort_values(by='data_faturamento', ascending=False)
df_tabela.rename(columns={
    'data_faturamento': 'Data',
    'parceiro': 'Cliente',
    'numero_nf': 'NF',
    'receita': 'Receita'
}, inplace=True)

st.dataframe(
    df_tabela.style.background_gradient(subset=['Receita'], cmap='Reds'),
    use_container_width=True,
    hide_index=True
)  

# Rodapé
st.markdown("""
---
<small style='color:#CECECE;'>Dashboard desenvolvido por Paulo Eduardo para Nacional Indústria Mecânica</small>
""", unsafe_allow_html=True)
