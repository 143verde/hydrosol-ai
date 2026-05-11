"""
🗓️ Calendário de Ações - Hydrosol AI v5.1
Gerenciamento de Lotes e Ações por Consórcio/Sabesp
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="📅 Calendário de Ações - Hydrosol",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS PERSONALIZADO
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4A6FA5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .acao-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .acao-atrasada {
        border-left-color: #e74c3c !important;
        background: #fff5f5 !important;
    }
    .acao-hoje {
        border-left-color: #f39c12 !important;
        background: #fffbeb !important;
    }
    .acao-futura {
        border-left-color: #27ae60 !important;
        background: #f0fff4 !important;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-atrasada { background: #fee2e2; color: #991b1b; }
    .badge-hoje { background: #fef3c7; color: #92400e; }
    .badge-futura { background: #d1fae5; color: #065f46; }
    .badge-concluida { background: #dbeafe; color: #1e40af; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #f1f5f9;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #667eea !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DADOS DE EXEMPLO (Lotes Sabesp)
# ============================================================
@st.cache_data
def carregar_dados():
    """Carrega dados de lotes e ações"""

    # Lotes atuais da Sabesp
    lotes = [
        {
            "id": "LOTE-001",
            "nome": "Lote 1 - Sistema de Esgoto",
            "consorcio": "Consórcio Engeform",
            "sabesp_id": "SAB-2024-001",
            "tipo": "ETE + Redes",
            "vazao": "500 L/s",
            "valor": 4500000,
            "prazo_entrega": "2025-03-15",
            "status": "Em Execução",
            "progresso": 65,
            "responsavel": "MC",
            "contato": "engeform@sabesp.com.br",
            "local": "ETE Camburi - São Paulo",
            "etapas_concluidas": 8,
            "etapas_total": 13
        },
        {
            "id": "LOTE-002",
            "nome": "Lote 2 - ETA Metropolitana",
            "consorcio": "Consórcio Azevedo Travassos",
            "sabesp_id": "SAB-2024-002",
            "tipo": "ETA",
            "vazao": "1000 L/s",
            "valor": 8200000,
            "prazo_entrega": "2025-06-30",
            "status": "Prospecção",
            "progresso": 15,
            "responsavel": "MC",
            "contato": "azevedo@sabesp.com.br",
            "local": "ETA Metropolitana - São Paulo",
            "etapas_concluidas": 2,
            "etapas_total": 13
        },
        {
            "id": "LOTE-003",
            "nome": "Lote 3 - Sistema Completo",
            "consorcio": "Consórcio Andrade Gutierrez",
            "sabesp_id": "SAB-2024-003",
            "tipo": "ETE + ETA + Redes",
            "vazao": "750 L/s",
            "valor": 12000000,
            "prazo_entrega": "2025-09-20",
            "status": "Negociação",
            "progresso": 35,
            "responsavel": "MC",
            "contato": "andrade@sabesp.com.br",
            "local": "Sistema Completo - Guarulhos",
            "etapas_concluidas": 4,
            "etapas_total": 13
        },
        {
            "id": "LOTE-004",
            "nome": "Lote 4 - Expansão ETE",
            "consorcio": "Consórcio Camargo Corrêa",
            "sabesp_id": "SAB-2024-004",
            "tipo": "ETE",
            "vazao": "300 L/s",
            "valor": 2800000,
            "prazo_entrega": "2025-01-30",
            "status": "Em Execução",
            "progresso": 80,
            "responsavel": "MC",
            "contato": "camargo@sabesp.com.br",
            "local": "ETE Expansão - Osasco",
            "etapas_concluidas": 10,
            "etapas_total": 13
        }
    ]

    # Ações por lote
    acoes = [
        # LOTE-001 - Engeform
        {"id": "A001", "lote_id": "LOTE-001", "lote_nome": "Lote 1 - Sistema de Esgoto", "consorcio": "Consórcio Engeform", "tipo": "📋", "descricao": "Reunião de alinhamento técnico - ETE Camburi", "data": "2024-12-20", "status": "Concluída", "prioridade": "Alta", "responsavel": "MC", "observacao": "Aprovado layout preliminar"},
        {"id": "A002", "lote_id": "LOTE-001", "lote_nome": "Lote 1 - Sistema de Esgoto", "consorcio": "Consórcio Engeform", "tipo": "📐", "descricao": "Entrega projeto executivo - Tanques e tubulações", "data": "2025-01-15", "status": "Pendente", "prioridade": "Alta", "responsavel": "Equipe Técnica", "observacao": "Aguardando aprovação Sabesp"},
        {"id": "A003", "lote_id": "LOTE-001", "lote_nome": "Lote 1 - Sistema de Esgoto", "consorcio": "Consórcio Engeform", "tipo": "🏭", "descricao": "Início fabricação tanques PRFV", "data": "2025-02-01", "status": "Pendente", "prioridade": "Alta", "responsavel": "Fornecedor", "observacao": "Prazo crítico"},
        {"id": "A004", "lote_id": "LOTE-001", "lote_nome": "Lote 1 - Sistema de Esgoto", "consorcio": "Consórcio Engeform", "tipo": "🔧", "descricao": "Instalação equipamentos - Fase 1", "data": "2025-02-20", "status": "Pendente", "prioridade": "Média", "responsavel": "Equipe Campo", "observacao": ""},
        {"id": "A005", "lote_id": "LOTE-001", "lote_nome": "Lote 1 - Sistema de Esgoto", "consorcio": "Consórcio Engeform", "tipo": "✅", "descricao": "Testes hidráulicos e commissioning", "data": "2025-03-10", "status": "Pendente", "prioridade": "Alta", "responsavel": "MC + Equipe", "observacao": "Finalização"},

        # LOTE-002 - Azevedo Travassos
        {"id": "A006", "lote_id": "LOTE-002", "lote_nome": "Lote 2 - ETA Metropolitana", "consorcio": "Consórcio Azevedo Travassos", "tipo": "💰", "descricao": "Apresentação proposta comercial - ETA 1000 L/s", "data": "2024-12-18", "status": "Concluída", "prioridade": "Alta", "responsavel": "MC", "observacao": "Proposta enviada R$ 8.2M"},
        {"id": "A007", "lote_id": "LOTE-002", "lote_nome": "Lote 2 - ETA Metropolitana", "consorcio": "Consórcio Azevedo Travassos", "tipo": "📊", "descricao": "Análise viabilidade técnica - ETA Metropolitana", "data": "2025-01-10", "status": "Pendente", "prioridade": "Alta", "responsavel": "Engenharia", "observacao": "Estudo de terreno"},
        {"id": "A008", "lote_id": "LOTE-002", "lote_nome": "Lote 2 - ETA Metropolitana", "consorcio": "Consórcio Azevedo Travassos", "tipo": "🤝", "descricao": "Negociação contratual - Reunião diretoria", "data": "2025-01-25", "status": "Pendente", "prioridade": "Alta", "responsavel": "MC", "observacao": "Aguardando posição consórcio"},

        # LOTE-003 - Andrade Gutierrez
        {"id": "A009", "lote_id": "LOTE-003", "lote_nome": "Lote 3 - Sistema Completo", "consorcio": "Consórcio Andrade Gutierrez", "tipo": "📋", "descricao": "Reunião kick-off - Sistema Completo Guarulhos", "data": "2024-12-10", "status": "Concluída", "prioridade": "Alta", "responsavel": "MC", "observacao": "Escopo definido"},
        {"id": "A010", "lote_id": "LOTE-003", "lote_nome": "Lote 3 - Sistema Completo", "consorcio": "Consórcio Andrade Gutierrez", "tipo": "📐", "descricao": "Entrega projeto básico - ETE + ETA", "data": "2025-01-20", "status": "Pendente", "prioridade": "Alta", "responsavel": "Projetos", "observacao": "Complexo - 2 sistemas"},
        {"id": "A011", "lote_id": "LOTE-003", "lote_nome": "Lote 3 - Sistema Completo", "consorcio": "Consórcio Andrade Gutierrez", "tipo": "💰", "descricao": "Revisão proposta comercial - R$ 12M", "data": "2025-02-05", "status": "Pendente", "prioridade": "Média", "responsavel": "MC", "observacao": "Ajustar margem"},

        # LOTE-004 - Camargo Corrêa
        {"id": "A012", "lote_id": "LOTE-004", "lote_nome": "Lote 4 - Expansão ETE", "consorcio": "Consórcio Camargo Corrêa", "tipo": "🏭", "descricao": "Fabricação tanques adicionais - 300 L/s", "data": "2024-11-15", "status": "Concluída", "prioridade": "Alta", "responsavel": "Fornecedor", "observacao": "Entregue"},
        {"id": "A013", "lote_id": "LOTE-004", "lote_nome": "Lote 4 - Expansão ETE", "consorcio": "Consórcio Camargo Corrêa", "tipo": "🔧", "descricao": "Instalação final - ETE Expansão Osasco", "data": "2025-01-05", "status": "Pendente", "prioridade": "Alta", "responsavel": "Equipe Campo", "observacao": "Última etapa"},
        {"id": "A014", "lote_id": "LOTE-004", "lote_nome": "Lote 4 - Expansão ETE", "consorcio": "Consórcio Camargo Corrêa", "tipo": "✅", "descricao": "Testes finais e liberação ART", "data": "2025-01-20", "status": "Pendente", "prioridade": "Alta", "responsavel": "MC", "observacao": "ART necessária"},

        # Ações gerais
        {"id": "A015", "lote_id": "GERAL", "lote_nome": "Geral", "consorcio": "Hydrosol", "tipo": "📊", "descricao": "Reunião mensal de portfólio - Todos os lotes", "data": "2025-01-08", "status": "Pendente", "prioridade": "Média", "responsavel": "MC", "observacao": "Preparar relatório"},
        {"id": "A016", "lote_id": "GERAL", "lote_nome": "Geral", "consorcio": "Hydrosol", "tipo": "💰", "descricao": "Fechamento trimestral - Balanço margens", "data": "2025-01-31", "status": "Pendente", "prioridade": "Alta", "responsavel": "Financeiro", "observacao": "Revisar BDI"},
    ]

    return pd.DataFrame(lotes), pd.DataFrame(acoes)

# ============================================================
# FUNÇÃO PARA GERAR RELATÓRIO PDF (simplificada)
# ============================================================
def gerar_relatorio_pdf(dados_lotes, dados_acoes, tipo="completo"):
    """Gera relatório em formato HTML para impressão/PDF"""

    hoje = datetime.now().strftime("%d/%m/%Y")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório Calendário de Ações - Hydrosol</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            .header {{ text-align: center; border-bottom: 3px solid #1E3A5F; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #1E3A5F; margin: 0; }}
            .header p {{ color: #666; margin: 5px 0; }}
            .kpi-box {{ display: inline-block; width: 22%; background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 10px 1%; text-align: center; border-top: 4px solid #667eea; }}
            .kpi-value {{ font-size: 2rem; font-weight: bold; color: #1E3A5F; }}
            .kpi-label {{ font-size: 0.85rem; color: #666; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #1E3A5F; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            .status-atrasada {{ color: #e74c3c; font-weight: bold; }}
            .status-hoje {{ color: #f39c12; font-weight: bold; }}
            .status-futura {{ color: #27ae60; font-weight: bold; }}
            .status-concluida {{ color: #3498db; }}
            .footer {{ margin-top: 40px; text-align: center; color: #999; font-size: 0.85rem; border-top: 1px solid #ddd; padding-top: 20px; }}
            .section {{ margin: 30px 0; }}
            .section h2 {{ color: #1E3A5F; border-left: 4px solid #667eea; padding-left: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🗓️ Calendário de Ações - Hydrosol AI</h1>
            <p>Relatório de Acompanhamento de Lotes e Ações</p>
            <p><strong>Data:</strong> {hoje} | <strong>Responsável:</strong> MC</p>
        </div>

        <div class="section">
            <h2>📊 Resumo Executivo</h2>
            <div style="text-align: center;">
                <div class="kpi-box">
                    <div class="kpi-value">{len(dados_lotes)}</div>
                    <div class="kpi-label">Lotes Ativos</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">{len(dados_acoes)}</div>
                    <div class="kpi-label">Total Ações</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">R$ {sum(dados_lotes['valor']):,.0f}</div>
                    <div class="kpi-label">Valor Pipeline</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">{dados_acoes[dados_acoes['status']=='Concluída'].shape[0]}</div>
                    <div class="kpi-label">Ações Concluídas</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📋 Lotes em Andamento</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Lote</th>
                    <th>Consórcio</th>
                    <th>Tipo</th>
                    <th>Vazão</th>
                    <th>Valor (R$)</th>
                    <th>Prazo</th>
                    <th>Progresso</th>
                    <th>Status</th>
                </tr>
    """

    for _, lote in dados_lotes.iterrows():
        prazo = datetime.strptime(lote['prazo_entrega'], '%Y-%m-%d').strftime('%d/%m/%Y')
        html += f"""
                <tr>
                    <td>{lote['id']}</td>
                    <td>{lote['nome']}</td>
                    <td>{lote['consorcio']}</td>
                    <td>{lote['tipo']}</td>
                    <td>{lote['vazao']}</td>
                    <td>R$ {lote['valor']:,.0f}</td>
                    <td>{prazo}</td>
                    <td>{lote['progresso']}%</td>
                    <td>{lote['status']}</td>
                </tr>
        """

    html += """
            </table>
        </div>

        <div class="section">
            <h2>⚡ Ações Pendentes</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Ação</th>
                    <th>Lote</th>
                    <th>Consórcio</th>
                    <th>Data</th>
                    <th>Prioridade</th>
                    <th>Responsável</th>
                    <th>Status</th>
                </tr>
    """

    hoje_dt = datetime.now()
    for _, acao in dados_acoes.iterrows():
        if acao['status'] != 'Concluída':
            data_acao = datetime.strptime(acao['data'], '%Y-%m-%d')
            if data_acao < hoje_dt:
                status_class = "status-atrasada"
                status_text = "🔴 ATRASADA"
            elif data_acao.date() == hoje_dt.date():
                status_class = "status-hoje"
                status_text = "🟡 HOJE"
            else:
                status_class = "status-futura"
                status_text = "🟢 FUTURA"

            html += f"""
                <tr>
                    <td>{acao['id']}</td>
                    <td>{acao['tipo']} {acao['descricao']}</td>
                    <td>{acao['lote_nome']}</td>
                    <td>{acao['consorcio']}</td>
                    <td>{data_acao.strftime('%d/%m/%Y')}</td>
                    <td>{acao['prioridade']}</td>
                    <td>{acao['responsavel']}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
            """

    html += f"""
            </table>
        </div>

        <div class="footer">
            <p>🌊 Hydrosol AI v5.1 - Sistema de Gestão de Portfólio</p>
            <p>Gerado em {hoje} | Relatório confidencial</p>
        </div>
    </body>
    </html>
    """

    return html

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-header">🗓️ Calendário de Ações</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hydrosol AI v5.1 | Gestão de Lotes e Ações por Consórcio/Sabesp</div>', unsafe_allow_html=True)

