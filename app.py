# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import get_data
from datetime import datetime

st.set_page_config(page_title="Faturamento Nacional", layout="wide")

# Estilo da página - fundo grafite escuro e faixa branca no topo
st.markdown("""
    <style>
        body {
            background-color: #1A1F22;
            color: #FFFFFF;
        }
        .block-container {
            background-color: #1A1F22;
        }
        label, h1, h2, h3, h4, h5, h6, div[data-testid="stMarkdownContainer"] {
            color: #FFFFFF;
        }
        .faixa-branca {
            background-color: white;
            padding: 20px 40px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Formatação de moeda brasileira
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Dados
df = get_data()

# Conversão de mês
df['mes_str'] = df['mes'].apply(lambda x: f"{x:02d}")
df['data_faturamento'] = pd.to_datetime(df['data_faturamento'])

# Faixa branca com logo e título centralizados
with st.container():
    st.markdown("""
        <div class="faixa-branca">
            <img src="nacional-escuro.svg" width="120">
            <h1 style="color:#13253D; margin: 0;">FATURAMENTO</h1>
        </div>
    """, unsafe_allow_html=True)

# Filtros de data
col_data1, col_data2 = st.columns(2)
with col_data1:
    data_inicio = st.date_input("Data Inicial", value=pd.to_datetime(df['data_faturamento'].min()).date())
with col_data2:
    data_fim = st.date_input("Data Final", value=pd.to_datetime(df['data_faturamento'].max()).date())

# Filtro por data — corrigido para garantir tipo compatível
data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)
df_filtrado = df[(df['data_faturamento'] >= data_inicio) & (df['data_faturamento'] <= data_fim)]

# Segmento 1 - Faturamento mensal e por operação
st.markdown("### Faturamento Mensal e por Operação")
col1, col2 = st.columns([0.7, 0.3])

with col1:
    faturamento_mensal = df_filtrado.groupby('mes_str')['receita'].sum().reset_index()
    faturamento_mensal['receita_fmt'] = faturamento_mensal['receita'].apply(formatar_moeda)
    fig_mes = px.bar(faturamento_mensal, x='mes_str', y='receita', text='receita_fmt',
                     labels={'mes_str': 'Mês', 'receita': 'Receita'})
    fig_mes.update_traces(marker_color='#13253D', textfont_size=12)
    fig_mes.update_layout(
        showlegend=False, xaxis_title=None, yaxis_title=None,
        margin=dict(t=10, b=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
        height=350,
        plot_bgcolor='white', paper_bgcolor='white',
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                     line=dict(color="#5A7497", width=1))]
    )
    st.plotly_chart(fig_mes, use_container_width=True)

with col2:
    op = df_filtrado.groupby('operacao')['receita'].sum().reset_index().sort_values(by='receita', ascending=True)
    op['receita_fmt'] = op['receita'].apply(formatar_moeda)
    fig_op = px.bar(op, x='receita', y='operacao', orientation='h', text='receita_fmt',
                    labels={'operacao': 'Operação', 'receita': 'Receita'})
    fig_op.update_traces(marker_color='#5A7497', textfont_size=12)
    fig_op.update_layout(
        showlegend=False, xaxis_title=None, yaxis_title=None,
        margin=dict(t=10, b=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
        height=350,
        plot_bgcolor='white', paper_bgcolor='white',
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                     line=dict(color="#13253D", width=1))]
    )
    st.plotly_chart(fig_op, use_container_width=True)

# Segmento 2 - Clientes
st.markdown("### Faturamento por Cliente")
col3, _ = st.columns([0.5, 0.5])

with col3:
    top_clientes = df_filtrado.groupby('parceiro')['receita'].sum().nlargest(10).reset_index()
    top_clientes['receita_fmt'] = top_clientes['receita'].apply(formatar_moeda)
    fig_cli = px.bar(top_clientes, x='receita', y='parceiro', orientation='h', text='receita_fmt',
                     labels={'parceiro': 'Cliente', 'receita': 'Receita'})
    fig_cli.update_traces(marker_color='#13253D')
    fig_cli.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None,
                          margin=dict(t=10, b=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                          height=350,
                          plot_bgcolor='white', paper_bgcolor='white',
                          shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                                       line=dict(color="#5A7497", width=1))])
    st.plotly_chart(fig_cli, use_container_width=True)

# Segmento 3 - Tabela
st.markdown("### Tabela de Vendas")
df_tabela = df_filtrado[['data_faturamento', 'parceiro', 'numero_nf', 'receita']].copy()
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
