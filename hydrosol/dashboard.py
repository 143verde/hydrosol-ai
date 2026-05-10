
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Hydrosol AI Dashboard v5.1",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0d2137 100%); }
    h1, h2, h3 { color: #e3f2fd !important; }
    p, span, div { color: #b0bec5; }
</style>
""", unsafe_allow_html=True)

# Imports com try/except
PIPELINE_DISPONIVEL = False
try:
    from pipeline import render_aba_pipeline
    PIPELINE_DISPONIVEL = True
except:
    pass

MARGEM_DISPONIVEL = False
try:
    from calculo_margem import calcular_margem_dna_camburi
    MARGEM_DISPONIVEL = True
except:
    pass

SIMULADOR_DISPONIVEL = False
try:
    from simulador_negociacao import render_simulador
    SIMULADOR_DISPONIVEL = True
except:
    pass

AGENTES_DISPONIVEL = False
try:
    from agentes import render_agentes
    AGENTES_DISPONIVEL = True
except:
    pass

WEBHOOKS_DISPONIVEL = False
try:
    from n8n_webhooks import render_webhooks
    WEBHOOKS_DISPONIVEL = True
except:
    pass

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color: #42a5f5; text-align: center;'>🌊 HYDROSOL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #90a4ae; text-align: center; font-size: 12px;'>AI Dashboard v5.1</p>", unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio("Menu", [
        "🏠 Início",
        "📋 Pipeline de Propostas",
        "🧬 DNA Camburi",
        "💰 Simulador BDI",
        "🤖 Agentes LangGraph",
        "🔗 n8n Webhooks",
        "⚙️ Configurações"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<p style='color: #42a5f5; font-weight: bold;'>Programa Onda Limpa</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #90a4ae; font-size: 11px;'>Sabesp | R$ 1,23 Bi | 49 Unidades</p>", unsafe_allow_html=True)

# Conteúdo
if menu == "🏠 Início":
    st.markdown("<h1 style='text-align: center; color: #42a5f5;'>🌊 Hydrosol AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #90a4ae;'>Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Valor Total", "R$ 1,24B")
    with col2:
        st.metric("Pipeline Ativo", "R$ 1,8B")
    with col3:
        st.metric("Em Execução", "R$ 420M")
    with col4:
        st.metric("Alertas", "3 críticos")

    st.markdown("---")
    st.markdown("### 📋 Etapas do Programa")

    etapas = [
        ("1", "Definição", "✅"), ("2", "Planejamento", "✅"),
        ("3", "Produção", "✅"), ("4", "Instalação", "🟡"),
        ("5", "Riscos", "⚪"), ("6", "Custos", "⚪"),
        ("7", "Cronograma", "⚪"), ("8", "Organização", "⚪"),
        ("9", "Processos", "⚪"), ("10", "Mod. Produção", "⚪"),
        ("11", "Budgeting", "⚪"), ("12", "Status", "⚪"),
        ("13", "Melhorias", "⚪"),
    ]

    cols = st.columns(7)
    for idx, (num, nome, status) in enumerate(etapas):
        with cols[idx % 7]:
            cor = {"✅": "#388e3c", "🟡": "#f9a825", "⚪": "#78909c"}.get(status, "#78909c")
            st.markdown(f"<div style='text-align: center; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.03); border: 2px solid {cor};'><div style='font-size: 20px;'>{status}</div><div style='font-size: 11px; color: #42a5f5;'>{nome}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Grupos por Vazão")

    grupos = [
        ("Micro", "1-5 L/s", "86", "32-35%", "#e3f2fd"),
        ("Pequeno", "8-20 L/s", "66", "29-32%", "#e8f5e9"),
        ("Médio", "25-60 L/s", "25", "26-29%", "#fff3e0"),
        ("Grande", "129-200 L/s", "6", "24-28%", "#fce4ec"),
        ("Magnum", "500-1000 L/s", "5", "20-24%", "#ffebee"),
    ]

    cols = st.columns(5)
    for idx, (nome, vazao, unidades, margem, cor) in enumerate(grupos):
        with cols[idx]:
            st.markdown(f"<div style='padding: 15px; border-radius: 10px; background: {cor};'><h4 style='margin: 0; color: #1565c0;'>{nome}</h4><p style='margin: 5px 0; color: #455a64; font-size: 12px;'>{vazao}</p><p style='margin: 5px 0; color: #37474f; font-weight: bold;'>{unidades} unidades</p><p style='margin: 3px 0; color: #388e3c; font-size: 11px; font-weight: bold;'>Margem: {margem}</p></div>", unsafe_allow_html=True)

elif menu == "📋 Pipeline de Propostas":
    if PIPELINE_DISPONIVEL:
        try:
            render_aba_pipeline()
        except Exception as e:
            st.error(f"Erro no Pipeline: {e}")
    else:
        st.error("Módulo pipeline.py não encontrado.")
        st.info("Faça upload do arquivo pipeline.py na pasta hydrosol/")

elif menu == "🧬 DNA Camburi":
    st.markdown("## 🧬 DNA Camburi")
    if MARGEM_DISPONIVEL:
        try:
            calcular_margem_dna_camburi()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.info("Módulo calculo_margem.py não disponível.")
        vazao = st.slider("Vazão (L/s)", 1, 1000, 57)
        st.metric("Margem Estimada", "25-30%")

elif menu == "💰 Simulador BDI":
    st.markdown("## 💰 Simulador BDI")
    if SIMULADOR_DISPONIVEL:
        try:
            render_simulador()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.info("Módulo simulador_negociacao.py não disponível.")
        custo = st.number_input("Custo (R$M)", 10.0, 500.0, 74.0)
        bdi = st.slider("BDI", 1.0, 2.0, 1.25, 0.01)
        valor = custo * bdi
        st.metric("Valor Venda", f"R$ {valor:.1f}M")

elif menu == "🤖 Agentes LangGraph":
    st.markdown("## 🤖 Agentes LangGraph")
    if AGENTES_DISPONIVEL:
        try:
            render_agentes()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.info("Módulo agentes.py não disponível.")
        agentes = [("🧮", "Agente Margem", "Ativo"), ("⚠️", "Agente Risco", "Ativo"), ("📅", "Agente Cronograma", "Ativo")]
        for emoji, nome, status in agentes:
            st.markdown(f"<div style='padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 8px;'><span style='font-size: 20px;'>{emoji}</span> <b style='color: #e3f2fd;'>{nome}</b> <span style='color: #66bb6a; float: right;'>● {status}</span></div>", unsafe_allow_html=True)

elif menu == "🔗 n8n Webhooks":
    st.markdown("## 🔗 n8n Webhooks")
    if WEBHOOKS_DISPONIVEL:
        try:
            render_webhooks()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.info("Módulo n8n_webhooks.py não disponível.")
        st.markdown("- 📄 Notas Fiscais
- 💬 WhatsApp Alertas
- 📊 Monitoramento
- 📰 Boletim Diário")

elif menu == "⚙️ Configurações":
    st.markdown("## ⚙️ Configurações")
    st.text_input("NOTION_TOKEN", value="secret_xxx", type="password")
    st.text_input("N8N_WEBHOOK_URL", value="https://n8n.hydrosol.ai/webhook/")
    st.markdown("**Versão:** v5.1 | **Stack:** Streamlit + Notion API + n8n + LangGraph")