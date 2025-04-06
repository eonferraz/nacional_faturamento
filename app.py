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
    query = """
        SELECT
          numero_nf AS "Número NF",
          data_negociacao AS "Data Negociação",
          data_faturamento AS "Data Faturamento",
          ano_mes AS "Ano-Mês",
          ano AS "Ano",
          mes AS "Mês",
          data_entrada AS "Data Entrada",
          cod_parceiro AS "Código Parceiro",
          cod_projeto AS "Código Projeto",
          abrev_projeto AS "Abrev. Projeto",
          projeto AS "Projeto",
          cnpj AS "CNPJ",
          parceiro AS "Parceiro",
          cod_top AS "Código TOP",
          [top] AS "TOP",
          movimento AS "Movimento",
          cliente AS "Cliente",
          fornecedor AS "Fornecedor",
          codigo AS "Código Produto",
          descricao AS "Descrição",
          ncm AS "NCM",
          grupo AS "Grupo",
          cfop AS "CFOP",
          operacao AS "Operação",
          qtd_negociada AS "Qtd. Negociada",
          qtd_entregue AS "Qtd. Entregue",
          status AS "Status",
          saldo AS "Saldo",
          valor_unitario AS "Valor Unitário",
          valor_total AS "Valor Total",
          valor_icms AS "Valor ICMS",
          valor_ipi AS "Valor IPI",
          receita AS "Receita"
        FROM
          nacional_faturamento;
    """
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

st.download_button(
    label="📥 Baixar Excel",
    data=buffer.getvalue(),
    file_name="faturamento.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
