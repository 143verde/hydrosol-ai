import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="Hydrosol AI v5.1", page_icon="🌊", layout="wide")

st.markdown("<style>.main{background:#0a1628;}h1,h2,h3{color:#42a5f5!important;}</style>", unsafe_allow_html=True)

PIPELINE_OK = False
try:
    from pipeline import render_aba_pipeline
    PIPELINE_OK = True
except:
    pass

with st.sidebar:
    st.title("HYDROSOL")
    st.caption("AI Dashboard v5.1")
    menu = st.radio("Menu", [
        "Inicio",
        "Pipeline de Propostas",
        "DNA Camburi",
        "Simulador BDI",
        "Agentes LangGraph",
        "n8n Webhooks",
        "Configuracoes"
    ])

if menu == "Inicio":
    st.title("Hydrosol AI")
    st.write("Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Valor Total", "R$ 1,24B")
    c2.metric("Pipeline", "R$ 1,8B")
    c3.metric("Execucao", "R$ 420M")
    c4.metric("Alertas", "3")

    st.write("Etapas do Programa:")
    etapas = ["Definicao", "Planejamento", "Producao", "Instalacao", "Riscos", "Custos", "Cronograma"]
    for i, e in enumerate(etapas, 1):
        st.write(f"{i}. {e}")

elif menu == "Pipeline de Propostas":
    if PIPELINE_OK:
        render_aba_pipeline()
    else:
        st.error("pipeline.py nao encontrado")

elif menu == "DNA Camburi":
    st.title("DNA Camburi")
    vazao = st.slider("Vazao L/s", 1, 1000, 57)
    st.metric("Margem", "25%")

elif menu == "Simulador BDI":
    st.title("Simulador BDI")
    custo = st.number_input("Custo R$M", 10.0, 500.0, 74.0)
    bdi = st.slider("BDI", 1.0, 2.0, 1.25, 0.01)
    st.metric("Venda", f"R$ {custo*bdi:.1f}M")

elif menu == "Agentes LangGraph":
    st.title("Agentes LangGraph")
    st.write("5 agentes autonomos ativos")

elif menu == "n8n Webhooks":
    st.title("n8n Webhooks")
    st.write("5 workflows configurados")

elif menu == "Configuracoes":
    st.title("Configuracoes")
    st.text_input("NOTION_TOKEN", type="password")