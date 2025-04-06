# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import get_data
from datetime import datetime
import io
import xlsxwriter

st.set_page_config(page_title="Faturamento Nacional", layout="wide", initial_sidebar_state="collapsed")

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
            color: #FFFFFF !important;
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

# Função de formatação monetária brasileira
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Carregamento de dados
df = get_data()
df['mes_str'] = df['mes'].apply(lambda x: f"{x:02d}")
df['data_faturamento'] = pd.to_datetime(df['data_faturamento'])

# Faixa superior branca com logo e título
with st.container():
    st.markdown("""
        <div class="faixa-branca">
            <img src="nacional-escuro.svg" width="120">
            <h1 style="color:#13253D; margin: 0;">FATURAMENTO</h1>
        </div>
    """, unsafe_allow_html=True)

# Filtros na sidebar
with st.sidebar:
    st.markdown("## Filtros")
    ano_atual = datetime.now().year
    data_inicio = st.date_input("Data Inicial", value=datetime(ano_atual, 1, 1).date())
    data_fim = st.date_input("Data Final", value=datetime.today().date())

data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)
df_filtrado = df[(df['data_faturamento'] >= data_inicio) & (df['data_faturamento'] <= data_fim)]

# Faturamento mensal com 12 meses fixos
todos_meses = pd.DataFrame({'mes_str': [f"{i:02d}" for i in range(1, 13)]})
faturamento_mensal = df_filtrado.groupby('mes_str')['receita'].sum().reset_index()
faturamento_mensal = todos_meses.merge(faturamento_mensal, on='mes_str', how='left').fillna(0)
faturamento_mensal['receita_fmt'] = faturamento_mensal['receita'].apply(formatar_moeda)

# Faturamento por operação
op = df_filtrado.groupby('operacao')['receita'].sum().reset_index().sort_values(by='receita', ascending=False)
op['percentual'] = (op['receita'] / op['receita'].sum()) * 100
op['label'] = op.apply(lambda x: f"{x['operacao']} ({formatar_moeda(x['receita'])} - {x['percentual']:.1f}%)", axis=1)

# Gráficos: Faturamento Mensal e por Operação
st.markdown("### Faturamento Mensal e por Operação")
col1, col2 = st.columns([0.7, 0.3])

with col1:
    fig_mes = px.bar(faturamento_mensal, x='mes_str', y='receita', text='receita_fmt')
    fig_mes.update_traces(marker_color='#13253D', textfont_size=12)
    fig_mes.update_layout(showlegend=False, height=350, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_mes, use_container_width=True)

with col2:
    fig_op = px.pie(op, values='receita', names='label', hole=0.4)
    fig_op.update_traces(textinfo='label+percent')
    fig_op.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='white', legend=dict(orientation='h', y=1.1))
    st.plotly_chart(fig_op, use_container_width=True)

# Faturamento por Cliente e Tabela
st.markdown("### Faturamento por Cliente e Tabela de Vendas")
col3, col4 = st.columns(2)

with col3:
    top_clientes = df_filtrado.groupby('parceiro')['receita'].sum().reset_index().sort_values(by='receita', ascending=False).head(10)
    top_clientes['receita_fmt'] = top_clientes['receita'].apply(formatar_moeda)
    fig_cli = px.bar(top_clientes, x='receita', y='parceiro', orientation='h', text='receita_fmt')
    fig_cli.update_traces(marker_color='#13253D')
    fig_cli.update_layout(showlegend=False, height=400, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_cli, use_container_width=True)

with col4:
    st.markdown("**📋 Lista Detalhada de Vendas Faturadas (com destaque por valor)**")
    df_tabela = df_filtrado[['data_faturamento', 'parceiro', 'numero_nf', 'receita']].copy()
    df_tabela = df_tabela.sort_values(by='data_faturamento', ascending=False)
    df_tabela.rename(columns={
        'data_faturamento': 'Data',
        'parceiro': 'Cliente',
        'numero_nf': 'NF',
        'receita': 'Receita'
    }, inplace=True)

    df_tabela_estilo = df_tabela.style.background_gradient(subset=['Receita'], cmap='Reds')
    st.dataframe(df_tabela_estilo, use_container_width=True, hide_index=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_tabela.to_excel(writer, sheet_name='Vendas', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Vendas']
        formato_moeda = workbook.add_format({'num_format': '#.##0,00', 'align': 'right'})
        worksheet.set_column('A:A', 18)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 18, formato_moeda)

    st.download_button(
        label="📥 Exportar para Excel",
        data=output.getvalue(),
        file_name="faturamento_vendas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exportar_excel"
    )

# Rodapé
st.markdown("""
---
<small style='color:#CECECE;'>Dashboard desenvolvido por Paulo Eduardo para Nacional Indústria Mecânica</small>
""", unsafe_allow_html=True)