# ============================================================
# CARREGAR DADOS
# ============================================================
df_lotes, df_acoes = carregar_dados()

# ============================================================
# MÉTRICAS PRINCIPAIS
# ============================================================
hoje = datetime.now()

# Calcular métricas
total_lotes = len(df_lotes)
total_acoes = len(df_acoes)
acoes_concluidas = len(df_acoes[df_acoes['status'] == 'Concluída'])
acoes_pendentes = total_acoes - acoes_concluidas

# Ações atrasadas
acoes_atrasadas = 0
for _, acao in df_acoes.iterrows():
    if acao['status'] != 'Concluída':
        data_acao = datetime.strptime(acao['data'], '%Y-%m-%d')
        if data_acao < hoje:
            acoes_atrasadas += 1

# Valor pipeline
valor_pipeline = df_lotes['valor'].sum()

# Progresso médio
progresso_medio = df_lotes['progresso'].mean()

# Colunas de métricas
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_lotes}</div>
        <div class="metric-label">Lotes Ativos</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
        <div class="metric-value">{acoes_pendentes}</div>
        <div class="metric-label">Ações Pendentes</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
        <div class="metric-value">{acoes_atrasadas}</div>
        <div class="metric-label">Ações Atrasadas</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <div class="metric-value">R${valor_pipeline/1e6:.1f}M</div>
        <div class="metric-label">Valor Pipeline</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="metric-value">{progresso_medio:.0f}%</div>
        <div class="metric-label">Progresso Médio</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# BOTÃO GERAR RELATÓRIO PDF
