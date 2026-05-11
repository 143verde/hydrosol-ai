import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# ==============================================================================
# CONFIGURACAO
# ==============================================================================
st.set_page_config(page_title="Hydrosol AI - Calendario de Lotes", page_icon="📅", layout="wide")

st.markdown("""
<style>
    .cal-header { font-size: 2.2rem; font-weight: 800; color: #1E3A5F; text-align: center; margin-bottom: 0.5rem; }
    .cal-sub { font-size: 1rem; color: #4A90A4; text-align: center; margin-bottom: 2rem; }
    .lote-card { background: white; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .acao-hoje { background: linear-gradient(135deg, #11998e20, #38ef7d20); border: 2px solid #11998e; }
    .acao-atrasada { background: linear-gradient(135deg, #eb334920, #f45c4320); border: 2px solid #eb3349; }
    .acao-futura { background: linear-gradient(135deg, #f7dc6f20, #ffeaa720); border: 2px solid #f7dc6f; }
    .semana-header { background: linear-gradient(90deg, #1E3A5F, #4A90A4); color: white; padding: 0.8rem; border-radius: 8px; text-align: center; font-weight: 600; margin-bottom: 0.5rem; }
    .metric-cal { background: white; border-radius: 10px; padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .metric-cal h3 { font-size: 1.8rem; color: #1E3A5F; margin: 0; }
    .metric-cal p { font-size: 0.85rem; color: #718096; margin: 0; }
    .consorcio-tag { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.75rem; font-weight: 600; }
    .sabesp-tag { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DADOS DOS LOTES - SABESP = CONTRATANTE | CONSORCIOS = CLIENTES
# ==============================================================================
LOTES_SABESP = [
    {
        "id": "LOTE-01",
        "nome": "Lote 1 - ETEs Série Interior",
        "descricao": "5 unidades de 20 L/s - Região interior SP",
        "quantidade": 5, "vazao_unidade": 20, "grupo": "Serie",
        "valor_total": 55_000_000,
        "status": "Em negociacao",
        "data_base": "2026-06-15",
        "data_limite_proposta": "2026-07-30",
        "data_prevista_assinatura": "2026-09-15",
        "data_inicio_obra": "2026-11-01",
        "data_fim_obra": "2027-08-31",
        "responsavel_comercial": "MC",

        # SABESP = CONTRATANTE (dona do programa)
        "contratante": "Sabesp",
        "contratante_contato": "Diretoria de Expansão - Sabesp",
        "contratante_telefone": "(11) 3333-4444",

        # CONSORCIO = CLIENTE (quem vai nos contratar)
        "cliente": "Consórcio Engeform",
        "cliente_contato": "Eng. Carlos Mendes - Diretor Comercial Engeform",
        "cliente_telefone": "(11) 99999-1111",
        "cliente_email": "carlos.mendes@engeform.com.br",

        "fase": "Proposta enviada",
        "acoes_pendentes": [
            {"data": "2026-05-12", "acao": "Follow-up com Engeform após proposta", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-05-15", "acao": "Reunião técnica Engeform + Sabesp", "responsavel": "MC", "status": "Agendada", "prioridade": "Alta", "tipo": "mista"},
            {"data": "2026-05-18", "acao": "Enviar catálogo técnico atualizado para Engeform", "responsavel": "MC", "status": "Pendente", "prioridade": "Média", "tipo": "cliente"},
            {"data": "2026-05-20", "acao": "Aguardar posicionamento Engeform sobre escopo", "responsavel": "MC", "status": "Pendente", "prioridade": "Média", "tipo": "cliente"},
            {"data": "2026-05-25", "acao": "Reunião interna: ajustar margem se Engeform pedir desconto", "responsavel": "MC", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-06-01", "acao": "Visita técnica aos terrenos com Engeform", "responsavel": "Operações", "status": "Pendente", "prioridade": "Média", "tipo": "mista"},
            {"data": "2026-06-10", "acao": "Proposta final para Engeform (após feedback Sabesp)", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-06-20", "acao": "Negociação final com Engeform", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-07-15", "acao": "Última revisão antes da entrega", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-07-30", "acao": "ENTREGA DA PROPOSTA À SABESP (via Engeform)", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "contratante"},
        ]
    },
    {
        "id": "LOTE-02",
        "nome": "Lote 2 - ETEs Série Litoral",
        "descricao": "8 unidades de 20 L/s - Região litoral SP",
        "quantidade": 8, "vazao_unidade": 20, "grupo": "Serie",
        "valor_total": 96_000_000,
        "status": "Prospeccao",
        "data_base": "2026-08-01",
        "data_limite_proposta": "2026-10-15",
        "data_prevista_assinatura": "2026-12-20",
        "data_inicio_obra": "2027-02-01",
        "data_fim_obra": "2028-01-31",
        "responsavel_comercial": "MC",

        "contratante": "Sabesp",
        "contratante_contato": "Diretoria de Expansão - Sabesp",
        "contratante_telefone": "(11) 3333-4444",

        "cliente": "Consórcio Azevedo Travassos",
        "cliente_contato": "Dra. Fernanda Azevedo - Sócia-diretora",
        "cliente_telefone": "(11) 98888-2222",
        "cliente_email": "fernanda@azevedotravassos.com.br",

        "fase": "Primeiro contato",
        "acoes_pendentes": [
            {"data": "2026-05-12", "acao": "Primeira apresentação à Azevedo Travassos", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-05-15", "acao": "Enviar credentials e portfólio Hydrosol", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-05-18", "acao": "Aguardar retorno Azevedo Travassos sobre interesse", "responsavel": "MC", "status": "Pendente", "prioridade": "Média", "tipo": "cliente"},
            {"data": "2026-05-22", "acao": "Levantamento de requisitos técnicos com Azevedo", "responsavel": "Engenharia", "status": "Pendente", "prioridade": "Média", "tipo": "cliente"},
            {"data": "2026-06-01", "acao": "Análise de fatores de ajuste (maresia litoral)", "responsavel": "Operações", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-06-10", "acao": "Simulação de preço no Dashboard (BDI ajustado)", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-06-20", "acao": "Proposta preliminar para Azevedo Travassos", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-07-05", "acao": "Reunião de negociação com Azevedo", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-08-01", "acao": "Azevedo Travassos define se segue com Hydrosol", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "cliente"},
            {"data": "2026-10-15", "acao": "ENTREGA DA PROPOSTA À SABESP (via Azevedo Travassos)", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "contratante"},
        ]
    },
    {
        "id": "LOTE-03",
        "nome": "Lote 3 - ETEs Médio",
        "descricao": "3 unidades de 100 L/s - Região metropolitana",
        "quantidade": 3, "vazao_unidade": 100, "grupo": "Medio",
        "valor_total": 165_000_000,
        "status": "Em negociacao",
        "data_base": "2026-07-01",
        "data_limite_proposta": "2026-09-30",
        "data_prevista_assinatura": "2026-11-30",
        "data_inicio_obra": "2027-01-15",
        "data_fim_obra": "2028-06-30",
        "responsavel_comercial": "MC",

        "contratante": "Sabesp",
        "contratante_contato": "Diretoria Metropolitana - Sabesp",
        "contratante_telefone": "(11) 3333-5555",

        "cliente": "Consórcio Constranil",
        "cliente_contato": "Eng. Roberto Silva - Gerente Comercial",
        "cliente_telefone": "(11) 97777-3333",
        "cliente_email": "roberto.silva@constranil.com.br",

        "fase": "Negociação avançada",
        "acoes_pendentes": [
            {"data": "2026-05-10", "acao": "Reunião de alinhamento de escopo com Constranil", "responsavel": "MC", "status": "Concluída", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-05-12", "acao": "Ajustar margem para 28% (BDI 1.35) - pedido Constranil", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-05-15", "acao": "Enviar nova simulação de preço para Constranil", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-05-18", "acao": "Revisão de cronograma com operações (prazo Constranil)", "responsavel": "Operações", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-05-22", "acao": "Documentação de garantias estendidas (pedido Constranil)", "responsavel": "Jurídico", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-06-01", "acao": "Apresentação conjunta Hydrosol + Constranil para Sabesp", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "mista"},
            {"data": "2026-06-15", "acao": "Negociação final de prazos com Constranil", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-09-30", "acao": "ENTREGA DA PROPOSTA À SABESP (via Constranil)", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "contratante"},
        ]
    },
    {
        "id": "LOTE-04",
        "nome": "Lote 4 - ETA Magnum",
        "descricao": "1 unidade de 1000 L/s - Grande São Paulo",
        "quantidade": 1, "vazao_unidade": 1000, "grupo": "Magnum",
        "valor_total": 520_000_000,
        "status": "Prospeccao",
        "data_base": "2026-10-01",
        "data_limite_proposta": "2027-03-31",
        "data_prevista_assinatura": "2027-06-30",
        "data_inicio_obra": "2027-09-01",
        "data_fim_obra": "2029-06-30",
        "responsavel_comercial": "MC",

        "contratante": "Sabesp",
        "contratante_contato": "Superintendência - Sabesp",
        "contratante_telefone": "(11) 3333-6666",

        "cliente": "Consórcio OAS/Galvo",
        "cliente_contato": "Eng. Paulo Galvo - Diretor Presidente",
        "cliente_telefone": "(11) 96666-4444",
        "cliente_email": "paulo.galvo@oasgalvo.com.br",

        "fase": "Estudo de viabilidade",
        "acoes_pendentes": [
            {"data": "2026-05-15", "acao": "Reunião inicial de escopo com OAS/Galvo", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-05-20", "acao": "Apresentar DNA Camburi adaptado para 1000 L/s", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-06-01", "acao": "Estudo geotécnico do terreno (Solicitado por OAS)", "responsavel": "Operações", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-06-10", "acao": "Análise de viabilidade técnica (equipe + OAS)", "responsavel": "Engenharia", "status": "Pendente", "prioridade": "Alta", "tipo": "mista"},
            {"data": "2026-06-20", "acao": "Primeira simulação de custo (DNA Camburi × escala Magnum)", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-07-01", "acao": "Definição de parceiros/subcontratados (OAS define)", "responsavel": "Operações", "status": "Pendente", "prioridade": "Média", "tipo": "cliente"},
            {"data": "2026-07-15", "acao": "Proposta conceitual para OAS/Galvo", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-08-01", "acao": "Negociação de BDI com OAS (target 1.30)", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-09-01", "acao": "OAS/Galvo define se Hydrosol entra no consórcio", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "cliente"},
            {"data": "2027-03-31", "acao": "ENTREGA DA PROPOSTA À SABESP (via OAS/Galvo)", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "contratante"},
        ]
    },
    {
        "id": "LOTE-05",
        "nome": "Lote 5 - ETEs Série Remanescentes",
        "descricao": "12 unidades de 20 L/s - Diversas regiões",
        "quantidade": 12, "vazao_unidade": 20, "grupo": "Serie",
        "valor_total": 138_000_000,
        "status": "Planejamento",
        "data_base": "2027-01-01",
        "data_limite_proposta": "2027-06-30",
        "data_prevista_assinatura": "2027-09-30",
        "data_inicio_obra": "2027-11-01",
        "data_fim_obra": "2029-02-28",
        "responsavel_comercial": "MC",

        "contratante": "Sabesp",
        "contratante_contato": "Programa Onda Limpa - Sabesp",
        "contratante_telefone": "(11) 3333-7777",

        "cliente": "A definir (licitação aberta)",
        "cliente_contato": "Aguardando publicação do edital",
        "cliente_telefone": "-",
        "cliente_email": "-",

        "fase": "Planejamento interno",
        "acoes_pendentes": [
            {"data": "2026-05-20", "acao": "Monitorar publicação do edital Sabesp", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "contratante"},
            {"data": "2026-06-01", "acao": "Mapeamento de terrenos disponíveis (12 unidades)", "responsavel": "Operações", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-06-15", "acao": "Identificar potenciais consórcios interessados", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-07-01", "acao": "Definição de prioridade de regiões (logística)", "responsavel": "MC", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-07-15", "acao": "Prospecção ativa: Engeform, Azevedo, Constranil", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-08-01", "acao": "Loteamento por proximidade logística (economia escala)", "responsavel": "Operações", "status": "Pendente", "prioridade": "Média", "tipo": "interna"},
            {"data": "2026-09-01", "acao": "Simulação de preço em lote (12 unidades = desconto)", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "interna"},
            {"data": "2026-10-01", "acao": "Primeiro contato com consórcio vencedor", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2026-11-01", "acao": "Negociação de preço de lote (12 unidades)", "responsavel": "MC", "status": "Pendente", "prioridade": "Alta", "tipo": "cliente"},
            {"data": "2027-06-30", "acao": "ENTREGA DA PROPOSTA À SABESP (via consórcio)", "responsavel": "MC", "status": "Pendente", "prioridade": "Crítica", "tipo": "contratante"},
        ]
    }
]

# ==============================================================================
# FUNCOES AUXILIARES
# ==============================================================================
def get_acoes_flat():
    acoes = []
    hoje = datetime.now().date()

    for lote in LOTES_SABESP:
        for acao in lote["acoes_pendentes"]:
            data_acao = datetime.strptime(acao["data"], "%Y-%m-%d").date()
            dias_restantes = (data_acao - hoje).days

            acoes.append({
                "lote_id": lote["id"],
                "lote_nome": lote["nome"],
                "grupo": lote["grupo"],
                "valor_total": lote["valor_total"],
                "contratante": lote["contratante"],
                "cliente": lote["cliente"],
                "cliente_contato": lote["cliente_contato"],
                "data": acao["data"],
                "data_dt": data_acao,
                "acao": acao["acao"],
                "responsavel": acao["responsavel"],
                "status": acao["status"],
                "prioridade": acao["prioridade"],
                "tipo": acao["tipo"],
                "dias_restantes": dias_restantes,
                "semana": data_acao.isocalendar()[1],
                "mes": data_acao.month,
                "ano": data_acao.year
            })

    return pd.DataFrame(acoes)

def get_cor_prioridade(p):
    return {"Crítica": "#EB3349", "Alta": "#F7DC6F", "Média": "#74B9FF", "Baixa": "#A0AEC0"}.get(p, "#A0AEC0")

def get_cor_tipo(t):
    return {"cliente": "#667EEA", "contratante": "#11998E", "interna": "#F7DC6F", "mista": "#4A90A4"}.get(t, "#A0AEC0")

def get_tag_tipo(t):
    tags = {
        "cliente": "<span class='consorcio-tag'>🏗️ CONSÓRCIO</span>",
        "contratante": "<span class='sabesp-tag'>💧 SABESP</span>",
        "interna": "<span style='background:#E2E8F0; padding:3px 10px; border-radius:15px; font-size:0.75rem;'>🏢 INTERNA</span>",
        "mista": "<span style='background:#DDA0DD; color:white; padding:3px 10px; border-radius:15px; font-size:0.75rem;'>🤝 MISTA</span>"
    }
    return tags.get(t, "")

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown('<div class="cal-header">📅 Calendário de Ações por Lote</div>', unsafe_allow_html=True)
st.markdown('<div class="cal-sub">Sabesp = Contratante | Consórcios = Clientes | Programa Onda Limpa</div>', unsafe_allow_html=True)

# ==============================================================================
# KPIs
# ==============================================================================
df_acoes = get_acoes_flat()
hoje = datetime.now().date()

acoes_hoje = len(df_acoes[(df_acoes["data_dt"] == hoje) & (df_acoes["status"] != "Concluída")])
acoes_atrasadas = len(df_acoes[(df_acoes["data_dt"] < hoje) & (df_acoes["status"] == "Pendente")])
acoes_semana = len(df_acoes[(df_acoes["dias_restantes"] >= 0) & (df_acoes["dias_restantes"] <= 7) & (df_acoes["status"] != "Concluída")])
acoes_consorcio = len(df_acoes[(df_acoes["tipo"] == "cliente") & (df_acoes["status"] != "Concluída")])
valor_pipeline = sum(l["valor_total"] for l in LOTES_SABESP if l["status"] in ["Em negociacao", "Prospeccao", "Planejamento"])

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.markdown(f'<div class="metric-cal"><h3>{acoes_hoje}</h3><p>Ações Hoje</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-cal"><h3>{acoes_atrasadas}</h3><p>Atrasadas</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-cal"><h3>{acoes_semana}</h3><p>Esta Semana</p></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-cal"><h3>{acoes_consorcio}</h3><p>c/ Consórcios</p></div>', unsafe_allow_html=True)
with col5: st.markdown(f'<div class="metric-cal"><h3>R$ {valor_pipeline/1e6:.0f}M</h3><p>Pipeline</p></div>', unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# MENU LATERAL
# ==============================================================================
menu = st.sidebar.radio("Visualização", [
    "📅 Visão Semanal",
    "📊 Visão Mensal",
    "📋 Lista de Ações",
    "🏗️ Por Consórcio",
    "📈 Timeline Geral"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros")

lote_filtro = st.sidebar.multiselect("Lotes", options=[l["nome"] for l in LOTES_SABESP], default=[l["nome"] for l in LOTES_SABESP])
tipo_filtro = st.sidebar.multiselect("Tipo de Ação", options=["cliente", "contratante", "interna", "mista"], default=["cliente", "contratante", "mista"])
prioridade_filtro = st.sidebar.multiselect("Prioridade", options=["Crítica", "Alta", "Média", "Baixa"], default=["Crítica", "Alta", "Média"])

mask = (df_acoes["lote_nome"].isin(lote_filtro) & df_acoes["tipo"].isin(tipo_filtro) & df_acoes["prioridade"].isin(prioridade_filtro))
df_filtrado = df_acoes[mask].copy()

# ==============================================================================
# ABA 1: VISAO SEMANAL
# ==============================================================================
if menu == "📅 Visão Semanal":
    st.subheader("📅 Ações da Semana")

    semana_atual = hoje.isocalendar()[1]
    ano_atual = hoje.year
    semanas = []
    for i in range(4):
        s = semana_atual + i
        a = ano_atual
        if s > 52: s -= 52; a += 1
        semanas.append((a, s))

    for ano, semana in semanas:
        st.markdown(f'<div class="semana-header">Semana {semana} / {ano}</div>', unsafe_allow_html=True)
        df_sem = df_filtrado[(df_filtrado["ano"] == ano) & (df_filtrado["semana"] == semana) & (df_filtrado["status"] != "Concluída")].sort_values("data_dt")

        if len(df_sem) == 0:
            st.info("Nenhuma ação agendada.")
        else:
            cols = st.columns(min(len(df_sem), 2))
            for idx, (_, acao) in enumerate(df_sem.iterrows()):
                with cols[idx % 2]:
                    cor = get_cor_prioridade(acao["prioridade"])
                    tag = get_tag_tipo(acao["tipo"])
                    dias_txt = "HOJE" if acao["dias_restantes"] == 0 else f"Em {acao['dias_restantes']}d" if acao["dias_restantes"] > 0 else f"ATRASADA {abs(acao['dias_restantes'])}d"
                    classe = "acao-hoje" if acao["dias_restantes"] == 0 else "acao-atrasada" if acao["dias_restantes"] < 0 else "acao-futura"

                    st.markdown(f"""
                    <div class="lote-card {classe}" style="border-left-color: {cor};">
                        <div style="margin-bottom:8px;">{tag}</div>
                        <div style="font-size:0.75rem; color:#718096;">{acao['data']} | {dias_txt}</div>
                        <div style="font-weight:600; color:#1E3A5F; margin:5px 0;">{acao['acao']}</div>
                        <div style="font-size:0.8rem; color:#4A5568;">📦 {acao['lote_id']} | 👤 {acao['responsavel']}</div>
                        <div style="margin-top:8px;">
                            <span style="background:{cor}; color:white; padding:2px 8px; border-radius:10px; font-size:0.7rem;">{acao['prioridade']}</span>
                            <span style="background:#E2E8F0; color:#4A5568; padding:2px 8px; border-radius:10px; font-size:0.7rem; margin-left:5px;">{acao['status']}</span>
                        </div>
                        {f'<div style="margin-top:5px; font-size:0.75rem; color:#667eea;">🏗️ {acao["cliente"][:30]}</div>' if acao['tipo'] == 'cliente' else ''}
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# ABA 2: VISAO MENSAL
# ==============================================================================
elif menu == "📊 Visão Mensal":
    st.subheader("📊 Calendário Mensal")

    mes_sel = st.selectbox("Mês", options=range(5,13), format_func=lambda x: f"{calendar.month_name[x]} 2026", index=0)
    ano_cal = 2026

    df_mes = df_filtrado[(df_filtrado["mes"] == mes_sel) & (df_filtrado["ano"] == ano_cal) & (df_filtrado["status"] != "Concluída")].sort_values("data_dt")

    # Grid calendário
    primeiro = datetime(ano_cal, mes_sel, 1)
    ultimo_dia = calendar.monthrange(ano_cal, mes_sel)[1]
    dias = [datetime(ano_cal, mes_sel, d) for d in range(1, ultimo_dia+1)]

    st.markdown("<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap:5px; margin-bottom:20px;'>", unsafe_allow_html=True)
    for d in ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]:
        st.markdown(f"<div style='text-align:center; font-weight:600; color:#1E3A5F; padding:5px;'>{d}</div>", unsafe_allow_html=True)

    for _ in range(primeiro.weekday()):
        st.markdown("<div style='min-height:80px;'></div>", unsafe_allow_html=True)

    for dia in dias:
        acoes_dia = df_mes[df_mes["data_dt"] == dia.date()]
        n = len(acoes_dia)
        tem_c = any(acoes_dia["prioridade"] == "Crítica") if n > 0 else False
        tem_cliente = any(acoes_dia["tipo"] == "cliente") if n > 0 else False

        bg = "#FEE2E2" if tem_c else "#E0E7FF" if tem_cliente else "#F0FDF4" if n > 0 else "white"
        bd = "#EB3349" if tem_c else "#667EEA" if tem_cliente else "#11998E" if n > 0 else "#E2E8F0"

        st.markdown(f"""
        <div style="background:{bg}; border:2px solid {bd}; border-radius:8px; padding:5px; min-height:80px;">
            <div style="font-weight:600; color:#1E3A5F; font-size:0.9rem;">{dia.day}</div>
            {f'<div style="font-size:0.7rem; color:#4A5568;">{n} ação(ões)</div>' if n > 0 else ''}
            {f'<div style="font-size:0.6rem; color:#EB3349; font-weight:600;">⚠️ CRÍTICA</div>' if tem_c else ''}
            {f'<div style="font-size:0.6rem; color:#667eea;">🏗️ Consórcio</div>' if tem_cliente else ''}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Lista detalhada
    st.markdown("---")
    st.subheader(f"📋 Ações de {calendar.month_name[mes_sel]} 2026")

    if len(df_mes) == 0:
        st.info("Nenhuma ação agendada.")
    else:
        for _, acao in df_mes.iterrows():
            cor = get_cor_prioridade(acao["prioridade"])
            tag = get_tag_tipo(acao["tipo"])
            st.markdown(f"""
            <div class="lote-card" style="border-left-color: {cor}; margin-bottom:8px;">
                <div style="margin-bottom:5px;">{tag}</div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><span style="font-weight:600; color:#1E3A5F;">{acao['data']}</span> <span style="margin-left:10px; color:#4A5568;">{acao['acao']}</span></div>
                    <span style="background:{cor}; color:white; padding:2px 8px; border-radius:10px; font-size:0.7rem;">{acao['prioridade']}</span>
                </div>
                <div style="margin-top:5px; font-size:0.8rem; color:#718096;">
                    📦 {acao['lote_id']} | 👤 {acao['responsavel']} | 💰 R$ {acao['valor_total']/1e6:.0f}M
                    {f' | 🏗️ <strong>{acao["cliente"]}</strong>' if acao['tipo'] == 'cliente' else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: LISTA DE ACOES
# ==============================================================================
elif menu == "📋 Lista de Ações":
    st.subheader("📋 Todas as Ações")

    df_lista = df_filtrado[df_filtrado["status"] != "Concluída"].sort_values("data_dt")

    if len(df_lista) == 0:
        st.success("✅ Todas as ações concluídas!")
    else:
        tabs = st.tabs(["🔴 Atrasadas", "🟡 Hoje", "🟢 Futuras", "🏗️ c/ Consórcios", "💧 c/ Sabesp"])

        with tabs[0]:
            df_a = df_lista[df_lista["dias_restantes"] < 0]
            if len(df_a) > 0:
                st.error(f"⚠️ {len(df_a)} ações atrasadas!")
                for _, acao in df_a.iterrows():
                    tag = get_tag_tipo(acao["tipo"])
                    st.markdown(f"""
                    <div class="lote-card acao-atrasada" style="border-left-color:#EB3349;">
                        <div style="margin-bottom:5px;">{tag}</div>
                        <div style="font-weight:600; color:#1E3A5F;">{acao['acao']}</div>
                        <div style="color:#EB3349; font-weight:600;">⚠️ ATRASADA {abs(acao['dias_restantes'])} DIAS</div>
                        <div style="font-size:0.85rem; color:#4A5568;">📅 {acao['data']} | 📦 {acao['lote_id']} | 👤 {acao['responsavel']}</div>
                        {f'<div style="font-size:0.8rem; color:#667eea; margin-top:5px;">🏗️ {acao["cliente"]} | 📞 {acao["cliente_telefone"]}</div>' if acao['tipo'] == 'cliente' else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Nenhuma ação atrasada!")

        with tabs[1]:
            df_h = df_lista[df_lista["dias_restantes"] == 0]
            if len(df_h) > 0:
                st.warning(f"📅 {len(df_h)} ações para HOJE")
                for _, acao in df_h.iterrows():
                    tag = get_tag_tipo(acao["tipo"])
                    st.markdown(f"""
                    <div class="lote-card acao-hoje" style="border-left-color:#11998E;">
                        <div style="margin-bottom:5px;">{tag}</div>
                        <div style="font-weight:600; color:#1E3A5F;">{acao['acao']}</div>
                        <div style="color:#11998E; font-weight:600;">📅 HOJE</div>
                        <div style="font-size:0.85rem; color:#4A5568;">📦 {acao['lote_id']} | 👤 {acao['responsavel']} | 🏷️ {acao['prioridade']}</div>
                        {f'<div style="font-size:0.8rem; color:#667eea; margin-top:5px;">🏗️ <strong>{acao["cliente"]}</strong> | 📞 {acao["cliente_telefone"]} | ✉️ {acao["cliente_email"]}</div>' if acao['tipo'] == 'cliente' else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📅 Nenhuma ação para hoje.")

        with tabs[2]:
            df_f = df_lista[df_lista["dias_restantes"] > 0]
            if len(df_f) > 0:
                st.info(f"📅 {len(df_f)} ações futuras")
                for _, acao in df_f.iterrows():
                    cor = get_cor_prioridade(acao["prioridade"])
                    tag = get_tag_tipo(acao["tipo"])
                    st.markdown(f"""
                    <div class="lote-card acao-futura" style="border-left-color:{cor};">
                        <div style="margin-bottom:5px;">{tag}</div>
                        <div style="font-weight:600; color:#1E3A5F;">{acao['acao']}</div>
                        <div style="color:#4A5568;">Em {acao['dias_restantes']} dias ({acao['data']})</div>
                        <div style="font-size:0.85rem; color:#4A5568;">📦 {acao['lote_id']} | 👤 {acao['responsavel']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📅 Nenhuma ação futura.")

        with tabs[3]:
            df_c = df_lista[df_lista["tipo"] == "cliente"]
            if len(df_c) > 0:
                st.info(f"🏗️ {len(df_c)} ações com consórcios")
                for _, acao in df_c.iterrows():
                    cor = get_cor_prioridade(acao["prioridade"])
                    st.markdown(f"""
                    <div class="lote-card" style="border-left-color:#667eea; margin-bottom:8px;">
                        <div style="margin-bottom:5px;">{get_tag_tipo('cliente')}</div>
                        <div style="font-weight:600; color:#1E3A5F;">{acao['acao']}</div>
                        <div style="font-size:0.85rem; color:#4A5568;">📅 {acao['data']} | 📦 {acao['lote_id']}</div>
                        <div style="margin-top:8px; padding:8px; background:#E0E7FF; border-radius:8px;">
                            <div style="font-size:0.85rem; color:#1E3A5F;"><strong>🏗️ {acao['cliente']}</strong></div>
                            <div style="font-size:0.8rem; color:#4A5568;">👤 {acao['cliente_contato']}</div>
                            <div style="font-size:0.8rem; color:#4A5568;">📞 {acao['cliente_telefone']} | ✉️ {acao['cliente_email']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("🏗️ Nenhuma ação com consórcios agendada.")

        with tabs[4]:
            df_s = df_lista[df_lista["tipo"] == "contratante"]
            if len(df_s) > 0:
                st.info(f"💧 {len(df_s)} ações com Sabesp")
                for _, acao in df_s.iterrows():
                    st.markdown(f"""
                    <div class="lote-card" style="border-left-color:#11998E; margin-bottom:8px;">
                        <div style="margin-bottom:5px;">{get_tag_tipo('contratante')}</div>
                        <div style="font-weight:600; color:#1E3A5F;">{acao['acao']}</div>
                        <div style="font-size:0.85rem; color:#4A5568;">📅 {acao['data']} | 📦 {acao['lote_id']}</div>
                        <div style="margin-top:8px; padding:8px; background:#D1FAE5; border-radius:8px;">
                            <div style="font-size:0.85rem; color:#1E3A5F;"><strong>💧 {acao['contratante']}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("💧 Nenhuma ação com Sabesp agendada.")

# ==============================================================================
# ABA 4: POR CONSORCIO
# ==============================================================================
elif menu == "🏗️ Por Consórcio":
    st.subheader("🏗️ Ações por Consórcio")

    consorcio_sel = st.selectbox("Selecione o Consórcio", options=[l["cliente"] for l in LOTES_SABESP])
    lote = next(l for l in LOTES_SABESP if l["cliente"] == consorcio_sel)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Unidades", lote["quantidade"])
    with col2: st.metric("Vazão", f"{lote['vazao_unidade']} L/s")
    with col3: st.metric("Valor", f"R$ {lote['valor_total']/1e6:.0f}M")
    with col4: st.metric("Status", lote["status"])

    # Card do consórcio
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea20, #764ba220); border: 2px solid #667eea; border-radius: 12px; padding: 20px; margin: 15px 0;">
        <div style="font-size: 1.2rem; font-weight: 700; color: #1E3A5F; margin-bottom: 10px;">🏗️ {lote['cliente']}</div>
        <div style="color: #4A5568; margin-bottom: 5px;"><strong>Contato:</strong> {lote['cliente_contato']}</div>
        <div style="color: #4A5568; margin-bottom: 5px;"><strong>📞</strong> {lote['cliente_telefone']} | <strong>✉️</strong> {lote['cliente_email']}</div>
        <div style="color: #4A5568; margin-top: 10px;"><strong>💧 Contratante:</strong> {lote['contratante']} | {lote['contratante_contato']}</div>
        <div style="color: #4A5568;"><strong>📞 Sabesp:</strong> {lote['contratante_telefone']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📅 Timeline do Lote")

    timeline_data = [
        {"Etapa": "Base", "Início": datetime.strptime(lote["data_base"], "%Y-%m-%d"), "Fim": datetime.strptime(lote["data_base"], "%Y-%m-%d"), "Tipo": "Marco"},
        {"Etapa": "Limite Proposta", "Início": datetime.strptime(lote["data_limite_proposta"], "%Y-%m-%d"), "Fim": datetime.strptime(lote["data_limite_proposta"], "%Y-%m-%d"), "Tipo": "Crítico"},
        {"Etapa": "Assinatura", "Início": datetime.strptime(lote["data_prevista_assinatura"], "%Y-%m-%d"), "Fim": datetime.strptime(lote["data_prevista_assinatura"], "%Y-%m-%d"), "Tipo": "Marco"},
        {"Etapa": "Início Obra", "Início": datetime.strptime(lote["data_inicio_obra"], "%Y-%m-%d"), "Fim": datetime.strptime(lote["data_inicio_obra"], "%Y-%m-%d"), "Tipo": "Marco"},
        {"Etapa": "Fim Obra", "Início": datetime.strptime(lote["data_fim_obra"], "%Y-%m-%d"), "Fim": datetime.strptime(lote["data_fim_obra"], "%Y-%m-%d"), "Tipo": "Marco"},
    ]
    df_timeline = pd.DataFrame(timeline_data)
    fig = px.timeline(df_timeline, x_start="Início", x_end="Fim", y="Etapa", color="Tipo",
                      color_discrete_map={"Marco": "#4A90A4", "Crítico": "#EB3349"})
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Ações com este Consórcio")

    df_lote = df_filtrado[(df_filtrado["lote_nome"] == lote["nome"]) & (df_filtrado["status"] != "Concluída")].sort_values("data_dt")

    for _, acao in df_lote.iterrows():
        cor = get_cor_prioridade(acao["prioridade"])
        tag = get_tag_tipo(acao["tipo"])
        st.markdown(f"""
        <div class="lote-card" style="border-left-color: {cor}; margin-bottom: 8px;">
            <div style="margin-bottom:5px;">{tag}</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div><span style="font-weight:600; color:#1E3A5F;">{acao['data']}</span> <span style="margin-left:10px; color:#4A5568;">{acao['acao']}</span></div>
                <span style="background:{cor}; color:white; padding:2px 8px; border-radius:10px; font-size:0.7rem;">{acao['prioridade']}</span>
            </div>
            <div style="margin-top:5px; font-size:0.8rem; color:#718096;">👤 {acao['responsavel']}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 5: TIMELINE GERAL
# ==============================================================================
elif menu == "📈 Timeline Geral":
    st.subheader("📈 Timeline de Todos os Lotes")

    timeline_geral = []
    for lote in LOTES_SABESP:
        timeline_geral.append({
            "Lote": lote["nome"],
            "Início": datetime.strptime(lote["data_base"], "%Y-%m-%d"),
            "Fim": datetime.strptime(lote["data_fim_obra"], "%Y-%m-%d"),
            "Grupo": lote["grupo"],
            "Cliente": lote["cliente"],
            "Valor": lote["valor_total"]
        })

    df_tg = pd.DataFrame(timeline_geral)
    fig = px.timeline(df_tg, x_start="Início", x_end="Fim", y="Lote", color="Grupo", hover_data=["Cliente", "Valor"])
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de consórcios
    st.markdown("---")
    st.subheader("🏗️ Consórcios e Lotes")

    df_cons = pd.DataFrame([{
        "Lote": l["id"],
        "Consórcio": l["cliente"],
        "Contato": l["cliente_contato"],
        "Telefone": l["cliente_telefone"],
        "Valor (R$)": f"{l['valor_total']/1e6:.0f}M",
        "Status": l["status"],
        "Fase": l["fase"]
    } for l in LOTES_SABESP])

    st.dataframe(df_cons, use_container_width=True, hide_index=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    🌊 Hydrosol AI v5.1 | Calendário de Ações | Programa Onda Limpa<br>
    💧 Sabesp = Contratante | 🏗️ Consórcios = Clientes<br>
    5 Lotes | 29 Unidades | R$ 974M em pipeline
</div>
""", unsafe_allow_html=True)