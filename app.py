import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
import os
from datetime import datetime
import re
from io import BytesIO, StringIO
from xhtml2pdf import pisa

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Juros Compostos", layout="wide")

# --- LOGO E TÍTULOS ---
logo = Image.open("logo.png")
st.image(logo, width=100)

st.markdown("<h1 style='text-align: center; color: navy;'>Francamente Ricas</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Planeje hoje. Conquiste amanhã.</h4>", unsafe_allow_html=True)

# --- SIDEBAR - PARÂMETROS ---
st.sidebar.title("Parâmetros")
valor_inicial = st.sidebar.number_input("Valor inicial (R$)", value=1000.0)
aporte_mensal = st.sidebar.number_input("Aporte mensal (R$)", value=100.0)
taxa_juros = st.sidebar.number_input("Taxa de juros mensal (%)", value=1.0)
periodos = st.sidebar.number_input("Período (meses)", value=24)

# --- CÁLCULO ---
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

# --- MOSTRAR KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Valor Final", f"R$ {df['Valor Total'].iloc[-1]:,.2f}")
col2.metric("Total Aportado", f"R$ {df['Aportes Acumulados'].iloc[-1]:,.2f}")
col3.metric("Total de Rendimentos", f"R$ {df['Rendimento Acumulado'].iloc[-1]:,.2f}")

# --- GRÁFICO ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Total"], mode="lines+markers", name="Valor Total"))
fig.add_trace(go.Scatter(x=df["Mês"], y=df["Aportes Acumulados"], mode="lines", name="Aportes"))
fig.update_layout(title="Evolução dos Investimentos", xaxis_title="Meses", yaxis_title="R$")

st.plotly_chart(fig, use_container_width=True)

# --- FUNÇÕES ÚTEIS PARA EXPORTAÇÃO ---

def df_to_html_table(dataframe):
    return dataframe.to_html(index=False, border=0)

def convert_html_to_pdf(html_content):
    pdf_out = BytesIO()
    pisa_status = pisa.CreatePDF(StringIO(html_content), dest=pdf_out)
    if pisa_status.err:
        return None
    pdf_out.seek(0)
    return pdf_out

# --- FORMATAÇÃO DO PDF ---
html_table = f"""
<h2>Simulação de Juros Compostos</h2>
{df_to_html_table(df)}
"""

pdf_file = convert_html_to_pdf(html_table)

# --- FUNÇÃO DE VALIDAÇÃO DE EMAIL ---
def email_valido(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- CAPTURA E SALVA EMAIL ---
def salvar_email(email):
    try:
        # Cria DataFrame com email e data/hora
        df_email = pd.DataFrame([{
            "email": email,
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        # Se arquivo existir, concatena, senão cria novo
        if os.path.exists("emails_capturados.csv"):
            df_existente = pd.read_csv("emails_capturados.csv")
            df_completo = pd.concat([df_existente, df_email], ignore_index=True)
        else:
            df_completo = df_email

        df_completo.to_csv("emails_capturados.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar o e-mail: {e}")
        return False

# --- SEÇÃO DE COLETA DE EMAIL E LIBERAÇÃO DE DOWNLOADS ---

st.subheader("Informe seu e-mail para ter acesso ao material completo")

email = st.text_input("Digite seu e-mail:")

if email and email_valido(email):
    if st.button("Material completo"):
        sucesso = salvar_email(email)
        if sucesso:
            st.success("Downloads liberados abaixo.")

            # Botões de download liberados só após salvar o email

            # CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name='simulacao.csv',
                mime='text/csv',
            )

            # Excel (.xlsx)
            from io import BytesIO
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Simulacao')
            output_excel.seek(0)

            st.download_button(
                label="📊 Baixar Excel (.xlsx)",
                data=output_excel,
                file_name="simulacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # PDF
            if pdf_file:
                st.download_button(
                    label="📄 Baixar PDF",
                    data=pdf_file,
                    file_name="simulacao.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Erro ao gerar PDF.")
else:
    if email:
        st.warning("⚠️ E-mail inválido. Por favor, verifique o formato.")
    st.info("Por favor, insira um e-mail válido para liberar os downloads.")
