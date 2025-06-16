import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="Calculadora de Juros Compostos", layout="wide")

# Sidebar - Entrada de dados
st.sidebar.title("Parâmetros")
valor_inicial = st.sidebar.number_input("Valor inicial (R$)", value=1000.0)
aporte_mensal = st.sidebar.number_input("Aporte mensal (R$)", value=100.0)
taxa_juros = st.sidebar.number_input("Taxa de juros mensal (%)", value=1.0)
periodos = st.sidebar.number_input("Período (meses)", value=24)

# Cálculo
i = taxa_juros / 100
dados = []
total = valor_inicial
aporte_acumulado = valor_inicial

for mes in range(1, periodos + 1):
    total = total * (1 + i) + aporte_mensal
    aporte_acumulado += aporte_mensal
    dados.append({
        "Mês": mes,
        "Valor Total": round(total, 2),
        "Aportes Acumulados": round(aporte_acumulado, 2),
        "Rendimento Acumulado": round(total - aporte_acumulado, 2)
    })

df = pd.DataFrame(dados)

# Mostrar KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Valor Final", f"R$ {df['Valor Total'].iloc[-1]:,.2f}")
col2.metric("Total Aportado", f"R$ {df['Aportes Acumulados'].iloc[-1]:,.2f}")
col3.metric("Total de Rendimentos", f"R$ {df['Rendimento Acumulado'].iloc[-1]:,.2f}")

# Gráfico
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Total"], mode="lines+markers", name="Valor Total"))
fig.add_trace(go.Scatter(x=df["Mês"], y=df["Aportes Acumulados"], mode="lines", name="Aportes"))
fig.update_layout(title="Evolução dos Investimentos", xaxis_title="Meses", yaxis_title="R$")

st.plotly_chart(fig, use_container_width=True)

# Tabela detalhada
st.subheader("Tabela Detalhada")
st.dataframe(df, use_container_width=True)
