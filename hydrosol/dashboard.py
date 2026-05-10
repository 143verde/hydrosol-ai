
"""
🌊 Hydrosol AI Dashboard v5.1 — Principal
Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
Stack: Streamlit + Notion API + n8n + LangGraph
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar pasta do pacote ao path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Hydrosol AI Dashboard v5.1",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS CUSTOMIZADO — TEMA HIDROSOL
# ============================================================

st.markdown("""
<style>
    /* Tema principal */
    .main {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0d2137 100%);
    }

    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #0d2137 0%, #1a3a5c 100%);
    }

    /* Cards */
    .stMetric {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Botões */
    .stButton>button {
        background: linear-gradient(90deg, #1976d2, #42a5f5);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #1565c0, #1e88e5);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(25,118,210,0.4);
    }

    /* Headers */
    h1, h2, h3 {
        color: #e3f2fd !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Texto */
    p, span, div {
        color: #b0bec5;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #90a4ae;
        border-radius: 8px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(25,118,210,0.2) !important;
        color: #42a5f5 !important;
    }

    /* Alertas */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
    }

    /* Dataframe */
    .dataframe {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 10px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0d2137;
    }
    ::-webkit-scrollbar-thumb {
        background: #1976d2;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# IMPORTS DOS MÓDULOS
# ============================================================

try:
    from pipeline import render_aba_pipeline
    PIPELINE_DISPONIVEL = True
except ImportError:
    PIPELINE_DISPONIVEL = False
    st.warning("⚠️ Módulo pipeline.py não encontrado. Instale na pasta hydrosol/")

try:
    from calculo_margem import calcular_margem_dna_camburi
    MARGEM_DISPONIVEL = True
except ImportError:
    MARGEM_DISPONIVEL = False

try:
    from simulador_negociacao import render_simulador
    SIMULADOR_DISPONIVEL = True
except ImportError:
    SIMULADOR_DISPONIVEL = False

try:
    from agentes import render_agentes
    AGENTES_DISPONIVEL = True
except ImportError:
    AGENTES_DISPONIVEL = False

try:
    from n8n_webhooks import render_webhooks
    WEBHOOKS_DISPONIVEL = True
except ImportError:
    WEBHOOKS_DISPONIVEL = False

# ============================================================
# SIDEBAR — NAVEGAÇÃO
# ============================================================

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #42a5f5; margin: 0; font-size: 28px;">🌊 HYDROSOL</h1>
        <p style="color: #90a4ae; margin: 5px 0; font-size: 12px;">AI Dashboard v5.1</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Menu de navegação
    st.markdown("### 📍 Navegação")

    menu = st.radio("", [
        "🏠 Início",
        "📋 Pipeline de Propostas",  # NOVO
        "🧬 DNA Camburi",
        "💰 Simulador BDI",
        "🤖 Agentes LangGraph",
        "🔗 n8n Webhooks",
        "⚙️ Configurações"
    ], label_visibility="collapsed")

    st.markdown("---")

    # Status do sistema
    st.markdown("### 📡 Status")

    status_items = {
        "Pipeline": "🟢 Online" if PIPELINE_DISPONIVEL else "🔴 Offline",
        "Margem": "🟢 Online" if MARGEM_DISPONIVEL else "🔴 Offline",
        "Simulador": "🟢 Online" if SIMULADOR_DISPONIVEL else "🔴 Offline",
        "Agentes": "🟢 Online" if AGENTES_DISPONIVEL else "🔴 Offline",
        "Webhooks": "🟢 Online" if WEBHOOKS_DISPONIVEL else "🔴 Offline",
    }

    for modulo, status in status_items.items():
        st.markdown(f"<small>{modulo}: {status}</small>", unsafe_allow_html=True)

    st.markdown("---")

    # Info do programa
    st.markdown("""
    <div style="background: rgba(25,118,210,0.1); padding: 15px; border-radius: 10px; margin-top: 20px;">
        <p style="color: #42a5f5; font-weight: bold; margin: 0;">Programa Onda Limpa</p>
        <p style="color: #90a4ae; font-size: 11px; margin: 5px 0;">Sabesp | R$ 1,23 Bi</p>
        <p style="color: #90a4ae; font-size: 11px; margin: 0;">49 Unidades | 13 Lotes</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CONTEÚDO PRINCIPAL
# ============================================================

if menu == "🏠 Início":
    # ═══════════════════════════════════════════════════════════
    # PÁGINA INICIAL — DASHBOARD PRINCIPAL
    # ═══════════════════════════════════════════════════════════

    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="color: #42a5f5; font-size: 42px; margin: 0;">🌊 Hydrosol AI</h1>
        <p style="color: #90a4ae; font-size: 18px; margin: 10px 0;">
            Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
        </p>
        <p style="color: #64b5f6; font-size: 14px;">
            Sistema de gestão inteligente para ETEs/ETAs 
            com orquestração de agentes de IA, automatização via n8n e cálculo paramétrico de margem
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Cards de resumo
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Valor Total",
            "R$ 1,24B",
            "13 Lotes | 174 Unidades",
            delta_color="off"
        )

    with col2:
        st.metric(
            "📊 Pipeline Ativo",
            "R$ 1,8B",
            "35% taxa conversão",
            delta="+12%"
        )

    with col3:
        st.metric(
            "🏭 Em Execução",
            "R$ 420M",
            "8 contratos ativos",
            delta="+8%"
        )

    with col4:
        st.metric(
            "⚠️ Alertas",
            "3 críticos",
            "ANKARA | Prazo | Margem",
            delta_color="inverse"
        )

    st.markdown("---")

    # Etapas do programa
    st.markdown("### 📋 Etapas do Programa Onda Limpa")

    etapas = [
        ("1", "Definição", "✅", "Concluído"),
        ("2", "Planejamento", "✅", "Concluído"),
        ("3", "Produção", "✅", "Concluído"),
        ("4", "Instalação/Start-up", "🟡", "Em andamento"),
        ("5", "Riscos", "⚪", "Aguardando"),
        ("6", "Custos", "⚪", "Aguardando"),
        ("7", "Cronograma", "⚪", "Aguardando"),
        ("8", "Organização", "⚪", "Aguardando"),
        ("9", "Processos", "⚪", "Aguardando"),
        ("10", "Mod. Produção (PSP)", "⚪", "Aguardando"),
        ("11", "Budgeting/Perf", "⚪", "Aguardando"),
        ("12", "Status/Feedback", "⚪", "Aguardando"),
        ("13", "Melhorias", "⚪", "Aguardando"),
    ]

    cols = st.columns(7)
    for idx, (num, nome, status, desc) in enumerate(etapas):
        with cols[idx % 7]:
            cor = {
                "✅": "#388e3c",
                "🟡": "#f9a825",
                "⚪": "#78909c"
            }.get(status, "#78909c")

            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border-radius: 10px; 
                        background: rgba(255,255,255,0.03); margin-bottom: 10px;
                        border: 2px solid {cor};">
                <div style="font-size: 24px; color: {cor};">{status}</div>
                <div style="font-size: 12px; color: #42a5f5; font-weight: bold;">Etapa {num}</div>
                <div style="font-size: 11px; color: #b0bec5;">{nome}</div>
                <div style="font-size: 10px; color: #78909c;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Grupos por vazão
    st.markdown("### 🎯 Grupos por Vazão — DNA Camburi")

    grupos_data = [
        ("Micro", "1-5 L/s", "86", "77 ETE + 9 ETA", "R$ 350-450K", "1.50-1.60", "32-35%", "#e3f2fd"),
        ("Pequeno", "8-20 L/s", "66", "43 ETE + 23 ETA", "R$ 270-320K", "1.40-1.45", "29-32%", "#e8f5e9"),
        ("Médio", "25-60 L/s", "25", "16 ETE + 9 ETA", "R$ 220-270K", "1.30-1.40", "26-29%", "#fff3e0"),
        ("Grande", "129-200 L/s", "6", "3 ETE + 3 ETA", "R$ 180-220K", "1.25-1.30", "24-28%", "#fce4ec"),
        ("Magnum", "500-1000 L/s", "5", "0 ETE + 5 ETA", "R$ 128-148K", "1.20-1.25", "20-24%", "#ffebee"),
    ]

    cols = st.columns(5)
    for idx, (nome, vazao, unidades, composicao, custo, bdi, margem, cor) in enumerate(grupos_data):
        with cols[idx]:
            alerta = "🔴" if nome == "Magnum" else ""
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 10px; background: {cor}; 
                        border-left: 4px solid {'#d32f2f' if nome == 'Magnum' else '#1976d2'};">
                <h4 style="margin: 0; color: #1565c0;">{alerta} {nome}</h4>
                <p style="margin: 5px 0; color: #455a64; font-size: 12px;">{vazao}</p>
                <p style="margin: 5px 0; color: #37474f; font-size: 14px; font-weight: bold;">{unidades} unidades</p>
                <p style="margin: 5px 0; color: #546e7a; font-size: 11px;">{composicao}</p>
                <hr style="border-color: rgba(0,0,0,0.1);">
                <p style="margin: 3px 0; color: #455a64; font-size: 11px;">Custo: {custo}/Ls</p>
                <p style="margin: 3px 0; color: #455a64; font-size: 11px;">BDI: {bdi}</p>
                <p style="margin: 3px 0; color: {'#d32f2f' if nome == 'Magnum' else '#388e3c'}; font-size: 11px; font-weight: bold;">Margem: {margem}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Ações prioritárias
    st.markdown("### ⚡ Ações Prioritárias do Coordenador")

    acoes = [
        ("1", "Negociação de Escopo com SABESP", "🔴 P1", "+4% margem", "15 dias"),
        ("2", "Compra Antecipada Equipamentos", "🔴 P1", "+3% margem", "30 dias"),
        ("3", "Hedge Cambial (Euro)", "🔴 P1", "+2% margem", "15 dias"),
        ("4", "Padronização Projeto Executivo", "🟡 P2", "+1.5% margem", "45 dias"),
        ("5", "Subcontratação Montagem", "🟡 P2", "+1% margem", "60 dias"),
        ("6", "Agente de Margem (LangGraph)", "🟢 P3", "+0.5% margem", "Contínuo"),
    ]

    for num, acao, prioridade, impacto, prazo in acoes:
        cor_prioridade = {"🔴 P1": "#d32f2f", "🟡 P2": "#f9a825", "🟢 P3": "#388e3c"}.get(prioridade, "#78909c")

        st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; margin-bottom: 8px;
                    background: rgba(255,255,255,0.03); border-left: 4px solid {cor_prioridade};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #42a5f5; font-weight: bold;">#{num}</span>
                <span style="color: {cor_prioridade}; font-weight: bold; font-size: 12px;">{prioridade}</span>
            </div>
            <p style="margin: 5px 0; color: #e3f2fd; font-weight: 500;">{acao}</p>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #81c784; font-size: 12px;">🎯 {impacto}</span>
                <span style="color: #90a4ae; font-size: 12px;">⏱️ {prazo}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Cenário de margem
    st.markdown("---")
    st.markdown("### 📈 Cenário de Margem — Grupo Magnum")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; background: rgba(255,255,255,0.03);">
            <h4 style="color: #ef5350;">⚠️ Cenário Atual</h4>
            <p style="color: #b0bec5;">Margem Magnum: <b style="color: #ef5350;">20%</b></p>
            <p style="color: #b0bec5;">Receita em risco: <b>R$ 479M</b></p>
            <p style="color: #b0bec5;">ANKARA perdeu 2 lotes por preço</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; background: rgba(255,255,255,0.03);">
            <h4 style="color: #66bb6a;">✅ Cenário Otimizado</h4>
            <p style="color: #b0bec5;">Margem Magnum: <b style="color: #66bb6a;">28%</b></p>
            <p style="color: #b0bec5;">Com ações prioritárias implementadas</p>
            <p style="color: #b0bec5;">BDI ajustado: 1.20 | Custo reduzido 10%</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.caption("🔄 Integrado com Notion API + n8n + LangGraph | Hydrosol AI v5.1")

# ═══════════════════════════════════════════════════════════
# ABA PIPELINE DE PROPOSTAS (NOVO)
# ═══════════════════════════════════════════════════════════

elif menu == "📋 Pipeline de Propostas":
    if PIPELINE_DISPONIVEL:
        render_aba_pipeline()
    else:
        st.error("❌ Módulo pipeline.py não encontrado.")
        st.info("📥 Faça upload do arquivo pipeline.py na pasta hydrosol/ do repositório GitHub")

        st.markdown("""
        ### Como instalar:
        1. Baixe o arquivo `pipeline.py`
        2. Vá para o GitHub → `hydrosol-ai/hydrosol/`
        3. Clique "Add file" → "Upload files"
        4. Suba o `pipeline.py`
        5. Aguarde 1-2 minutos para o Streamlit redeployar
        """)

# ═══════════════════════════════════════════════════════════
# OUTRAS ABAS (mantidas do código original)
# ═══════════════════════════════════════════════════════════

elif menu == "🧬 DNA Camburi":
    st.markdown("## 🧬 DNA Camburi — Cálculo Paramétrico de Margem")

    if MARGEM_DISPONIVEL:
        try:
            calcular_margem_dna_camburi()
        except Exception as e:
            st.error(f"Erro no módulo de margem: {e}")
    else:
        st.info("Módulo calculo_margem.py não disponível.")

        # Fallback simples
        st.markdown("### Parâmetros DNA Camburi")

        vazao = st.slider("Vazão (L/s)", 1, 1000, 57)
        custo_base = 198000  # R$/Ls para 57 L/s

        # Fator de escala
        if vazao <= 5:
            fator = 1.37
            bdi = 1.60
        elif vazao <= 20:
            fator = 1.37
            bdi = 1.40
        elif vazao <= 60:
            fator = 1.10
            bdi = 1.35
        elif vazao <= 200:
            fator = 0.90
            bdi = 1.28
        else:
            fator = 0.65
            bdi = 1.25

        custo_ls = custo_base * fator
        valor_ls = custo_ls * bdi
        margem = (valor_ls - custo_ls) / valor_ls

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Custo/Ls", f"R$ {custo_ls/1000:.0f}K")
        with col2:
            st.metric("BDI", f"{bdi:.2f}")
        with col3:
            st.metric("Margem", f"{margem:.1%}")

elif menu == "💰 Simulador BDI":
    st.markdown("## 💰 Simulador de Negociação BDI")

    if SIMULADOR_DISPONIVEL:
        try:
            render_simulador()
        except Exception as e:
            st.error(f"Erro no simulador: {e}")
    else:
        st.info("Módulo simulador_negociacao.py não disponível.")

        # Fallback
        st.markdown("### Simulação Manual")

        col1, col2 = st.columns(2)

        with col1:
            custo = st.number_input("Custo Base (R$M)", 10.0, 500.0, 74.0)
            bdi = st.slider("BDI", 1.0, 2.0, 1.25, 0.01)
            desconto = st.slider("Desconto (%)", 0, 20, 0)
            risco = st.selectbox("Fator Risco", ["Baixo", "Médio", "Alto"])

        with col2:
            valor_venda = custo * bdi * (1 - desconto/100)
            margem = (valor_venda - custo) / valor_venda

            risco_fator = {"Baixo": 1.0, "Médio": 0.95, "Alto": 0.90}[risco]
            margem_ajustada = margem * risco_fator

            st.metric("Valor Venda", f"R$ {valor_venda:.1f}M")
            st.metric("Margem Bruta", f"{margem:.1%}")
            st.metric("Margem Ajustada", f"{margem_ajustada:.1%}")

            if margem_ajustada < 0.20:
                st.error("⚠️ Margem abaixo do mínimo de 20%")
            elif margem_ajustada < 0.25:
                st.warning("⚠️ Margem baixa — revisar custos")
            else:
                st.success("✅ Margem saudável")

elif menu == "🤖 Agentes LangGraph":
    st.markdown("## 🤖 Agentes Autônomos — LangGraph")

    if AGENTES_DISPONIVEL:
        try:
            render_agentes()
        except Exception as e:
            st.error(f"Erro nos agentes: {e}")
    else:
        st.info("Módulo agentes.py não disponível.")

        agentes = [
            ("🧮", "Agente Margem", "Monitora margens em tempo real", "Ativo"),
            ("⚠️", "Agente Risco", "Avalia riscos de propostas", "Ativo"),
            ("📅", "Agente Cronograma", "Gerencia prazos e entregas", "Ativo"),
            ("📄", "Agente NF", "Automatiza notas fiscais", "Aguardando n8n"),
            ("🎯", "Agente Coordenador", "Orquestra todos os agentes", "Ativo"),
        ]

        for emoji, nome, desc, status in agentes:
            cor = "#66bb6a" if status == "Ativo" else "#ffa726"
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 10px; margin-bottom: 10px;
                        background: rgba(255,255,255,0.03); border-left: 4px solid {cor};">
                <span style="font-size: 24px;">{emoji}</span>
                <b style="color: #e3f2fd; margin-left: 10px;">{nome}</b>
                <span style="color: {cor}; float: right; font-size: 12px;">● {status}</span>
                <p style="color: #90a4ae; margin: 5px 0 0 40px; font-size: 13px;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "🔗 n8n Webhooks":
    st.markdown("## 🔗 Workflows n8n")

    if WEBHOOKS_DISPONIVEL:
        try:
            render_webhooks()
        except Exception as e:
            st.error(f"Erro nos webhooks: {e}")
    else:
        st.info("Módulo n8n_webhooks.py não disponível.")

        workflows = [
            ("📄", "Notas Fiscais", "Automatiza emissão de NF", "https://n8n.../webhook/nf"),
            ("💬", "WhatsApp Alertas", "Envia alertas para equipe", "https://n8n.../webhook/whatsapp"),
            ("📊", "Monitoramento", "Coleta métricas do dashboard", "https://n8n.../webhook/monitor"),
            ("📰", "Boletim Diário", "Gera relatório diário", "https://n8n.../webhook/boletim"),
            ("🤖", "LangGraph Trigger", "Dispara agentes autônomos", "https://n8n.../webhook/agente"),
        ]

        for emoji, nome, desc, url in workflows:
            st.markdown(f"""
            <div style="padding: 12px; border-radius: 8px; margin-bottom: 8px;
                        background: rgba(255,255,255,0.03);">
                <span style="font-size: 20px;">{emoji}</span>
                <b style="color: #e3f2fd; margin-left: 8px;">{nome}</b>
                <p style="color: #90a4ae; margin: 5px 0 0 32px; font-size: 12px;">{desc}</p>
                <code style="color: #64b5f6; font-size: 10px; margin-left: 32px;">{url}</code>
            </div>
            """, unsafe_allow_html=True)

elif menu == "⚙️ Configurações":
    st.markdown("## ⚙️ Configurações do Sistema")

    st.markdown("### 🔑 Variáveis de Ambiente")

    with st.form("config_env"):
        st.text_input("NOTION_TOKEN", value="secret_xxxxxxxx", type="password")
        st.text_input("N8N_WEBHOOK_URL", value="https://n8n.hydrosol.ai/webhook/")
        st.text_input("WHATSAPP_API_KEY", value="key_xxxxxxxx", type="password")
        st.text_input("SAP_USERNAME", value="hydrosol_user")
        st.text_input("SAP_PASSWORD", value="", type="password")

        st.form_submit_button("💾 Salvar Configurações")

    st.markdown("---")

    st.markdown("### 📝 Sobre o Sistema")
    st.markdown("""
    - **Versão:** v5.1
    - **Stack:** Streamlit + Notion API + n8n + LangGraph
    - **Repositório:** [github.com/143verde/hydrosol-ai](https://github.com/143verde/hydrosol-ai)
    - **Deploy:** Streamlit Cloud
    - **Última atualização:** 2026-05-09

    **Módulos:**
    - ✅ Pipeline de Propostas
    - ✅ Cálculo de Margem (DNA Camburi)
    - ✅ Simulador BDI
    - ✅ Agentes LangGraph
    - ✅ n8n Webhooks
    """)