# ============================================================
col_pdf1, col_pdf2 = st.columns([1, 4])
with col_pdf1:
    if st.button("📥 Gerar Relatório PDF", type="primary", use_container_width=True):
        with st.spinner("Gerando relatório..."):
            html_relatorio = gerar_relatorio_pdf(df_lotes, df_acoes)
            st.download_button(
                label="⬇️ Baixar Relatório HTML (imprimir como PDF)",
                data=html_relatorio,
                file_name=f"relatorio_calendario_{hoje.strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
            st.success("✅ Relatório gerado! Clique acima para baixar.")

with col_pdf2:
    st.info("💡 **Dica:** Baixe o arquivo HTML e abra no navegador. Depois use Ctrl+P (ou menu ⋮ → Imprimir) e escolha 'Salvar como PDF'. Funciona no PC e celular!")

st.markdown("---")

# ============================================================
# TABS PRINCIPAIS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Lista de Ações", 
    "📅 Timeline", 
    "📊 Dashboard", 
    "🏗️ Lotes", 
    "⚡ Alertas"
])

# ============================================================
# TAB 1: LISTA DE AÇÕES
# ============================================================
with tab1:
    st.subheader("📋 Todas as Ações")

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_status = st.selectbox("Status:", ["Todos", "Pendente", "Concluída", "Atrasada", "Hoje", "Futura"])
    with col_f2:
        filtro_lote = st.selectbox("Lote:", ["Todos"] + df_lotes['nome'].tolist() + ["Geral"])
    with col_f3:
        filtro_prioridade = st.selectbox("Prioridade:", ["Todos", "Alta", "Média", "Baixa"])

    # Filtrar ações
    df_filtrado = df_acoes.copy()

    if filtro_status == "Concluída":
        df_filtrado = df_filtrado[df_filtrado['status'] == 'Concluída']
    elif filtro_status == "Pendente":
        df_filtrado = df_filtrado[df_filtrado['status'] == 'Pendente']
    elif filtro_status == "Atrasada":
        df_filtrado = df_filtrado[
            (df_filtrado['status'] == 'Pendente') & 
            (pd.to_datetime(df_filtrado['data']) < hoje)
        ]
    elif filtro_status == "Hoje":
        df_filtrado = df_filtrado[
            (df_filtrado['status'] == 'Pendente') & 
            (pd.to_datetime(df_filtrado['data']).dt.date == hoje.date())
        ]
    elif filtro_status == "Futura":
        df_filtrado = df_filtrado[
            (df_filtrado['status'] == 'Pendente') & 
            (pd.to_datetime(df_filtrado['data']) > hoje)
        ]

    if filtro_lote != "Todos":
        df_filtrado = df_filtrado[df_filtrado['lote_nome'] == filtro_lote]

    if filtro_prioridade != "Todos":
        df_filtrado = df_filtrado[df_filtrado['prioridade'] == filtro_prioridade]

    # Ordenar por data
    df_filtrado = df_filtrado.sort_values('data')

    # Exibir ações
    if len(df_filtrado) == 0:
        st.success("✅ Nenhuma ação encontrada com os filtros selecionados!")
    else:
        for _, acao in df_filtrado.iterrows():
            data_acao = datetime.strptime(acao['data'], '%Y-%m-%d')

            # Determinar classe CSS
            if acao['status'] == 'Concluída':
                classe = "acao-futura"
                badge = '<span class="badge badge-concluida">✅ Concluída</span>'
            elif data_acao < hoje:
                classe = "acao-atrasada"
                badge = '<span class="badge badge-atrasada">🔴 ATRASADA</span>'
            elif data_acao.date() == hoje.date():
                classe = "acao-hoje"
                badge = '<span class="badge badge-hoje">🟡 HOJE</span>'
            else:
                classe = "acao-futura"
                badge = '<span class="badge badge-futura">🟢 Futura</span>'

            # CORREÇÃO: Usar .get() para evitar KeyError
            cliente_info = f"👤 {acao.get('consorcio', 'N/A')}"

            st.markdown(f"""
            <div class="acao-card {classe}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{acao['tipo']} {acao['descricao']}</strong><br>
                        <small>{cliente_info} | 📅 {data_acao.strftime('%d/%m/%Y')} | 🎯 {acao['prioridade']}</small><br>
                        <small>Responsável: {acao['responsavel']}</small>
                        {f"<br><small>💬 {acao['observacao']}</small>" if acao['observacao'] else ""}
                    </div>
                    <div>{badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# TAB 2: TIMELINE
# ============================================================
with tab2:
    st.subheader("📅 Timeline dos Lotes")

    # Criar timeline com Plotly - CORREÇÃO: usar datas diretamente
    fig = go.Figure()

    cores_status = {
        'Em Execução': '#27ae60',
        'Prospecção': '#3498db',
        'Negociação': '#f39c12',
        'Concluído': '#95a5a6'
    }

    for _, lote in df_lotes.iterrows():
        data_inicio = datetime.strptime(lote['prazo_entrega'], '%Y-%m-%d') - timedelta(days=180)
        data_fim = datetime.strptime(lote['prazo_entrega'], '%Y-%m-%d')

        fig.add_trace(go.Bar(
            name=lote['nome'],
            y=[lote['nome']],
            x=[(data_fim - data_inicio).days],
            base=[data_inicio],
            orientation='h',
            marker_color=cores_status.get(lote['status'], '#667eea'),
            text=f"{lote['status']} | {lote['progresso']}%",
            textposition='inside',
            hovertemplate=f"""
            <b>{lote['nome']}</b><br>
            Consórcio: {lote['consorcio']}<br>
            Status: {lote['status']}<br>
            Progresso: {lote['progresso']}%<br>
            Valor: R$ {lote['valor']:,.0f}<br>
            Prazo: {data_fim.strftime('%d/%m/%Y')}
            """
        ))

    fig.update_layout(
        title="Cronograma dos Lotes - Hydrosol",
        xaxis_title="Data",
        yaxis_title="",
        barmode='overlay',
        height=400,
        showlegend=False,
        xaxis=dict(
            tickformat='%d/%m/%Y',
            tickmode='auto'
        )
    )

    # CORREÇÃO: Não usar add_vline com datetime direto - usar shape em vez disso
    # Adicionar linha de hoje como anotação
    fig.add_annotation(
        x=hoje,
        y=-0.5,
        text="📅 Hoje",
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        font=dict(color="red", size=12),
        ax=0,
        ay=-40
    )

    st.plotly_chart(fig, use_container_width=True)

    # Timeline detalhada por lote
    st.subheader("📋 Detalhamento por Lote")

    for _, lote in df_lotes.iterrows():
        with st.expander(f"{lote['id']} - {lote['nome']} ({lote['status']})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Progresso", f"{lote['progresso']}%")
                st.metric("Etapas", f"{lote['etapas_concluidas']}/{lote['etapas_total']}")
            with col2:
                st.metric("Valor", f"R$ {lote['valor']:,.0f}")
                st.metric("Vazão", lote['vazao'])
            with col3:
                prazo = datetime.strptime(lote['prazo_entrega'], '%Y-%m-%d')
                dias_restantes = (prazo - hoje).days
                st.metric("Prazo", prazo.strftime('%d/%m/%Y'))
                st.metric("Dias Restantes", dias_restantes, 
                         delta="No prazo" if dias_restantes > 30 else "Urgente!" if dias_restantes < 0 else "Atenção")

            # CORREÇÃO: Usar .get() para evitar KeyError
            st.write(f"**Contato:** {lote.get('contato', 'N/A')}")
            st.write(f"**Local:** {lote['local']}")

            # Barra de progresso
            st.progress(lote['progresso'] / 100)

# ============================================================
# TAB 3: DASHBOARD ANALÍTICO
# ============================================================
with tab3:
    st.subheader("📊 Dashboard Analítico")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de status dos lotes
        status_counts = df_lotes['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Status dos Lotes",
            color=status_counts.index,
            color_discrete_map=cores_status
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Gráfico de valor por consórcio
        fig_valor = px.bar(
            df_lotes,
            x='consorcio',
            y='valor',
            title="Valor por Consórcio (R$)",
            color='status',
            color_discrete_map=cores_status,
            text='valor'
        )
        fig_valor.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_valor, use_container_width=True)

    # Gráfico de progresso
    st.subheader("📈 Progresso dos Lotes")

    # CORREÇÃO: Usar barras simples em vez de Indicator (mais estável)
    fig_prog = px.bar(
        df_lotes,
        x='nome',
        y='progresso',
        title="Progresso por Lote (%)",
        color='status',
        color_discrete_map=cores_status,
        text='progresso'
    )
    fig_prog.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_prog.update_yaxes(range=[0, 100])
    fig_prog.update_layout(height=400)

    st.plotly_chart(fig_prog, use_container_width=True)

    # Tabela de ações por prioridade
    st.subheader("🎯 Ações por Prioridade")
    prioridade_counts = df_acoes[df_acoes['status'] == 'Pendente']['prioridade'].value_counts()
    if len(prioridade_counts) > 0:
        fig_prioridade = px.bar(
            x=prioridade_counts.index,
            y=prioridade_counts.values,
            title="Ações Pendentes por Prioridade",
            color=prioridade_counts.index,
            color_discrete_map={'Alta': '#e74c3c', 'Média': '#f39c12', 'Baixa': '#27ae60'},
            labels={'x': 'Prioridade', 'y': 'Quantidade'}
        )
        st.plotly_chart(fig_prioridade, use_container_width=True)
    else:
        st.info("✅ Nenhuma ação pendente!")

# ============================================================
# TAB 4: LOTES
# ============================================================
with tab4:
    st.subheader("🏗️ Gerenciamento de Lotes")

    # Cards dos lotes
    cols = st.columns(len(df_lotes))
    for idx, (_, lote) in enumerate(df_lotes.iterrows()):
        with cols[idx]:
            prazo = datetime.strptime(lote['prazo_entrega'], '%Y-%m-%d')
            dias_restantes = (prazo - hoje).days

            status_color = {
                'Em Execução': '🟢',
                'Prospecção': '🔵',
                'Negociação': '🟡',
                'Concluído': '⚪'
            }

            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-top: 4px solid {cores_status.get(lote['status'], '#667eea')};">
                <h4 style="margin: 0; color: #1E3A5F;">{lote['id']}</h4>
                <p style="margin: 5px 0; font-size: 0.9rem;">{lote['nome'][:30]}...</p>
                <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">{status_color.get(lote['status'], '⚪')} {lote['status']}</p>
                <p style="margin: 5px 0; font-size: 0.8rem;"><strong>R$ {lote['valor']:,.0f}</strong></p>
                <p style="margin: 5px 0; font-size: 0.8rem;">📅 {prazo.strftime('%d/%m/%Y')} ({dias_restantes} dias)</p>
                <div style="margin-top: 10px;">
                    <div style="background: #e5e7eb; border-radius: 10px; height: 8px;">
                        <div style="background: {cores_status.get(lote['status'], '#667eea')}; width: {lote['progresso']}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                    <small>{lote['progresso']}% completo</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabela completa de lotes
    st.subheader("📋 Tabela Completa")

    df_display = df_lotes.copy()
    df_display['prazo_entrega'] = pd.to_datetime(df_display['prazo_entrega']).dt.strftime('%d/%m/%Y')
    df_display['valor'] = df_display['valor'].apply(lambda x: f"R$ {x:,.0f}")

    st.dataframe(
        df_display[['id', 'nome', 'consorcio', 'tipo', 'vazao', 'valor', 'prazo_entrega', 'status', 'progresso']],
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# TAB 5: ALERTAS
# ============================================================
with tab5:
    st.subheader("⚡ Alertas e Notificações")

    # Alertas de ações atrasadas
    st.markdown("### 🔴 Ações Atrasadas")

    acoes_atrasadas_list = []
    for _, acao in df_acoes.iterrows():
        if acao['status'] == 'Pendente':
            data_acao = datetime.strptime(acao['data'], '%Y-%m-%d')
            if data_acao < hoje:
                dias_atraso = (hoje - data_acao).days
                acoes_atrasadas_list.append({
                    'acao': acao,
                    'dias_atraso': dias_atraso
                })

    if not acoes_atrasadas_list:
        st.success("✅ Nenhuma ação atrasada! Ótimo trabalho!")
    else:
        for item in sorted(acoes_atrasadas_list, key=lambda x: x['dias_atraso'], reverse=True):
            acao = item['acao']
            st.markdown(f"""
            <div style="background: #fee2e2; border-left: 4px solid #e74c3c; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;">
                <strong>🔴 {acao['tipo']} {acao['descricao']}</strong><br>
                <small>📅 Previsto: {acao['data']} | ⏰ Atraso: {item['dias_atraso']} dias | 🎯 {acao['prioridade']}</small><br>
                <small>👤 {acao.get('consorcio', 'N/A')} | Responsável: {acao['responsavel']}</small><br>
                <small>💬 {acao['observacao'] if acao['observacao'] else 'Sem observações'}</small>
            </div>
            """, unsafe_allow_html=True)

    # Alertas de prazo de lotes
    st.markdown("### 🟡 Lotes com Prazo Próximo")

    for _, lote in df_lotes.iterrows():
        prazo = datetime.strptime(lote['prazo_entrega'], '%Y-%m-%d')
        dias_restantes = (prazo - hoje).days

        if dias_restantes <= 60 and lote['status'] in ['Em Execução', 'Negociação']:
            cor = "#e74c3c" if dias_restantes < 30 else "#f39c12"
            emoji = "🔴" if dias_restantes < 30 else "🟡"

            st.markdown(f"""
            <div style="background: #fffbeb; border-left: 4px solid {cor}; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;">
                <strong>{emoji} {lote['nome']}</strong><br>
                <small>📅 Prazo: {prazo.strftime('%d/%m/%Y')} | ⏰ {dias_restantes} dias restantes</small><br>
                <small>📊 Progresso: {lote['progresso']}% | 🎯 Status: {lote['status']}</small><br>
                <small>👤 Contato: {lote.get('contato', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)

    # Ações de hoje
    st.markdown("### 🟢 Ações para Hoje")

    acoes_hoje = []
    for _, acao in df_acoes.iterrows():
        if acao['status'] == 'Pendente':
            data_acao = datetime.strptime(acao['data'], '%Y-%m-%d')
            if data_acao.date() == hoje.date():
                acoes_hoje.append(acao)

    if not acoes_hoje:
        st.info("📭 Nenhuma ação programada para hoje.")
    else:
        for acao in acoes_hoje:
            st.markdown(f"""
            <div style="background: #f0fff4; border-left: 4px solid #27ae60; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;">
                <strong>🟡 {acao['tipo']} {acao['descricao']}</strong><br>
                <small>🎯 {acao['prioridade']} | 👤 {acao['responsavel']} | 🏢 {acao.get('consorcio', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85rem;">
    🌊 <strong>Hydrosol AI v5.1</strong> | Sistema de Gestão de Portfólio<br>
    Desenvolvido para MC | Calendário de Ações por Consórcio/Sabesp<br>
    <small>Última atualização: {atualizacao}</small>
</div>
""".format(atualizacao=hoje.strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)