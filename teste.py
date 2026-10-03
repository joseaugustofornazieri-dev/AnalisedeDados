import pandas as pd
import streamlit as st
import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Produção Empilhadeira",
    layout="wide"
)

st.title("Dashboard de Produção de Empilhadeira")


# ==========================================
# CARREGAR DADOS
# ==========================================

@st.cache_data
def load_data():

    df = pd.read_excel(
        "julho.xlsx",
        header=1
    )

    # Converter data brasileira
    df["DATA_FILTRO"] = pd.to_datetime(
        df["DATA_FILTRO"],
        dayfirst=True,  
        errors="coerce"
    )

    # Garantir que SACAS seja número
    df["SACAS"] = pd.to_numeric(
        df["SACAS"],
        errors="coerce"
    ).fillna(0)



    return df


df = load_data()

data_Inicio = st.date_input(
    "Data início",
    value=datetime.date(2026, 6, 1),
    format="DD/MM/YYYY")


data_Fim = st.date_input(
    "Data fim",
    value=datetime.date(2026, 6, 30),
    format="DD/MM/YYYY"
)


data_inicio = pd.Timestamp(data_Inicio)
data_fim = pd.Timestamp(data_Fim)

data = df[
    (df['DATA_FILTRO'] >= data_inicio) &
    (df['DATA_FILTRO'] <= data_fim)
].copy()

# ==========================================
# FILTRO DE OPERADOR
# ==========================================

operadores = sorted(
    data["OPERADOR"]
    .dropna()
    .unique()
)

operador = st.sidebar.selectbox(
    "Selecione o operador",
    ["TODOS"] + operadores
)

if operador != "TODOS":

    data = data[
        data["OPERADOR"] == operador
    ]


total_sacas = data["SACAS"].sum()

total_operacoes = len(data)

total_remocoes = data[
    data["TIPO_MOV"] == "REMOCAO"
]["SACAS"].sum()

total = total_sacas + total_remocoes


# ==========================================
# MÉTRICAS
# ==========================================

col1, col2, col3 , col4 = st.columns(4)


with col1:

    st.metric(
        "Total de Sacas",
        f"{data['SACAS'].sum():,.0f}"
    )


with col2:

    st.metric(
        "Quantidade de Operações",
        f"{len(data):,.0f}"
    )


with col3:

    peso_remocao = data[
        data["TIPO_MOV"] == "REMOCAO"
    ]["SACAS"].sum()

    st.metric(
        "Remoções",
        f"{peso_remocao:,.0f}"
    )

with col4:

    st.metric(
        "Total de movimentação",
        f"{total:,.0f}"
    )

# =============================
# verificação de balança

balancas = ['BAM01','BAM02','BAM03','BAC01','BAB01','BAA01','BAA02','BAG01','BAF01','BAF02']
balanca = st.selectbox("Selecione a balança",balancas)

filtro_Balanca = data[
    (data['LOCAL_ORIGEM'].str[:5] == balanca)&
    (data['TIPO_MOV'] == 'REMOCAO')
]['SACAS'].sum()

st.metric("Sacas Retiradas",f"{filtro_Balanca:,.0f}")
# =============================

# ==========================================
# CRIAÇÃO DA COLUNA DE HORA
# ==========================================

data["hora"] = data[
    "DATA_MOVIMENTACAO"
].dt.floor("h")


# ==========================================
# SACAS POR HORA
# ==========================================

st.subheader("Quantidade de Sacas por Hora")

sacas_hora = (
    data.groupby("hora")["SACAS"]
    .sum()
)

st.bar_chart(
    sacas_hora
)


# ==========================================
# OPERAÇÕES POR HORA
# ==========================================

st.subheader("Quantidade de Operações por Hora")

operacoes_hora = (
    data.groupby("hora")
    .size()
)

st.line_chart(
    operacoes_hora
)


# ==========================================
# SACAS POR TIPO DE MOVIMENTAÇÃO
# ==========================================

st.subheader("Total de Sacas por Tipo de Movimentação")

sacas_modalidade = (
    data.groupby("TIPO_MOV")["SACAS"]
    .sum()
)

st.bar_chart(
    sacas_modalidade
)


# ==========================================
# TABELA DETALHADA
# ==========================================

st.subheader("Dados Filtrados")

st.dataframe(
    data,
    use_container_width=True
)