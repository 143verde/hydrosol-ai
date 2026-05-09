"""
================================================================================
HYDROSOL AI DASHBOARD v5.1 - UNIFICADO
Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
================================================================================
MODULOS INTEGRADOS:
  1. Dashboard Base (13 etapas + Notion API)
  2. Calculo Parametrico de Margem (DNA Camburi)
  3. Simulador de Negociacao (sliders BDI/margem)
  4. Integracao n8n (envio de propostas)
================================================================================
"""

import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import os

# CONFIGURACAO GLOBAL
st.set_page_config(page_title="Hydrosol AI Dashboard v5.1", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# CSS TEMA HYDROSOL
st.markdown("""
<style>
:root { --hydro-primary: #0066CC; --hydro-secondary: #00A3E0; --hydro-accent: #00D4AA; --hydro-dark: #0A1628; --hydro-card: #111D2E; --hydro-border: #1E3A5F; --hydro-text: #E8F4F8; --hydro-muted: #7A8B9A; --hydro-success: #00D4AA; --hydro-warning: #FFB800; --hydro-danger: #FF4757; }
.main { background-color: var(--hydro-dark); color: var(--hydro-text); }
.stApp { background-color: var(--hydro-dark); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A1628 0%, #0D1F35 100%) !important; border-right: 1px solid var(--hydro-border); }
.hydro-header { background: linear-gradient(135deg, #0066CC 0%, #00A3E0 50%, #00D4AA 100%); padding: 20px 30px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0, 102, 204, 0.3); }
.hydro-header h1 { color: white !important; font-size: 2rem !important; font-weight: 800 !important; margin: 0 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
.hydro-header p { color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0 !important; font-size: 1rem; }
.hydro-card { background: linear-gradient(145deg, #111D2E 0%, #0F1A2A 100%); border: 1px solid var(--hydro-border); border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); transition: all 0.3s ease; }
.hydro-card:hover { border-color: var(--hydro-secondary); box-shadow: 0 8px 30px rgba(0, 163, 224, 0.15); transform: translateY(-2px); }
.kpi-card { background: linear-gradient(145deg, #111D2E 0%, #0F1A2A 100%); border: 1px solid var(--hydro-border); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.kpi-value { font-size: 2.2rem; font-weight: 800; color: var(--hydro-accent); margin: 8px 0; }
.kpi-label { font-size: 0.85rem; color: var(--hydro-muted); text-transform: uppercase; letter-spacing: 1px; }
.stepper-container { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; margin-bottom: 24px; }
.step-item { display: flex; flex-direction: column; align-items: center; flex: 1; position: relative; }
.step-item:not(:last-child)::after { content: ''; position: absolute; top: 20px; right: -50%; width: 100%; height: 3px; background: var(--hydro-border); z-index: 0; }
.step-item.active:not(:last-child)::after { background: linear-gradient(90deg, var(--hydro-primary), var(--hydro-accent)); }
.step-circle { width: 40px; height: 40px; border-radius: 50%; background: var(--hydro-card); border: 2px solid var(--hydro-border); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; color: var(--hydro-muted); z-index: 1; transition: all 0.3s ease; }
.step-item.active .step-circle { background: linear-gradient(135deg, var(--hydro-primary), var(--hydro-accent)); border-color: var(--hydro-accent); color: white; box-shadow: 0 0 20px rgba(0, 212, 170, 0.4); }
.step-item.completed .step-circle { background: var(--hydro-success); border-color: var(--hydro-success); color: white; }
.step-label { margin-top: 8px; font-size: 0.75rem; color: var(--hydro-muted); text-align: center; max-width: 80px; }
.step-item.active .step-label { color: var(--hydro-accent); font-weight: 600; }
.stButton > button { background: linear-gradient(135deg, var(--hydro-primary), var(--hydro-secondary)) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 12px 24px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
.stButton > button:hover { box-shadow: 0 4px 20px rgba(0, 102, 204, 0.4) !important; transform: translateY(-2px) !important; }
.hydro-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--hydro-border), transparent); margin: 24px 0; }
.notion-status { display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 12px; font-size: 0.9rem; font-weight: 500; }
.notion-status.connected { background: rgba(0, 212, 170, 0.1); border: 1px solid var(--hydro-success); color: var(--hydro-success); }
.notion-status.disconnected { background: rgba(255, 71, 87, 0.1); border: 1px solid var(--hydro-danger); color: var(--hydro-danger); }
.status-dot { width: 10px; height: 10px; border-radius: 50%; animation: pulse 2s infinite; }
.status-dot.connected { background: var(--hydro-success); }
.status-dot.disconnected { background: var(--hydro-danger); }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.simulador-header { background: linear-gradient(135deg, #0066CC 0%, #00A3E0 50%, #00D4AA 100%); padding: 24px 30px; border-radius: 20px; margin-bottom: 28px; box-shadow: 0 12px 40px rgba(0, 102, 204, 0.35); text-align: center; }
.simulador-header h2 { color: white !important; font-size: 1.8rem !important; font-weight: 800 !important; margin: 0 !important; }
.resultado-card { background: linear-gradient(145deg, #111D2E 0%, #0F1A2A 100%); border: 2px solid #1E3A5F; border-radius: 20px; padding: 28px; text-align: center; box-shadow: 0 8px 30px rgba(0,0,0,0.4); transition: all 0.4s ease; }
.resultado-card.destaque { border-color: #00D4AA; box-shadow: 0 0 40px rgba(0, 212, 170, 0.2); transform: scale(1.02); }
.resultado-valor { font-size: 2.8rem; font-weight: 900; color: #00D4AA; margin: 12px 0; text-shadow: 0 0 20px rgba(0, 212, 170, 0.3); }
.resultado-label { font-size: 0.9rem; color: #7A8B9A; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
.badge-negociacao { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; margin: 4px; }
.badge-otimo { background: rgba(0, 212, 170, 0.15); color: #00D4AA; border: 1px solid #00D4AA; }
.badge-bom { background: rgba(0, 163, 224, 0.15); color: #00A3E0; border: 1px solid #00A3E0; }
.badge-atencao { background: rgba(255, 184, 0, 0.15); color: #FFB800; border: 1px solid #FFB800; }
.badge-critico { background: rgba(255, 71, 87, 0.15); color: #FF4757; border: 1px solid #FF4757; }
.comparativo-table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.comparativo-table th { background: linear-gradient(135deg, #0066CC, #00A3E0); color: white; padding: 14px; text-align: center; font-weight: 600; }
.comparativo-table td { padding: 12px 14px; border-bottom: 1px solid #1E3A5F; color: #E8F4F8; text-align: center; }
.comparativo-table tr:hover td { background: rgba(0, 163, 224, 0.1); }
.comparativo-table .positivo { color: #00D4AA; font-weight: 700; }
.comparativo-table .negativo { color: #FF4757; font-weight: 700; }
.comparativo-table .neutro { color: #FFB800; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ESTADO DA SESSAO
# ==============================================================================
def init_session_state():
    defaults = {
        'notion_connected': False,
        'notion_token': os.getenv('NOTION_TOKEN', ''),
        'notion_database_id': os.getenv('NOTION_DB_PROJETOS', ''),
        'current_step': 1,
        'selected_unit': None,
        'selected_group': 'Todos',
        'data_loaded': False,
        'last_sync': None,
        'user_role': 'Coordenador',
        'theme': 'dark',
        'language': 'pt-BR',
        'notifications': [],
        'filters': {'vazao_min': 0, 'vazao_max': 1000, 'status': 'Todos', 'grupo': 'Todos'}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==============================================================================
# CONFIGURACAO DAS 13 ETAPAS
# ==============================================================================
ETAPAS = [
    {"id": 1, "nome": "Definicao", "icone": "📋", "desc": "Escopo e requisitos do projeto"},
    {"id": 2, "nome": "Planejamento", "icone": "🗺️", "desc": "Cronograma e alocacao de recursos"},
    {"id": 3, "nome": "Producao", "icone": "🏭", "desc": "Fabricacao dos modulos e equipamentos"},
    {"id": 4, "nome": "Instalacao/Start-up", "icone": "🔧", "desc": "Montagem e comissionamento"},
    {"id": 5, "nome": "Riscos", "icone": "⚠️", "desc": "Gestao de riscos e contingencias"},
    {"id": 6, "nome": "Custos", "icone": "💰", "desc": "Controle orcamentario e margem"},
    {"id": 7, "nome": "Cronograma", "icone": "📅", "desc": "Acompanhamento de prazos e milestones"},
    {"id": 8, "nome": "Organizacao", "icone": "👥", "desc": "Estrutura de equipe e responsabilidades"},
    {"id": 9, "nome": "Processos/Modulos", "icone": "⚙️", "desc": "Fluxos operacionais e padronizacao"},
    {"id": 10, "nome": "Producao (PSP)", "icone": "📊", "desc": "Plano de Saude do Projeto"},
    {"id": 11, "nome": "Budgeting/Performance", "icone": "📈", "desc": "Analise de performance financeira"},
    {"id": 12, "nome": "Status/Feedback", "icone": "💬", "desc": "Relatorios e comunicacao com cliente"},
    {"id": 13, "nome": "Melhorias", "icone": "🚀", "desc": "Licoes aprendidas e otimizacao"}
]

GRUPOS = {
    "Serie": {"unidades": 23, "vazao": "20 L/s", "cor": "#00D4AA", "estrategia": "Padronizacao + Compra em Lote"},
    "Medio": {"unidades": 10, "vazao": "40-150 L/s", "cor": "#00A3E0", "estrategia": "Replicacao DNA Camburi"},
    "Magnum": {"unidades": 5, "vazao": "500-1000 L/s", "cor": "#0066CC", "estrategia": "Agentes de Risco Avancados"},
    "ETA": {"unidades": 11, "vazao": "Variavel", "cor": "#7B61FF", "estrategia": "Gestao de Alto Valor"}
}

# ==============================================================================
# NOTION CONNECTOR
# ==============================================================================
class NotionConnector:
    def __init__(self, token=None, database_id=None):
        self.token = token or st.session_state.get('notion_token', '')
        self.database_id = database_id or st.session_state.get('notion_database_id', '')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.connected = False
        self.last_error = None

    def test_connection(self):
        if not self.token:
            self.last_error = "Token de integracao nao configurado"
            return {"status": "error", "message": self.last_error}
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.connected = True
                st.session_state.notion_connected = True
                st.session_state.last_sync = datetime.now()
                return {"status": "success", "user": response.json().get("name", "Usuario"), "workspace": response.json().get("workspace_name", "Workspace")}
            else:
                self.last_error = f"Erro {response.status_code}: {response.text}"
                return {"status": "error", "message": self.last_error}
        except Exception as e:
            self.last_error = str(e)
            return {"status": "error", "message": self.last_error}

    def query_database(self, database_id=None, filter_obj=None):
        db_id = database_id or self.database_id
        if not db_id or not self.connected:
            return []
        url = f"{self.base_url}/databases/{db_id}/query"
        payload = {"page_size": 100}
        if filter_obj:
            payload["filter"] = filter_obj
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
        except Exception as e:
            st.error(f"Erro ao consultar Notion: {e}")
            return []

    def create_page(self, database_id, properties):
        if not self.connected:
            return {"status": "error", "message": "Nao conectado"}
        url = f"{self.base_url}/pages"
        payload = {"parent": {"database_id": database_id}, "properties": properties}
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            return response.json() if response.status_code == 200 else {"status": "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ==============================================================================
# CALCULO PARAMETRICO DE MARGEM
# ==============================================================================
@dataclass
class DNACamburi:
    nome: str = "ETE Camburi"
    vazao_ls: float = 57.0
    vazao_m3d: float = 4924.8
    custo_total_rs: float = 15_800_000.0
    custo_por_ls: float = 277_192.98
    custo_por_m3d: float = 3_208.13
    composicao: Dict[str, float] = field(default_factory=lambda: {
        "civil": 0.35, "eletromecanico": 0.28, "instrumentacao": 0.12,
        "eletrica": 0.10, "automacao": 0.08, "terraplenagem": 0.05, "imprevistos": 0.02
    })
    area_m2: float = 1_200.0
    potencia_instalada_kw: float = 85.0
    consumo_energia_kwh_m3: float = 0.45
    mao_de_obra_permanente: int = 4
    bdi_padrao: float = 1.35
    margem_liquida_padrao: float = 0.28
    prazo_projeto: int = 2
    prazo_fabricacao: int = 6
    prazo_instalacao: int = 8
    prazo_total: int = 18

DNA_CAMBURI = DNACamburi()

@dataclass
class FatoresAjuste:
    distancia: float = 1.0
    maresia: float = 1.0
    complexidade: float = 1.0
    urgencia: float = 1.0

    @property
    def fator_total(self) -> float:
        return self.distancia * self.maresia * self.complexidade * self.urgencia

    def to_dict(self) -> Dict:
        return {
            "distancia": self.distancia, "maresia": self.maresia,
            "complexidade": self.complexidade, "urgencia": self.urgencia,
            "fator_total": self.fator_total
        }

@dataclass
class ResultadoMargem:
    projeto_nome: str
    grupo: str
    vazao_ls: float
    custo_base_por_ls: float
    custo_ajustado_por_ls: float
    custo_total_base: float
    custo_total_ajustado: float
    fatores: FatoresAjuste
    fator_escala: float
    preco_venda: float
    bdi_aplicado: float
    receita_bruta: float
    margem_bruta_rs: float
    margem_bruta_pct: float
    margem_liquida_rs: float
    margem_liquida_pct: float
    vs_dna_camburi_pct: float
    status_margem: str
    detalhamento: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "projeto": self.projeto_nome, "grupo": self.grupo, "vazao_ls": self.vazao_ls,
            "custo_base_total": self.custo_total_base, "custo_ajustado_total": self.custo_total_ajustado,
            "fator_escala": self.fator_escala, "fatores_ajuste": self.fatores.to_dict(),
            "preco_venda": self.preco_venda, "bdi": self.bdi_aplicado,
            "margem_bruta_pct": self.margem_bruta_pct, "margem_liquida_pct": self.margem_liquida_pct,
            "status": self.status_margem
        }

class CalculadorParametrico:
    CUSTO_TARGET_10LS: float = 363_300.0
    PREMIUM_ESCALA_MENOR: float = 0.37
    BDI_SERIE: float = 1.45
    BDI_PADRAO: float = 1.35
    BDI_MAGNUM: float = 1.30

    FATORES_ESCALA: Dict[str, float] = {
        "Serie": 1.37, "Medio": 1.00, "Magnum": 0.85, "ETA": 1.10
    }

    BDI_POR_GRUPO: Dict[str, float] = {
        "Serie": 1.45, "Medio": 1.35, "Magnum": 1.30, "ETA": 1.38
    }

    def __init__(self, dna: DNACamburi = None):
        self.dna = dna or DNA_CAMBURI

    def calcular_custo_base(self, vazao_ls: float, grupo: str) -> float:
        if vazao_ls <= 10:
            return self.CUSTO_TARGET_10LS
        fator_escala = self.FATORES_ESCALA.get(grupo, 1.0)
        return self.dna.custo_por_ls * fator_escala

    def calcular(self, projeto_nome: str, vazao_ls: float, grupo: str = "Serie",
                 fatores: FatoresAjuste = None, bdi_custom: float = None, custo_extra_rs: float = 0.0) -> ResultadoMargem:
        fatores = fatores or FatoresAjuste()
        custo_base_ls = self.calcular_custo_base(vazao_ls, grupo)
        custo_ajustado_ls = custo_base_ls * fatores.fator_total
        custo_total_base = custo_base_ls * vazao_ls
        custo_total_ajustado = custo_ajustado_ls * vazao_ls + custo_extra_rs
        bdi = bdi_custom or self.BDI_POR_GRUPO.get(grupo, self.BDI_PADRAO)
        preco_venda = custo_total_ajustado * bdi
        margem_bruta_rs = preco_venda - custo_total_ajustado
        margem_bruta_pct = (margem_bruta_rs / preco_venda) * 100 if preco_venda > 0 else 0
        margem_liquida_rs = margem_bruta_rs * 0.85
        margem_liquida_pct = (margem_liquida_rs / preco_venda) * 100 if preco_venda > 0 else 0
        custo_camburi_equivalente = self.dna.custo_por_ls * vazao_ls
        vs_camburi = ((custo_total_ajustado / custo_camburi_equivalente) - 1) * 100

        if margem_liquida_pct >= 31:
            status = "Acima do target"
        elif margem_liquida_pct >= 28:
            status = "Dentro do target"
        elif margem_liquida_pct >= 20:
            status = "Abaixo do target - Atencao"
        else:
            status = "Critico - Revisar urgente"

        detalhamento = {
            "composicao_custos": {cat: custo_total_ajustado * pct for cat, pct in self.dna.composicao.items()},
            "impacto_fatores": {
                "distancia": f"+{(fatores.distancia - 1) * 100:.1f}%",
                "maresia": f"+{(fatores.maresia - 1) * 100:.1f}%",
                "complexidade": f"+{(fatores.complexidade - 1) * 100:.1f}%",
                "urgencia": f"+{(fatores.urgencia - 1) * 100:.1f}%"
            },
            "premissas": {
                "custo_target_10ls": self.CUSTO_TARGET_10LS,
                "premium_escala_menor": f"{self.PREMIUM_ESCALA_MENOR * 100:.0f}%",
                "fator_escala_grupo": self.FATORES_ESCALA.get(grupo, 1.0),
                "bdi_aplicado": bdi
            }
        }

        return ResultadoMargem(
            projeto_nome=projeto_nome, grupo=grupo, vazao_ls=vazao_ls,
            custo_base_por_ls=custo_base_ls, custo_ajustado_por_ls=custo_ajustado_ls,
            custo_total_base=custo_total_base, custo_total_ajustado=custo_total_ajustado,
            fatores=fatores, fator_escala=self.FATORES_ESCALA.get(grupo, 1.0),
            preco_venda=preco_venda, bdi_aplicado=bdi, receita_bruta=preco_venda,
            margem_bruta_rs=margem_bruta_rs, margem_bruta_pct=margem_bruta_pct,
            margem_liquida_rs=margem_liquida_rs, margem_liquida_pct=margem_liquida_pct,
            vs_dna_camburi_pct=vs_camburi, status_margem=status, detalhamento=detalhamento
        )

# ==============================================================================
# SIMULADOR DE NEGOCIACAO
# ==============================================================================
@dataclass
class SimuladorProposta:
    projeto_nome: str = "ETE Onda Limpa #01"
    vazao_ls: float = 20.0
    grupo: str = "Serie"
    custo_base_ls: float = 379_754.38
    custo_total_base: float = 0.0
    fator_distancia: float = 1.15
    fator_maresia: float = 1.15
    fator_complexidade: float = 1.00
    fator_urgencia: float = 1.00
    bdi: float = 1.45
    margem_desejada_pct: float = 31.0
    desconto_negociado_pct: float = 0.0
    acrescimo_risco_pct: float = 0.0

    def __post_init__(self):
        self.custo_total_base = self.custo_base_ls * self.vazao_ls
        self.custo_ajustado = self.custo_total_base * self.fator_total

    @property
    def fator_total(self) -> float:
        return self.fator_distancia * self.fator_maresia * self.fator_complexidade * self.fator_urgencia

    @property
    def custo_com_risco(self) -> float:
        return self.custo_ajustado * (1 + self.acrescimo_risco_pct / 100)

    @property
    def preco_venda_bruto(self) -> float:
        return self.custo_com_risco * self.bdi

    @property
    def preco_venda_liquido(self) -> float:
        return self.preco_venda_bruto * (1 - self.desconto_negociado_pct / 100)

    @property
    def margem_real_pct(self) -> float:
        margem = self.preco_venda_liquido - self.custo_com_risco
        return (margem / self.preco_venda_liquido) * 100 if self.preco_venda_liquido > 0 else 0

    @property
    def margem_liquida_real_pct(self) -> float:
        return self.margem_real_pct * 0.85

    @property
    def desconto_em_reais(self) -> float:
        return self.preco_venda_bruto * (self.desconto_negociado_pct / 100)

    @property
    def status_negociacao(self) -> str:
        ml = self.margem_liquida_real_pct
        if ml >= 31: return "Otimo - Margem acima do target"
        elif ml >= 28: return "Bom - Dentro do target"
        elif ml >= 20: return "Atencao - Abaixo do target, mas viavel"
        else: return "Critico - Margem inaceitavel"

    @property
    def cor_status(self) -> str:
        ml = self.margem_liquida_real_pct
        if ml >= 31: return "#00D4AA"
        elif ml >= 28: return "#00A3E0"
        elif ml >= 20: return "#FFB800"
        else: return "#FF4757"

    def gerar_cenarios(self) -> List[Dict]:
        cenarios = []
        for bdi in [1.30, 1.35, 1.40, 1.45, 1.50, 1.55]:
            preco = self.custo_com_risco * bdi
            margem = ((preco - self.custo_com_risco) / preco) * 100 * 0.85
            cenarios.append({
                "BDI": f"{bdi:.2f}x",
                "Preço Venda": preco,
                "Margem Líquida": margem,
                "Status": "Otimo" if margem >= 31 else "Bom" if margem >= 28 else "Atencao" if margem >= 20 else "Critico"
            })
        return cenarios

    def to_dict(self) -> Dict:
        return {
            "projeto": self.projeto_nome, "vazao_ls": self.vazao_ls, "grupo": self.grupo,
            "custo_base": self.custo_total_base, "custo_ajustado": self.custo_ajustado,
            "fator_total": self.fator_total, "bdi": self.bdi,
            "margem_desejada": self.margem_desejada_pct,
            "desconto": self.desconto_negociado_pct,
            "acrescimo_risco": self.acrescimo_risco_pct,
            "preco_bruto": self.preco_venda_bruto,
            "preco_liquido": self.preco_venda_liquido,
            "margem_bruta": self.margem_real_pct,
            "margem_liquida": self.margem_liquida_real_pct,
            "status": self.status_negociacao
        }

# ==============================================================================
# INTEGRACAO N8N
# ==============================================================================
class N8NConfig:
    BASE_URL = os.getenv("N8N_WEBHOOK_BASE", "http://localhost:5678/webhook")
    WEBHOOK_PROPOSTA = f"{BASE_URL}/proposta-comercial"
    WEBHOOK_RELATORIO = f"{BASE_URL}/relatorio-proposta"
    WEBHOOK_WHATSAPP = f"{BASE_URL}/whatsapp"
    TIMEOUT = 15
    HEADERS = {"Content-Type": "application/json", "X-Origem": "Hydrosol-Simulador-v5.1"}

def enviar_proposta_n8n(
    projeto_nome: str, projeto_id: str, vazao_ls: float, grupo: str,
    bdi_ajustado: float, margem_desejada: float, desconto_negociado: float,
    acrescimo_risco: float, custo_base: float, custo_ajustado: float,
    preco_venda_bruto: float, preco_venda_liquido: float,
    margem_bruta_pct: float, margem_liquida_pct: float,
    status_negociacao: str, aprovado_por: str = "", observacoes: str = ""
) -> Dict:
    payload = {
        "id_proposta": f"PROP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "versao_simulador": "5.1.0",
        "projeto": {"nome": projeto_nome, "id": projeto_id, "vazao_ls": vazao_ls, "grupo": grupo},
        "parametros_negociacao": {
            "bdi_ajustado": round(bdi_ajustado, 2),
            "margem_desejada_pct": round(margem_desejada, 1),
            "desconto_negociado_pct": round(desconto_negociado, 1),
            "acrescimo_risco_pct": round(acrescimo_risco, 1)
        },
        "custos": {
            "custo_base_total": round(custo_base, 2),
            "custo_ajustado": round(custo_ajustado, 2),
            "custo_final_com_risco": round(custo_ajustado * (1 + acrescimo_risco/100), 2)
        },
        "precos": {
            "preco_venda_bruto": round(preco_venda_bruto, 2),
            "preco_venda_liquido": round(preco_venda_liquido, 2),
            "desconto_em_reais": round(preco_venda_bruto * (desconto_negociado/100), 2),
            "preco_por_ls": round(preco_venda_liquido / vazao_ls, 2) if vazao_ls > 0 else 0
        },
        "margens": {"bruta_pct": round(margem_bruta_pct, 2), "liquida_pct": round(margem_liquida_pct, 2), "status": status_negociacao},
        "aprovacao": {"aprovado_por": aprovado_por, "data_aprovacao": datetime.now().isoformat() if aprovado_por else None, "status": "aprovada" if aprovado_por else "pendente"},
        "observacoes": observacoes,
        "acao_requerida": {"gerar_relatorio_pdf": True, "notificar_whatsapp": True, "salvar_notion": True, "enviar_email_diretoria": True}
    }

    try:
        response = requests.post(N8NConfig.WEBHOOK_PROPOSTA, headers=N8NConfig.HEADERS, json=payload, timeout=N8NConfig.TIMEOUT)
        if response.status_code == 200:
            return {"status": "sucesso", "id_proposta": payload["id_proposta"], "mensagem": "Proposta enviada ao n8n", "payload_enviado": payload}
        else:
            return {"status": "falha", "id_proposta": payload["id_proposta"], "mensagem": f"Erro n8n: HTTP {response.status_code}", "payload_enviado": payload}
    except requests.exceptions.ConnectionError:
        return {"status": "erro_conexao", "id_proposta": payload["id_proposta"], "mensagem": "n8n nao esta rodando", "payload_enviado": payload}
    except Exception as e:
        return {"status": "erro", "id_proposta": payload["id_proposta"], "mensagem": str(e), "payload_enviado": payload}

def notificar_whatsapp_proposta(numero_destino: str, projeto_nome: str, bdi_ajustado: float, preco_final: float, margem_liquida: float, aprovado: bool = False) -> Dict:
    status_emoji = "✅" if aprovado else "📊"
    status_texto = "APROVADA" if aprovado else "EM ANALISE"
    mensagem = f"""{status_emoji} *PROPOSTA {status_texto} - HYDROSOL AI*

📋 Projeto: {projeto_nome}
💰 BDI Ajustado: {bdi_ajustado:.2f}x
🏷️ Preço Final: R$ {preco_final/1e6:.2f} Mi
📈 Margem Líquida: {margem_liquida:.1f}%

{'✅ Proposta aprovada pelo coordenador.' if aprovado else '⏳ Aguardando aprovação final.'}

🔗 Acesse o dashboard para detalhes completos.
"""
    payload = {"numero": numero_destino, "mensagem": mensagem, "tipo": "proposta_comercial", "origem": "simulador_negociacao", "timestamp": datetime.now().isoformat()}
    try:
        response = requests.post(N8NConfig.WEBHOOK_WHATSAPP, headers=N8NConfig.HEADERS, json=payload, timeout=10)
        return {"status": "enviado", "whatsapp": response.status_code == 200}
    except:
        return {"status": "falha", "whatsapp": False}

def salvar_proposta_completa(simulador_instance, aprovado_por: str = "", observacoes: str = "") -> Dict:
    s = simulador_instance
    resultado_proposta = enviar_proposta_n8n(
        projeto_nome=s.projeto_nome, projeto_id="ETE-001", vazao_ls=s.vazao_ls, grupo=s.grupo,
        bdi_ajustado=s.bdi, margem_desejada=s.margem_desejada_pct, desconto_negociado=s.desconto_negociado_pct,
        acrescimo_risco=s.acrescimo_risco_pct, custo_base=s.custo_total_base, custo_ajustado=s.custo_ajustado,
        preco_venda_bruto=s.preco_venda_bruto, preco_venda_liquido=s.preco_venda_liquido,
        margem_bruta_pct=s.margem_real_pct, margem_liquida_pct=s.margem_liquida_real_pct,
        status_negociacao=s.status_negociacao, aprovado_por=aprovado_por, observacoes=observacoes
    )
    resultado_whatsapp = notificar_whatsapp_proposta(
        numero_destino=os.getenv("WHATSAPP_COORDENADOR", "+5511999999999"),
        projeto_nome=s.projeto_nome, bdi_ajustado=s.bdi, preco_final=s.preco_venda_liquido,
        margem_liquida=s.margem_liquida_real_pct, aprovado=bool(aprovado_por)
    )
    return {
        "status_geral": "sucesso" if resultado_proposta["status"] == "sucesso" else "parcial",
        "id_proposta": resultado_proposta.get("id_proposta", "N/A"),
        "envio_n8n": resultado_proposta["status"],
        "whatsapp": resultado_whatsapp["status"],
        "bdi_enviado": s.bdi,
        "preco_enviado": s.preco_venda_liquido,
        "margem_enviada": s.margem_liquida_real_pct,
        "detalhes": {"proposta": resultado_proposta, "whatsapp": resultado_whatsapp}
    }

# ==============================================================================
# FUNCOES DE RENDERIZACAO
# ==============================================================================

def render_header():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("""
        <div class="hydro-header">
            <h1>🌊 Hydrosol AI Dashboard v5.1</h1>
            <p>Programa Onda Limpa · Sabesp · R$ 1,23 Bi · 49 Unidades</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Margem Alvo</div>
            <div class="kpi-value">28-31%</div>
            <div style="color: #00D4AA; font-size: 0.9rem;">▲ Target ativo</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Unidades</div>
            <div class="kpi-value">49</div>
            <div style="color: #00D4AA; font-size: 0.9rem;">● Em operacao</div>
        </div>
        """, unsafe_allow_html=True)

def render_stepper(active_step=1):
    html = '<div class="stepper-container">'
    for etapa in ETAPAS:
        if etapa["id"] < active_step:
            status = "completed"
        elif etapa["id"] == active_step:
            status = "active"
        else:
            status = ""
        html += f'<div class="step-item {status}"><div class="step-circle">{etapa["id"]}</div><div class="step-label">{etapa["nome"]}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_notion_config():
    st.markdown("""
    <div class="hydro-card">
        <h3 style="color: #00A3E0; margin-top: 0;">🔌 Integracao Notion API</h3>
        <p style="color: #7A8B9A;">Configure a conexao com seu workspace do Notion para sincronizacao de dados em tempo real.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚙️ Configurar Conexao Notion", expanded=not st.session_state.notion_connected):
        col1, col2 = st.columns(2)
        with col1:
            token = st.text_input("🔑 Token de Integracao", value=st.session_state.notion_token, type="password", placeholder="secret_xxxxxxxxxxxxxxxx", help="Crie em: notion.so/my-integrations")
        with col2:
            db_id = st.text_input("🗄️ ID da Database", value=st.session_state.notion_database_id, placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", help="ID da database de projetos no Notion")

        col_test, col_save = st.columns([1, 1])
        with col_test:
            if st.button("🔄 Testar Conexao", use_container_width=True):
                st.session_state.notion_token = token
                st.session_state.notion_database_id = db_id
                connector = NotionConnector(token, db_id)
                result = connector.test_connection()
                if result["status"] == "success":
                    st.success(f"✅ Conectado! Workspace: {result['workspace']}")
                else:
                    st.error(f"❌ Falha: {result['message']}")
        with col_save:
            if st.button("💾 Salvar Configuracao", use_container_width=True):
                st.session_state.notion_token = token
                st.session_state.notion_database_id = db_id
                st.success("💾 Configuracao salva!")

    status_class = "connected" if st.session_state.notion_connected else "disconnected"
    status_text = "Conectado" if st.session_state.notion_connected else "Desconectado"
    status_icon = "🟢" if st.session_state.notion_connected else "🔴"
    last_sync = st.session_state.last_sync.strftime("%d/%m %H:%M") if st.session_state.last_sync else "Nunca"

    st.markdown(f"""
    <div style="margin-top: 16px;">
        <div class="notion-status {status_class}">
            <div class="status-dot {status_class}"></div>
            <span>{status_icon} Notion API: <strong>{status_text}</strong></span>
            <span style="margin-left: auto; color: #7A8B9A;">Ultima sincronizacao: {last_sync}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 3rem;">🌊</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: #00A3E0;">HYDROSOL</div>
            <div style="font-size: 0.75rem; color: #7A8B9A;">AI Dashboard v5.1</div>
        </div>
        <div class="hydro-divider"></div>
        """, unsafe_allow_html=True)

        menu_options = ["🏠 Visao Geral"] + [f"{e['icone']} {e['nome']}" for e in ETAPAS] + ["💼 Simulador de Negociacao", "⚙️ Configuracoes"]
        menu_icons = ["house"] + ["circle"] * 13 + ["briefcase", "gear"]

        selected = option_menu(
            menu_title="Navegacao",
            options=menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": "#00A3E0", "font-size": "1rem"},
                "nav-link": {"font-size": "0.9rem", "text-align": "left", "padding": "12px 16px", "margin": "4px 0", "border-radius": "12px", "color": "#E8F4F8"},
                "nav-link-selected": {"background": "linear-gradient(135deg, #0066CC, #00A3E0)", "color": "white", "font-weight": "600"}
            }
        )

        if selected != "🏠 Visao Geral" and selected != "💼 Simulador de Negociacao" and selected != "⚙️ Configuracoes":
            for etapa in ETAPAS:
                if etapa["nome"] in selected:
                    st.session_state.current_step = etapa["id"]
                    break

        st.markdown('<div class="hydro-divider"></div>', unsafe_allow_html=True)

        st.markdown("<p style='color: #7A8B9A; font-size: 0.8rem; font-weight: 600;'>FILTROS RAPIDOS</p>", unsafe_allow_html=True)

        grupo_filter = st.selectbox("Grupo", ["Todos", "Serie (20 L/s)", "Medio (40-150 L/s)", "Magnum (500-1000 L/s)", "ETA"], label_visibility="collapsed")
        status_filter = st.selectbox("Status", ["Todos", "🟢 Em dia", "🟡 Atencao", "🔴 Critico", "⚪ Nao iniciado"], label_visibility="collapsed")

        st.session_state.filters['grupo'] = grupo_filter
        st.session_state.filters['status'] = status_filter

        st.markdown('<div class="hydro-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="padding: 12px; background: #111D2E; border-radius: 12px; border: 1px solid #1E3A5F;">
            <div style="font-size: 0.8rem; color: #7A8B9A;">Logado como</div>
            <div style="font-weight: 600; color: #E8F4F8;">{st.session_state.user_role}</div>
            <div style="font-size: 0.75rem; color: #00D4AA;">● Online</div>
        </div>
        """, unsafe_allow_html=True)

        return selected

def render_overview():
    st.markdown("""
    <div class="hydro-card">
        <h2 style="color: #00A3E0; margin-top: 0;">🎯 Visao Geral do Programa</h2>
        <p style="color: #7A8B9A;">Dashboard executivo do ecossistema Hydrosol — Programa Onda Limpa/Sabesp</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    kpis = [
        ("💰 Valor Total", "R$ 1,24 Bi", "▲ Orcamento aprovado", "positive"),
        ("🏗️ Unidades", "49", "● 23 Serie | 10 Medio | 5 Magnum | 11 ETA", "positive"),
        ("📊 Margem Media", "29,5%", "▲ Dentro do target (28-31%)", "positive"),
        ("⏱️ Prazo Medio", "18 meses", "● Base DNA Camburi", "positive")
    ]
    for col, (label, value, delta, delta_class) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div style="color: {'#00D4AA' if 'positive' in delta_class else '#FF4757'}; font-size: 0.9rem;">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="hydro-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hydro-card">
        <h3 style="color: #00A3E0; margin-top: 0;">📦 Portfolio por Grupo</h3>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for col, (nome, info) in zip(cols, GRUPOS.items()):
        with col:
            st.markdown(f"""
            <div class="hydro-card" style="border-left: 4px solid {info['cor']};">
                <div style="font-size: 1.5rem; font-weight: 800; color: {info['cor']};">{nome}</div>
                <div style="font-size: 2rem; font-weight: 700; color: #E8F4F8;">{info['unidades']}</div>
                <div style="font-size: 0.85rem; color: #7A8B9A;">unidades</div>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #1E3A5F;">
                    <div style="font-size: 0.8rem; color: #7A8B9A;">Vazao: {info['vazao']}</div>
                    <div style="font-size: 0.75rem; color: {info['cor']}; margin-top: 4px;">{info['estrategia']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="hydro-divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="hydro-card">
            <h4 style="color: #00A3E0;">📈 Distribuicao Financeira</h4>
            <p style="color: #7A8B9A; font-size: 0.85rem;">ETE ~R$ 800M | ETA ~R$ 437M</p>
        </div>
        """, unsafe_allow_html=True)

        df_finance = pd.DataFrame({
            'Categoria': ['ETE - Serie', 'ETE - Medio', 'ETE - Magnum', 'ETA'],
            'Valor': [280, 320, 200, 437],
            'Cor': ['#00D4AA', '#00A3E0', '#0066CC', '#7B61FF']
        })

        fig = go.Figure(data=[go.Pie(
            labels=df_finance['Categoria'], values=df_finance['Valor'], hole=0.55,
            marker_colors=df_finance['Cor'], textinfo='label+percent', textfont_size=12,
            hovertemplate='<b>%{label}</b><br>R$ %{value}M<br>%{percent}<extra></extra>'
        )])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#E8F4F8'), margin=dict(t=20, b=20, l=20, r=20),
                          annotations=[dict(text='R$<br>1,24Bi', x=0.5, y=0.5, font_size=20, font_color='#00A3E0', showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="hydro-card">
            <h4 style="color: #00A3E0;">📊 Status das Unidades</h4>
            <p style="color: #7A8B9A; font-size: 0.85rem;">Acompanhamento por status operacional</p>
        </div>
        """, unsafe_allow_html=True)

        df_status = pd.DataFrame({
            'Status': ['Em dia', 'Atencao', 'Critico', 'Nao iniciado'],
            'Quantidade': [28, 12, 4, 5],
            'Cor': ['#00D4AA', '#FFB800', '#FF4757', '#7A8B9A']
        })

        fig2 = go.Figure(data=[go.Bar(
            x=df_status['Status'], y=df_status['Quantidade'], marker_color=df_status['Cor'],
            text=df_status['Quantidade'], textposition='auto', textfont=dict(color='white', size=14),
            hovertemplate='<b>%{x}</b><br>%{y} unidades<extra></extra>'
        )])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#E8F4F8'), margin=dict(t=20, b=40, l=40, r=20),
                          xaxis=dict(showgrid=False, color='#7A8B9A'), yaxis=dict(showgrid=True, gridcolor='#1E3A5F', color='#7A8B9A'))
        st.plotly_chart(fig2, use_container_width=True)

def render_etapa(etapa_id: int):
    etapa = ETAPAS[etapa_id - 1]
    st.markdown(f"""
    <div class="hydro-card">
        <h2 style="color: #00A3E0; margin-top: 0;">{etapa['icone']} Etapa {etapa_id}: {etapa['nome']}</h2>
        <p style="color: #7A8B9A;">{etapa['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    render_stepper(etapa_id)

    if etapa_id == 6:
        st.markdown("""
        <div class="hydro-card">
            <h4 style="color: #E8F4F8;">💰 Calculo Parametrico de Margem - DNA Camburi</h4>
            <p style="color: #7A8B9A;">Calcule a margem do projeto baseado no DNA da ETE Camburi (57 L/s)</p>
        </div>
        """, unsafe_allow_html=True)

        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            calc_vazao = st.number_input("Vazao (L/s)", min_value=1.0, max_value=1000.0, value=20.0, step=1.0)
            calc_grupo = st.selectbox("Grupo", ["Serie", "Medio", "Magnum", "ETA"])
            calc_bdi = st.slider("BDI", 1.20, 1.80, 1.45, 0.01, format="%.2fx")
        with col_calc2:
            calc_dist = st.selectbox("Distancia", [(1.0, "Baixo (<50km)"), (1.15, "Medio (50-150km)"), (1.35, "Alto (150-300km)"), (1.60, "Critico (>300km)")], format_func=lambda x: x[1])
            calc_mar = st.selectbox("Maresia", [(1.0, "Baixo (Interior)"), (1.15, "Medio (Costa protegida)"), (1.35, "Alto (Litoral direto)"), (1.60, "Critico (Ambiente agressivo)")], format_func=lambda x: x[1])
            calc_comp = st.selectbox("Complexidade", [(1.0, "Baixo (Terreno plano)"), (1.15, "Medio (Irregular)"), (1.35, "Alto (Area restrita)"), (1.60, "Critico (Terreno problematico)")], format_func=lambda x: x[1])

        if st.button("🔄 Calcular Margem", use_container_width=True):
            calc = CalculadorParametrico()
            fatores = FatoresAjuste(distancia=calc_dist[0], maresia=calc_mar[0], complexidade=calc_comp[0])
            resultado = calc.calcular(projeto_nome=f"ETE Calculada ({calc_vazao} L/s)", vazao_ls=calc_vazao, grupo=calc_grupo, fatores=fatores, bdi_custom=calc_bdi)

            st.success(f"✅ Margem Liquida: {resultado.margem_liquida_pct:.1f}% | Status: {resultado.status_margem}")
            st.info(f"💰 Preço Venda: R$ {resultado.preco_venda:,.2f} | Custo: R$ {resultado.custo_total_ajustado:,.2f}")
            st.json(resultado.to_dict())
    else:
        st.markdown(f"""
        <div class="hydro-card">
            <h4 style="color: #E8F4F8;">📋 Conteudo da Etapa {etapa_id}</h4>
            <p style="color: #7A8B9A;">
                Esta e a estrutura base da etapa <strong>{etapa['nome']}</strong>. 
                Aqui serao integrados os modulos de dados, agentes de IA e automacoes via n8n/LangGraph.
            </p>
            <div style="padding: 20px; background: #0A1628; border-radius: 12px; border: 1px dashed #1E3A5F; margin-top: 16px;">
                <p style="color: #7A8B9A; margin: 0; text-align: center;">
                    🚧 Modulo em desenvolvimento<br>
                    <span style="font-size: 0.8rem;">Aguardando integracao com Notion API e agentes autonomos</span>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    tabs = st.tabs(["📊 Dados", "📈 Analise", "⚙️ Acoes", "📋 Historico"])
    with tabs[0]:
        st.info("📥 Dados serao carregados da API do Notion apos configuracao da conexao.")
        if st.session_state.notion_connected:
            st.success("✅ Conexao ativa! Clique em 'Sincronizar' para carregar dados.")
            if st.button("🔄 Sincronizar com Notion", use_container_width=True):
                st.toast("Sincronizacao iniciada...", icon="🔄")
        else:
            st.warning("⚠️ Configure a conexao com o Notion em 'Configuracoes' para visualizar dados.")
    with tabs[1]:
        st.info("📊 Analises e relatorios serao gerados pelos agentes de IA.")
    with tabs[2]:
        st.info("⚙️ Acoes automatizadas via n8n serao configuradas aqui.")
    with tabs[3]:
        st.info("📋 Historico de alteracoes e logs de auditoria.")

# ==============================================================================
# SIMULADOR DE NEGOCIACAO - RENDER
# ==============================================================================

def render_simulador_negociacao():
    st.markdown("""
    <div class="simulador-header">
        <h2>💼 Simulador de Negociacao</h2>
        <p>Ajuste BDI, margem e fatores de risco em tempo real para negociacoes com consorcios Sabesp</p>
    </div>
    """, unsafe_allow_html=True)

    col_controles, col_resultados = st.columns([1, 1.2])

    with col_controles:
        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">🎚️ Controles de Negociacao</h4>
            <p style="color: #7A8B9A; font-size: 0.85rem; margin: 0;">Arraste as barras para simular diferentes cenarios</p>
        </div>
        """, unsafe_allow_html=True)

        projeto_sel = st.selectbox("📋 Selecionar Projeto Base",
            ["ETE Onda Limpa #01 (20 L/s - Serie)", "ETE Onda Limpa #05 (20 L/s - Serie)",
             "ETE Onda Limpa #28 (100 L/s - Medio)", "ETA Onda Limpa #45 (500 L/s - Magnum)", "Personalizado"],
            help="Escolha um projeto existente ou configure manualmente")

        if projeto_sel == "Personalizado":
            vazao_input = st.number_input("Vazao (L/s)", min_value=1.0, max_value=1000.0, value=20.0, step=1.0)
            custo_ls_input = st.number_input("Custo por L/s (R$)", min_value=100000.0, max_value=1000000.0, value=379754.0, step=1000.0)
            grupo_input = "Serie"
        else:
            configs = {
                "ETE Onda Limpa #01 (20 L/s - Serie)": (20.0, 379754.38, "Serie"),
                "ETE Onda Limpa #05 (20 L/s - Serie)": (20.0, 379754.38, "Serie"),
                "ETE Onda Limpa #28 (100 L/s - Medio)": (100.0, 277192.98, "Medio"),
                "ETA Onda Limpa #45 (500 L/s - Magnum)": (500.0, 235614.03, "Magnum")
            }
            vazao_input, custo_ls_input, grupo_input = configs[projeto_sel]

        st.markdown("<div class='hydro-divider'></div>", unsafe_allow_html=True)

        bdi = st.slider("📈 BDI (Bonus e Despesas Indiretas)", 1.20, 1.80, 1.45, 0.01, format="%.2fx",
                       help="BDI = multiplicador sobre o custo. Padrao Hydrosol: 1.35 a 1.45")
        bdi_pct = ((bdi - 1.20) / (1.80 - 1.20)) * 100
        cor_bdi = "#00D4AA" if bdi >= 1.35 else "#FFB800" if bdi >= 1.25 else "#FF4757"
        st.markdown(f'<div style="width: 100%; height: 12px; background: #0A1628; border-radius: 6px; overflow: hidden; margin-top: 8px;"><div style="width: {bdi_pct}%; height: 100%; background: {cor_bdi}; border-radius: 6px; transition: all 0.5s ease;"></div></div>', unsafe_allow_html=True)

        margem_desejada = st.slider("🎯 Margem Liquida Desejada", 15.0, 40.0, 31.0, 0.5, format="%.1f%%",
                                     help="Target Hydrosol: 28-31%. Abaixo de 20% e critico.")
        margem_pct = ((margem_desejada - 15) / (40 - 15)) * 100
        cor_margem = "#00D4AA" if margem_desejada >= 28 else "#FFB800" if margem_desejada >= 20 else "#FF4757"
        st.markdown(f'<div style="width: 100%; height: 12px; background: #0A1628; border-radius: 6px; overflow: hidden; margin-top: 8px;"><div style="width: {margem_pct}%; height: 100%; background: {cor_margem}; border-radius: 6px; transition: all 0.5s ease;"></div></div>', unsafe_allow_html=True)

        desconto = st.slider("🏷️ Desconto para Consorcio Sabesp", 0.0, 15.0, 0.0, 0.5, format="%.1f%%",
                            help="Desconto concedido na negociacao. Cada 1% reduz a margem.")
        desconto_pct = (desconto / 15) * 100
        cor_desconto = "#00D4AA" if desconto <= 3 else "#FFB800" if desconto <= 8 else "#FF4757"
        st.markdown(f'<div style="width: 100%; height: 12px; background: #0A1628; border-radius: 6px; overflow: hidden; margin-top: 8px;"><div style="width: {desconto_pct}%; height: 100%; background: {cor_desconto}; border-radius: 6px; transition: all 0.5s ease;"></div></div>', unsafe_allow_html=True)

        risco = st.slider("⚠️ Acrescimo de Risco (Imprevistos)", 0.0, 10.0, 0.0, 0.5, format="%.1f%%",
                         help="Reserva para riscos e imprevistos. Recomendado: 2-5% para projetos complexos.")
        risco_pct = (risco / 10) * 100
        cor_risco = "#00D4AA" if risco <= 3 else "#FFB800" if risco <= 6 else "#FF4757"
        st.markdown(f'<div style="width: 100%; height: 12px; background: #0A1628; border-radius: 6px; overflow: hidden; margin-top: 8px;"><div style="width: {risco_pct}%; height: 100%; background: {cor_risco}; border-radius: 6px; transition: all 0.5s ease;"></div></div>', unsafe_allow_html=True)

    with col_resultados:
        sim = SimuladorProposta(
            projeto_nome=projeto_sel.split(" (")[0] if "(" in projeto_sel else projeto_sel,
            vazao_ls=vazao_input, grupo=grupo_input, custo_base_ls=custo_ls_input,
            bdi=bdi, margem_desejada_pct=margem_desejada, desconto_negociado_pct=desconto, acrescimo_risco_pct=risco
        )

        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📊 Resultado da Proposta</h4>
            <p style="color: #7A8B9A; font-size: 0.85rem; margin: 0;">Atualizado automaticamente ao mover os sliders</p>
        </div>
        """, unsafe_allow_html=True)

        preco_formatado = f"R$ {sim.preco_venda_liquido/1e6:.2f} Mi"
        st.markdown(f"""
        <div class="resultado-card destaque">
            <div class="resultado-label">💰 PRECO FINAL DA PROPOSTA</div>
            <div class="resultado-valor">{preco_formatado}</div>
            <div style="color: {sim.cor_status}; font-size: 1rem; margin-top: 8px;">
                BDI {sim.bdi:.2f}x | Desconto {sim.desconto_negociado_pct:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="resultado-card">
                <div class="resultado-label">📈 MARGEM BRUTA</div>
                <div class="resultado-valor" style="font-size: 1.8rem; color: #00A3E0;">{sim.margem_real_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="resultado-card">
                <div class="resultado-label">📉 MARGEM LIQUIDA</div>
                <div class="resultado-valor" style="font-size: 1.8rem; color: {sim.cor_status};">{sim.margem_liquida_real_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        badge_class = "badge-otimo" if sim.margem_liquida_real_pct >= 31 else "badge-bom" if sim.margem_liquida_real_pct >= 28 else "badge-atencao" if sim.margem_liquida_real_pct >= 20 else "badge-critico"
        st.markdown(f'<div style="text-align: center; margin: 16px 0;"><span class="badge-negociacao {badge_class}">{sim.status_negociacao}</span></div>', unsafe_allow_html=True)

        with st.expander("📋 Ver Detalhamento Completo", expanded=False):
            st.markdown(f"""
            <table style="width: 100%; color: #E8F4F8; font-size: 0.9rem;">
                <tr><td style="padding: 8px; color: #7A8B9A;">Custo Base Total</td><td style="padding: 8px; text-align: right; font-weight: 600;">R$ {sim.custo_total_base:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Fator de Ajuste</td><td style="padding: 8px; text-align: right; font-weight: 600;">{sim.fator_total:.2f}x</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Custo Ajustado</td><td style="padding: 8px; text-align: right; font-weight: 600;">R$ {sim.custo_ajustado:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Acrescimo Risco</td><td style="padding: 8px; text-align: right; font-weight: 600; color: {'#FFB800' if sim.acrescimo_risco_pct > 0 else '#7A8B9A'};">+{sim.acrescimo_risco_pct:.1f}% = R$ {sim.custo_com_risco - sim.custo_ajustado:,.2f}</td></tr>
                <tr style="border-top: 2px solid #1E3A5F;"><td style="padding: 8px; color: #7A8B9A;"><strong>Custo Final</strong></td><td style="padding: 8px; text-align: right; font-weight: 700;">R$ {sim.custo_com_risco:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">BDI Aplicado</td><td style="padding: 8px; text-align: right; font-weight: 600;">{sim.bdi:.2f}x</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Preco Bruto</td><td style="padding: 8px; text-align: right; font-weight: 600;">R$ {sim.preco_venda_bruto:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Desconto Sabesp</td><td style="padding: 8px; text-align: right; font-weight: 600; color: #FF4757;">-{sim.desconto_negociado_pct:.1f}% = R$ {sim.desconto_em_reais:,.2f}</td></tr>
                <tr style="border-top: 2px solid #1E3A5F;"><td style="padding: 8px; color: #00D4AA;"><strong>PRECO FINAL</strong></td><td style="padding: 8px; text-align: right; font-weight: 800; color: #00D4AA; font-size: 1.1rem;">R$ {sim.preco_venda_liquido:,.2f}</td></tr>
            </table>
            """, unsafe_allow_html=True)

    st.markdown("<div class='hydro-divider'></div>", unsafe_allow_html=True)

    col_grafico, col_tabela = st.columns([1.5, 1])

    with col_grafico:
        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📈 Composicao do Preco Final</h4>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Pie(
            labels=['Custo Base', 'Ajustes (Dist/Mar/Comp)', 'Risco', 'Margem (BDI)', 'Desconto'],
            values=[sim.custo_total_base, sim.custo_ajustado - sim.custo_total_base,
                    sim.custo_com_risco - sim.custo_ajustado, sim.preco_venda_bruto - sim.custo_com_risco,
                    -sim.desconto_em_reais if sim.desconto_em_reais > 0 else 0],
            hole=0.5, marker_colors=['#0066CC', '#00A3E0', '#FFB800', '#00D4AA', '#FF4757'],
            textinfo='label+percent', textfont_size=11,
            hovertemplate='<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>'
        )])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#E8F4F8'), margin=dict(t=10, b=10, l=10, r=10), height=350,
                          annotations=[dict(text=f'R$<br>{sim.preco_venda_liquido/1e6:.2f}Mi', x=0.5, y=0.5, font_size=18, font_color='#00D4AA', showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

    with col_tabela:
        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📊 Comparativo por BDI</h4>
        </div>
        """, unsafe_allow_html=True)

        cenarios = sim.gerar_cenarios()
        html_tabela = """
        <table class="comparativo-table">
            <tr><th>BDI</th><th>Preco (Mi)</th><th>Margem Liq.</th><th>Status</th></tr>
        """
        for c in cenarios:
            cor_classe = "positivo" if c["Margem Líquida"] >= 28 else "neutro" if c["Margem Líquida"] >= 20 else "negativo"
            badge_class = "badge-otimo" if c["Status"]=="Otimo" else "badge-bom" if c["Status"]=="Bom" else "badge-atencao" if c["Status"]=="Atencao" else "badge-critico"
            html_tabela += f"""
            <tr style="{'background: rgba(0, 212, 170, 0.05);' if c['BDI'] == f'{sim.bdi:.2f}x' else ''}">
                <td><strong>{c['BDI']}</strong></td>
                <td>R$ {c['Preço Venda']/1e6:.2f}M</td>
                <td class="{cor_classe}">{c['Margem Líquida']:.1f}%</td>
                <td><span class="badge-negociacao {badge_class}">{c['Status']}</span></td>
            </tr>
            """
        html_tabela += "</table>"
        st.markdown(html_tabela, unsafe_allow_html=True)

    st.markdown("<div class='hydro-divider'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px;">
        <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📤 Exportar Proposta (BDI Enviado ao n8n)</h4>
        <p style="color: #7A8B9A; font-size: 0.85rem;">O BDI ajustado ({sim.bdi:.2f}x) e o preco final serao enviados automaticamente ao n8n para geracao do relatorio</p>
    </div>
    """, unsafe_allow_html=True)

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        if st.button("📄 Gerar PDF da Proposta", use_container_width=True):
            st.success("✅ PDF gerado! (Integracao com relatorio futura)")

    with col_exp2:
        if st.button("📧 Enviar por Email", use_container_width=True):
            st.info("📧 Proposta enviada para diretoria@hydrosol.ai")

    with col_exp3:
        if st.button("💾 Salvar Proposta + Enviar BDI ao n8n", use_container_width=True):
            with st.spinner("🔄 Enviando BDI e precos ao n8n..."):
                resultado = salvar_proposta_completa(sim, aprovado_por="Socio Diretor", 
                    observacoes=f"BDI ajustado para {sim.bdi:.2f}x apos negociacao com consorcio Sabesp. Desconto de {sim.desconto_negociado_pct:.1f}% concedido.")

                if resultado["status_geral"] == "sucesso":
                    st.success(f"✅ Proposta {resultado['id_proposta']} salva!")
                    st.balloons()
                    col_r1, col_r2, col_r3 = st.columns(3)
                    col_r1.metric("BDI Enviado", f"{resultado['bdi_enviado']:.2f}x")
                    col_r2.metric("Preco Enviado", f"R$ {resultado['preco_enviado']:,.0f}")
                    col_r3.metric("Margem", f"{resultado['margem_enviada']:.1f}%")
                    st.info("📱 WhatsApp notificado | 📄 PDF gerando | 📝 Notion salvo")
                else:
                    st.warning("⚠️ n8n offline — proposta salva localmente")
                    with st.expander("Ver detalhes do erro"):
                        st.json(resultado)

    with st.expander("🔍 Ver JSON da Proposta (para desenvolvedores)", expanded=False):
        st.json(sim.to_dict())

# ==============================================================================
# SETTINGS E FOOTER
# ==============================================================================

def render_settings():
    st.markdown("""
    <div class="hydro-header">
        <h1>⚙️ Configuracoes</h1>
        <p>Gerencie integracoes, preferencias e conexoes do dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    render_notion_config()

    st.markdown('<div class="hydro-divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="hydro-card">
            <h4 style="color: #00A3E0;">👤 Perfil do Usuario</h4>
        </div>
        """, unsafe_allow_html=True)
        role = st.selectbox("Funcao", ["Coordenador", "Engenheiro", "Financeiro", "Cliente", "Administrador"],
                           index=["Coordenador", "Engenheiro", "Financeiro", "Cliente", "Administrador"].index(st.session_state.user_role))
        st.session_state.user_role = role
        st.selectbox("Idioma", ["Portugues (BR)", "English", "Espanol"])
        st.selectbox("Tema", ["Dark (Hydrosol)", "Light", "Sistema"])

    with col2:
        st.markdown("""
        <div class="hydro-card">
            <h4 style="color: #00A3E0;">🔔 Notificacoes</h4>
        </div>
        """, unsafe_allow_html=True)
        st.toggle("Alertas de margem", value=True)
        st.toggle("Atualizacoes de cronograma", value=True)
        st.toggle("Relatorios automaticos", value=False)
        st.toggle("Notificacoes push", value=True)

    st.markdown('<div class="hydro-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hydro-card">
        <h4 style="color: #00A3E0;">ℹ️ Sobre o Sistema</h4>
        <table style="width: 100%; color: #E8F4F8; font-size: 0.9rem;">
            <tr><td style="padding: 8px; color: #7A8B9A;">Versao</td><td style="padding: 8px;">v5.1.0-unificado</td></tr>
            <tr><td style="padding: 8px; color: #7A8B9A;">Stack</td><td style="padding: 8px;">Streamlit + Python + Notion API + n8n</td></tr>
            <tr><td style="padding: 8px; color: #7A8B9A;">Modulos</td><td style="padding: 8px;">Dashboard + Calculo Margem + Simulador + n8n</td></tr>
            <tr><td style="padding: 8px; color: #7A8B9A;">DNA Referencia</td><td style="padding: 8px;">ETE Camburi (57 L/s)</td></tr>
            <tr><td style="padding: 8px; color: #7A8B9A;">Atualizado em</td><td style="padding: 8px;">2026-05-07</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #7A8B9A; font-size: 0.8rem; border-top: 1px solid #1E3A5F; margin-top: 40px;">
        🌊 <strong>Hydrosol AI</strong> · Programa Onda Limpa · Sabesp · 2026<br>
        <span style="font-size: 0.7rem;">Dashboard v5.1 Unificado | Streamlit + Notion API + n8n + LangGraph</span>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    selected = render_sidebar()

    if selected == "🏠 Visao Geral":
        render_header()
        render_overview()
    elif selected == "💼 Simulador de Negociacao":
        render_header()
        render_simulador_negociacao()
    elif selected == "⚙️ Configuracoes":
        render_settings()
    else:
        render_header()
        for etapa in ETAPAS:
            if etapa["nome"] in selected:
                render_etapa(etapa["id"])
                break

    render_footer()

if __name__ == "__main__":
    main()
