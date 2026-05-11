import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# IMPORTAR MÓDULOS ADICIONAIS
# ============================================================
try:
    from relatorio_dashboard import gerar_relatorio_pipeline_pdf
except ImportError:
    def gerar_relatorio_pipeline_pdf(dados, periodo="Mensal"):
        return "<html><body><h1>Relatório não disponível</h1></body></html>"

try:
    from proposta_valor import render_aba_proposta_valor
    PROPOSTA_OK = True
except ImportError:
    PROPOSTA_OK = False

st.set_page_config(page_title="Hydrosol AI v5.1", page_icon="🌊", layout="wide")

st.markdown("", unsafe_allow_html=True)

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
        "Proposta de Valor",
        "DNA Camburi",
        "Simulador BDI",
        "Agentes LangGraph",
        "n8n Webhooks",
        "Configuracoes"
    ])

if menu == "Inicio":
    st.title("Hydrosol AI")
    st.write("Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades")

    # ============================================================
    # BOTÃO GERAR RELATÓRIO PDF - INÍCIO
    # ============================================================
    st.markdown("---")
    col_pdf1, col_pdf2 = st.columns([1, 4])
    with col_pdf1:
        if st.button("📥 Gerar Relatório PDF", type="primary", use_container_width=True):
            with st.spinner("Gerando relatório..."):
                dados_pipeline = [
                    {"id": "ETA-1000-01", "nome": "ETA Rio Grande", "consorcio": "ANKARA", "status": "Simulada", "vazao": "1000 L/s", "bdi": "1.25", "margem": 20, "valor": 5000000, "custo": 128500000, "data_envio": "2026-05-01"},
                    {"id": "ETA-1000-02", "nome": "ETA Vale do Sol", "consorcio": "ANKARA", "status": "Simulada", "vazao": "1000 L/s", "bdi": "1.20", "margem": 22, "valor": 5000000, "custo": 128500000, "data_envio": "2026-05-01"},
                    {"id": "ETE-150-02", "nome": "ETE Zona Sul", "consorcio": "MAGNUS", "status": "Enviada", "vazao": "150 L/s", "bdi": "1.30", "margem": 26, "valor": 37000000, "custo": 28500000, "data_envio": "2026-05-01"},
                    {"id": "ETE-200-02", "nome": "ETE Zona Leste", "consorcio": "MAGNUS", "status": "Enviada", "vazao": "200 L/s", "bdi": "1.30", "margem": 26, "valor": 49000000, "custo": 38000000, "data_envio": "2026-04-01"},
                    {"id": "ETA-500-01", "nome": "ETA Camburi Norte", "consorcio": "TRAIL", "status": "Negociando", "vazao": "500 L/s", "bdi": "1.25", "margem": 20, "valor": 92500000, "custo": 74000000, "data_envio": "2026-04-15"},
                    {"id": "ETA-129-01", "nome": "ETA Litoral Norte", "consorcio": "HYDROSOL", "status": "Negociando", "vazao": "129 L/s", "bdi": "1.30", "margem": 28, "valor": 28000000, "custo": 22000000, "data_envio": "2026-04-01"},
                ]

                html_relatorio = gerar_relatorio_pipeline_pdf(dados_pipeline, periodo="Mensal")
                st.download_button(
                    label="⬇️ Baixar Relatório HTML",
                    data=html_relatorio,
                    file_name=f"relatorio_pipeline_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                st.success("✅ Relatório gerado! Baixe acima.")

    with col_pdf2:
        st.info("💡 Baixe o HTML e use Ctrl+P → 'Salvar como PDF'. Funciona no PC e celular!")
    st.markdown("---")
    # ============================================================
    # BOTÃO GERAR RELATÓRIO PDF - FIM
    # ============================================================

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
    # ============================================================
    # BOTÃO GERAR RELATÓRIO PDF - PIPELINE
    # ============================================================
    st.markdown("---")
    col_pdf1, col_pdf2 = st.columns([1, 4])
    with col_pdf1:
        if st.button("📥 Gerar Relatório PDF", type="primary", use_container_width=True, key="btn_pdf_pipeline"):
            with st.spinner("Gerando relatório..."):
                dados_pipeline = [
                    {"id": "ETA-1000-01", "nome": "ETA Rio Grande", "consorcio": "ANKARA", "status": "Simulada", "vazao": "1000 L/s", "bdi": "1.25", "margem": 20, "valor": 5000000, "custo": 128500000, "data_envio": "2026-05-01"},
                    {"id": "ETA-1000-02", "nome": "ETA Vale do Sol", "consorcio": "ANKARA", "status": "Simulada", "vazao": "1000 L/s", "bdi": "1.20", "margem": 22, "valor": 5000000, "custo": 128500000, "data_envio": "2026-05-01"},
                    {"id": "ETE-150-02", "nome": "ETE Zona Sul", "consorcio": "MAGNUS", "status": "Enviada", "vazao": "150 L/s", "bdi": "1.30", "margem": 26, "valor": 37000000, "custo": 28500000, "data_envio": "2026-05-01"},
                    {"id": "ETE-200-02", "nome": "ETE Zona Leste", "consorcio": "MAGNUS", "status": "Enviada", "vazao": "200 L/s", "bdi": "1.30", "margem": 26, "valor": 49000000, "custo": 38000000, "data_envio": "2026-04-01"},
                    {"id": "ETA-500-01", "nome": "ETA Camburi Norte", "consorcio": "TRAIL", "status": "Negociando", "vazao": "500 L/s", "bdi": "1.25", "margem": 20, "valor": 92500000, "custo": 74000000, "data_envio": "2026-04-15"},
                    {"id": "ETA-129-01", "nome": "ETA Litoral Norte", "consorcio": "HYDROSOL", "status": "Negociando", "vazao": "129 L/s", "bdi": "1.30", "margem": 28, "valor": 28000000, "custo": 22000000, "data_envio": "2026-04-01"},
                ]

                html_relatorio = gerar_relatorio_pipeline_pdf(dados_pipeline, periodo="Mensal")
                st.download_button(
                    label="⬇️ Baixar Relatório HTML",
                    data=html_relatorio,
                    file_name=f"relatorio_pipeline_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True,
                    key="download_pipeline"
                )
                st.success("✅ Relatório gerado! Baixe acima.")

    with col_pdf2:
        st.info("💡 Baixe o HTML e use Ctrl+P → 'Salvar como PDF'. Funciona no PC e celular!")
    st.markdown("---")
    # ============================================================
    # BOTÃO GERAR RELATÓRIO PDF - FIM
    # ============================================================

    if PIPELINE_OK:
        render_aba_pipeline()
    else:
        st.error("pipeline.py nao encontrado")

# ============================================================
# NOVA ABA: PROPOSTA DE VALOR
# ============================================================
elif menu == "Proposta de Valor":
    if PROPOSTA_OK:
        render_aba_proposta_valor()
    else:
        st.error("proposta_valor.py nao encontrado. Verifique se o arquivo está na pasta hydrosol.")
        st.info("💡 Dica: Suba o arquivo proposta_valor.py no GitHub e faça reboot no Streamlit Cloud.")

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