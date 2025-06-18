import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
import os

# Configuração da página
st.set_page_config(page_title="Calculadora de Juros Compostos", layout="wide")

# Mostrar logo e título da consultoria
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    else:
        st.write("")
with col_titulo:
    st.markdown("<h1 style='color: navy;'>Consultoria Financeira XYZ</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: gray;'>Planeje hoje. Conquiste amanhã.</h4>", unsafe_allow_html=True)

# 1. Texto explicativo no topo
st.info("💡 Esta calculadora simula o crescimento dos seus investimentos com base em aportes mensais, juros compostos e tempo de aplicação.")

# Sidebar - Entrada de dados
st.sidebar.title("🔢 Parâmetros")
valor_inicial = st.sidebar.number_input("Valor inicial (R$)", value=1000.0)
aporte_mensal = st.sidebar.number_input("Aporte mensal (R$)", value=100.0)
taxa_juros = st.sidebar.number_input("Taxa de juros mensal (%)", value=1.0)
periodos = st.sidebar.number_input("Período (meses)", value=24)

# Cálculo principal
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

# 2. Organização por abas
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Resultados", 
    "📈 Gráficos", 
    "📋 Tabela Detalhada", 
    "🧮 Cálculo Inverso (Meta)"
])

with tab1:
    st.subheader("📊 Resultados do Investimento")
    col1, col2, col3 = st.columns(3)
    col1.metric("Valor Final", f"R$ {df['Valor Total'].iloc[-1]:,.2f}")
    col2.metric("Total Aportado", f"R$ {df['Aportes Acumulados'].iloc[-1]:,.2f}")
    col3.metric("Total de Rendimentos", f"R$ {df['Rendimento Acumulado'].iloc[-1]:,.2f}")

with tab2:
    st.subheader("📈 Gráfico de Evolução")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Total"], mode="lines+markers", name="Valor Total"))
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Aportes Acumulados"], mode="lines", name="Aportes"))
    fig.update_layout(title="Evolução dos Investimentos", xaxis_title="Meses", yaxis_title="R$")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("📋 Tabela Detalhada")
    st.dataframe(df, use_container_width=True)

    col_csv, col_pdf, col_xlsx = st.columns(3)

    # CSV
    csv = df.to_csv(index=False).encode('utf-8')
    with col_csv:
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name='simulacao.csv',
            mime='text/csv',
        )

    # Excel (.xlsx)
    from io import BytesIO
    import openpyxl

    output_excel = BytesIO()
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Simulacao')
    output_excel.seek(0)

    with col_xlsx:
        st.download_button(
            label="📊 Baixar Excel (.xlsx)",
            data=output_excel,
            file_name="simulacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # PDF
    from xhtml2pdf import pisa
    from io import StringIO

    def df_to_html_table(dataframe):
        return dataframe.to_html(index=False, border=0)

    def convert_html_to_pdf(html_content):
        pdf_out = BytesIO()
        pisa_status = pisa.CreatePDF(StringIO(html_content), dest=pdf_out)
        if pisa_status.err:
            return None
        pdf_out.seek(0)
        return pdf_out

    html_table = f"""
    <h2>Simulação de Juros Compostos</h2>
    {df_to_html_table(df)}
    """

    pdf_file = convert_html_to_pdf(html_table)

    with col_pdf:
        if pdf_file:
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_file,
                file_name="simulacao.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Erro ao gerar PDF")

with tab4:
    st.subheader("🧮 Quanto devo investir por mês para alcançar minha meta?")
    meta = st.number_input("Meta de valor final (R$)", value=50000.0)
    i_meta = taxa_juros / 100
    n = periodos

    if i_meta > 0:
        fator = ((1 + i_meta) ** n - 1) / i_meta
        aporte_necessario = (meta - valor_inicial * (1 + i_meta) ** n) / fator
        if aporte_necessario < 0:
            st.warning("Com o valor inicial e juros informados, você já atinge a meta sem aporte mensal.")
        else:
            st.success(f"💰 Para alcançar R$ {meta:,.2f} em {n} meses, você deve investir **R$ {aporte_necessario:,.2f}** por mês.")
    else:
        st.error("A taxa de juros precisa ser maior que 0% para esse cálculo.")

# Rodapé
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2025 Consultoria XYZ. Todos os direitos reservados.</p>", unsafe_allow_html=True)
