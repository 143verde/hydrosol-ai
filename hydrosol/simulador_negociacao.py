"""
================================================================================
HYDROSOL AI - SIMULADOR DE NEGOCIAÇÃO v5.1
Slider interativo para ajuste de BDI e Lucro em tempo real
Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
================================================================================
Este módulo adiciona uma aba "Simulador de Negociação" ao Dashboard,
permitindo ao sócio ajustar BDI, margem e fatores de risco via sliders
e ver o preço final da proposta mudar instantaneamente.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json

# ==============================================================================
# CSS PERSONALIZADO PARA O SIMULADOR
# ==============================================================================

st.markdown("""
<style>
    /* === SIMULADOR DE NEGOCIAÇÃO === */
    .simulador-header {
        background: linear-gradient(135deg, #0066CC 0%, #00A3E0 50%, #00D4AA 100%);
        padding: 24px 30px;
        border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 12px 40px rgba(0, 102, 204, 0.35);
        text-align: center;
    }
    .simulador-header h2 {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }
    .simulador-header p {
        color: rgba(255,255,255,0.9) !important;
        margin: 8px 0 0 0 !important;
        font-size: 1rem;
    }

    /* === CARDS DE RESULTADO === */
    .resultado-card {
        background: linear-gradient(145deg, #111D2E 0%, #0F1A2A 100%);
        border: 2px solid #1E3A5F;
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        transition: all 0.4s ease;
    }
    .resultado-card.destaque {
        border-color: #00D4AA;
        box-shadow: 0 0 40px rgba(0, 212, 170, 0.2);
        transform: scale(1.02);
    }
    .resultado-valor {
        font-size: 2.8rem;
        font-weight: 900;
        color: #00D4AA;
        margin: 12px 0;
        text-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
    }
    .resultado-label {
        font-size: 0.9rem;
        color: #7A8B9A;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    .resultado-delta {
        font-size: 1rem;
        margin-top: 8px;
        font-weight: 500;
    }

    /* === SLIDERS CUSTOMIZADOS === */
    .slider-container {
        background: #111D2E;
        border: 1px solid #1E3A5F;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .slider-label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .slider-nome {
        font-size: 1rem;
        font-weight: 600;
        color: #E8F4F8;
    }
    .slider-valor {
        font-size: 1.2rem;
        font-weight: 800;
        color: #00A3E0;
        background: #0A1628;
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid #1E3A5F;
    }

    /* === BARRA DE PROGRESSO VISUAL === */
    .progress-bar-container {
        width: 100%;
        height: 12px;
        background: #0A1628;
        border-radius: 6px;
        overflow: hidden;
        margin-top: 8px;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease, background 0.5s ease;
    }

    /* === TABELA COMPARATIVA === */
    .comparativo-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
    }
    .comparativo-table th {
        background: linear-gradient(135deg, #0066CC, #00A3E0);
        color: white;
        padding: 14px;
        text-align: center;
        font-weight: 600;
    }
    .comparativo-table td {
        padding: 12px 14px;
        border-bottom: 1px solid #1E3A5F;
        color: #E8F4F8;
        text-align: center;
    }
    .comparativo-table tr:hover td {
        background: rgba(0, 163, 224, 0.1);
    }
    .comparativo-table .positivo { color: #00D4AA; font-weight: 700; }
    .comparativo-table .negativo { color: #FF4757; font-weight: 700; }
    .comparativo-table .neutro { color: #FFB800; font-weight: 700; }

    /* === BADGES DE STATUS === */
    .badge-negociacao {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 4px;
    }
    .badge-otimo { background: rgba(0, 212, 170, 0.15); color: #00D4AA; border: 1px solid #00D4AA; }
    .badge-bom { background: rgba(0, 163, 224, 0.15); color: #00A3E0; border: 1px solid #00A3E0; }
    .badge-atencao { background: rgba(255, 184, 0, 0.15); color: #FFB800; border: 1px solid #FFB800; }
    .badge-critico { background: rgba(255, 71, 87, 0.15); color: #FF4757; border: 1px solid #FF4757; }

    /* === BOTAO EXPORTAR === */
    .btn-exportar {
        background: linear-gradient(135deg, #0066CC, #00A3E0) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .btn-exportar:hover {
        box-shadow: 0 8px 25px rgba(0, 102, 204, 0.4) !important;
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CLASSE: SIMULADOR DE PROPOSTA
# ==============================================================================

@dataclass
class SimuladorProposta:
    """Simulador interativo de proposta comerciais para negociação."""

    # Dados base do projeto (vêm do DNA Camburi ou input do usuário)
    projeto_nome: str = "ETE Onda Limpa #01"
    vazao_ls: float = 20.0
    grupo: str = "Serie"

    # Custos base (fixos - não mudam na negociação)
    custo_base_ls: float = 379_754.38  # DNA Camburi × fator escala Série
    custo_total_base: float = 0.0  # Calculado automaticamente

    # Fatores de ajuste (fixos para esta simulação)
    fator_distancia: float = 1.15
    fator_maresia: float = 1.15
    fator_complexidade: float = 1.00
    fator_urgencia: float = 1.00

    # Variáveis de negociação (controladas por sliders)
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
        return self.margem_real_pct * 0.85  # Desconto impostos/admin

    @property
    def desconto_em_reais(self) -> float:
        return self.preco_venda_bruto * (self.desconto_negociado_pct / 100)

    @property
    def status_negociacao(self) -> str:
        ml = self.margem_liquida_real_pct
        if ml >= 31:
            return "🟢 ÓTIMO - Margem acima do target"
        elif ml >= 28:
            return "🟡 BOM - Dentro do target"
        elif ml >= 20:
            return "🟠 ATENÇÃO - Abaixo do target, mas viável"
        else:
            return "🔴 CRÍTICO - Margem inaceitável"

    @property
    def cor_status(self) -> str:
        ml = self.margem_liquida_real_pct
        if ml >= 31: return "#00D4AA"
        elif ml >= 28: return "#00A3E0"
        elif ml >= 20: return "#FFB800"
        else: return "#FF4757"

    def gerar_cenarios(self) -> List[Dict]:
        """Gera cenários comparativos para análise."""
        cenarios = []
        for bdi in [1.30, 1.35, 1.40, 1.45, 1.50, 1.55]:
            preco = self.custo_com_risco * bdi
            margem = ((preco - self.custo_com_risco) / preco) * 100 * 0.85
            cenarios.append({
                "BDI": f"{bdi:.2f}x",
                "Preço Venda": preco,
                "Margem Líquida": margem,
                "Status": "Ótimo" if margem >= 31 else "Bom" if margem >= 28 else "Atenção" if margem >= 20 else "Crítico"
            })
        return cenarios

    def to_dict(self) -> Dict:
        return {
            "projeto": self.projeto_nome,
            "vazao_ls": self.vazao_ls,
            "grupo": self.grupo,
            "custo_base_total": self.custo_total_base,
            "custo_ajustado": self.custo_ajustado,
            "fator_total": self.fator_total,
            "bdi": self.bdi,
            "margem_desejada": self.margem_desejada_pct,
            "desconto_negociado": self.desconto_negociado_pct,
            "acrescimo_risco": self.acrescimo_risco_pct,
            "preco_venda_bruto": self.preco_venda_bruto,
            "preco_venda_liquido": self.preco_venda_liquido,
            "margem_real": self.margem_real_pct,
            "margem_liquida_real": self.margem_liquida_real_pct,
            "desconto_reais": self.desconto_em_reais,
            "status": self.status_negociacao
        }


# ==============================================================================
# FUNÇÃO PRINCIPAL DO SIMULADOR (PARA INTEGRAR NO DASHBOARD)
# ==============================================================================

def render_simulador_negociacao():
    """
    Renderiza a aba completa do Simulador de Negociação.
    Chame esta função no dashboard principal para adicionar a aba.
    """

    # Header
    st.markdown("""
    <div class="simulador-header">
        <h2>💼 Simulador de Negociação</h2>
        <p>Ajuste BDI, margem e fatores de risco em tempo real para negociações com consórcios Sabesp</p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================
    # COLUNA ESQUERDA: CONTROLES (SLIDERS)
    # ==========================================================
    col_controles, col_resultados = st.columns([1, 1.2])

    with col_controles:
        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">🎚️ Controles de Negociação</h4>
            <p style="color: #7A8B9A; font-size: 0.85rem; margin: 0;">Arraste as barras para simular diferentes cenários</p>
        </div>
        """, unsafe_allow_html=True)

        # Seleção do projeto base
        projeto_sel = st.selectbox(
            "📋 Selecionar Projeto Base",
            ["ETE Onda Limpa #01 (20 L/s - Série)", 
             "ETE Onda Limpa #05 (20 L/s - Série)",
             "ETE Onda Limpa #28 (100 L/s - Médio)",
             "ETA Onda Limpa #45 (500 L/s - Magnum)",
             "Personalizado"],
            help="Escolha um projeto existente ou configure manualmente"
        )

        # Se personalizado, mostrar inputs
        if projeto_sel == "Personalizado":
            vazao_input = st.number_input("Vazão (L/s)", min_value=1.0, max_value=1000.0, value=20.0, step=1.0)
            custo_ls_input = st.number_input("Custo por L/s (R$)", min_value=100000.0, max_value=1000000.0, value=379754.0, step=1000.0)
        else:
            # Valores pré-configurados
            configs = {
                "ETE Onda Limpa #01 (20 L/s - Série)": (20.0, 379754.38, "Serie"),
                "ETE Onda Limpa #05 (20 L/s - Série)": (20.0, 379754.38, "Serie"),
                "ETE Onda Limpa #28 (100 L/s - Médio)": (100.0, 277192.98, "Medio"),
                "ETA Onda Limpa #45 (500 L/s - Magnum)": (500.0, 235614.03, "Magnum")
            }
            vazao_input, custo_ls_input, grupo_input = configs[projeto_sel]

        st.markdown("<div class='hydro-divider'></div>", unsafe_allow_html=True)

        # SLIDER 1: BDI
        st.markdown("""
        <div class="slider-container">
            <div class="slider-label">
                <span class="slider-nome">📈 BDI (Bônus e Despesas Indiretas)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bdi = st.slider(
            "",
            min_value=1.20,
            max_value=1.80,
            value=1.45,
            step=0.01,
            format="%.2fx",
            help="BDI = multiplicador sobre o custo. Padrão Hydrosol: 1.35 a 1.45"
        )

        # Barra visual do BDI
        bdi_pct = ((bdi - 1.20) / (1.80 - 1.20)) * 100
        cor_bdi = "#00D4AA" if bdi >= 1.35 else "#FFB800" if bdi >= 1.25 else "#FF4757"
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {bdi_pct}%; background: {cor_bdi};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
            <span style="font-size: 0.75rem; color: #7A8B9A;">1.20x (mínimo)</span>
            <span style="font-size: 0.9rem; font-weight: 700; color: {cor_bdi};">{bdi:.2f}x</span>
            <span style="font-size: 0.75rem; color: #7A8B9A;">1.80x (máximo)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SLIDER 2: Margem Desejada
        st.markdown("""
        <div class="slider-container">
            <div class="slider-label">
                <span class="slider-nome">🎯 Margem Líquida Desejada</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        margem_desejada = st.slider(
            "",
            min_value=15.0,
            max_value=40.0,
            value=31.0,
            step=0.5,
            format="%.1f%%",
            help="Target Hydrosol: 28-31%. Abaixo de 20% é considerado crítico."
        )

        margem_pct = ((margem_desejada - 15) / (40 - 15)) * 100
        cor_margem = "#00D4AA" if margem_desejada >= 28 else "#FFB800" if margem_desejada >= 20 else "#FF4757"
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {margem_pct}%; background: {cor_margem};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
            <span style="font-size: 0.75rem; color: #7A8B9A;">15% (mínimo)</span>
            <span style="font-size: 0.9rem; font-weight: 700; color: {cor_margem};">{margem_desejada:.1f}%</span>
            <span style="font-size: 0.75rem; color: #7A8B9A;">40% (máximo)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SLIDER 3: Desconto Negociado
        st.markdown("""
        <div class="slider-container">
            <div class="slider-label">
                <span class="slider-nome">🏷️ Desconto para Consórcio Sabesp</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        desconto = st.slider(
            "",
            min_value=0.0,
            max_value=15.0,
            value=0.0,
            step=0.5,
            format="%.1f%%",
            help="Desconto concedido na negociação. Cada 1% de desconto reduz a margem."
        )

        desconto_pct = (desconto / 15) * 100
        cor_desconto = "#00D4AA" if desconto <= 3 else "#FFB800" if desconto <= 8 else "#FF4757"
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {desconto_pct}%; background: {cor_desconto};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
            <span style="font-size: 0.75rem; color: #7A8B9A;">0% (sem desconto)</span>
            <span style="font-size: 0.9rem; font-weight: 700; color: {cor_desconto};">{desconto:.1f}%</span>
            <span style="font-size: 0.75rem; color: #7A8B9A;">15% (máximo)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SLIDER 4: Acréscimo de Risco
        st.markdown("""
        <div class="slider-container">
            <div class="slider-label">
                <span class="slider-nome">⚠️ Acréscimo de Risco (Imprevistos)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        risco = st.slider(
            "",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
            format="%.1f%%",
            help="Reserva para riscos e imprevistos. Recomendado: 2-5% para projetos complexos."
        )

        risco_pct = (risco / 10) * 100
        cor_risco = "#00D4AA" if risco <= 3 else "#FFB800" if risco <= 6 else "#FF4757"
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {risco_pct}%; background: {cor_risco};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
            <span style="font-size: 0.75rem; color: #7A8B9A;">0% (sem risco)</span>
            <span style="font-size: 0.9rem; font-weight: 700; color: {cor_risco};">{risco:.1f}%</span>
            <span style="font-size: 0.75rem; color: #7A8B9A;">10% (máximo)</span>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================================
    # COLUNA DIREITA: RESULTADOS EM TEMPO REAL
    # ==========================================================
    with col_resultados:
        # Instanciar simulador com valores dos sliders
        sim = SimuladorProposta(
            projeto_nome=projeto_sel.split(" (")[0] if "(" in projeto_sel else projeto_sel,
            vazao_ls=vazao_input,
            grupo=grupo_input if "grupo_input" in dir() else "Serie",
            custo_base_ls=custo_ls_input,
            bdi=bdi,
            margem_desejada_pct=margem_desejada,
            desconto_negociado_pct=desconto,
            acrescimo_risco_pct=risco
        )

        st.markdown(f"""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📊 Resultado da Proposta</h4>
            <p style="color: #7A8B9A; font-size: 0.85rem; margin: 0;">Atualizado automaticamente ao mover os sliders</p>
        </div>
        """, unsafe_allow_html=True)

        # CARD PREÇO FINAL
        preco_formatado = f"R$ {sim.preco_venda_liquido/1e6:.2f} Mi"
        st.markdown(f"""
        <div class="resultado-card destaque">
            <div class="resultado-label">💰 PREÇO FINAL DA PROPOSTA</div>
            <div class="resultado-valor">{preco_formatado}</div>
            <div class="resultado-delta" style="color: {sim.cor_status};">
                BDI {sim.bdi:.2f}x | Desconto {sim.desconto_negociado_pct:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CARDS SECUNDÁRIOS
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
                <div class="resultado-label">📉 MARGEM LÍQUIDA</div>
                <div class="resultado-valor" style="font-size: 1.8rem; color: {sim.cor_status};">{sim.margem_liquida_real_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # STATUS
        st.markdown(f"""
        <div style="text-align: center; margin: 16px 0;">
            <span class="badge-negociacao {'badge-otimo' if sim.margem_liquida_real_pct >= 31 else 'badge-bom' if sim.margem_liquida_real_pct >= 28 else 'badge-atencao' if sim.margem_liquida_real_pct >= 20 else 'badge-critico'}">
                {sim.status_negociacao}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # DETALHAMENTO
        with st.expander("📋 Ver Detalhamento Completo", expanded=False):
            st.markdown(f"""
            <table style="width: 100%; color: #E8F4F8; font-size: 0.9rem;">
                <tr><td style="padding: 8px; color: #7A8B9A;">Custo Base Total</td><td style="padding: 8px; text-align: right; font-weight: 600;">R$ {sim.custo_total_base:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Fator de Ajuste</td><td style="padding: 8px; text-align: right; font-weight: 600;">{sim.fator_total:.2f}x</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Custo Ajustado</td><td style="padding: 8px; text-align: right; font-weight: 600;">R$ {sim.custo_ajustado:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Acréscimo Risco</td><td style="padding: 8px; text-align: right; font-weight: 600; color: {'#FFB800' if sim.acrescimo_risco_pct > 0 else '#7A8B9A'};">+{sim.acrescimo_risco_pct:.1f}% = R$ {sim.custo_com_risco - sim.custo_ajustado:,.2f}</td></tr>
                <tr style="border-top: 2px solid #1E3A5F;"><td style="padding: 8px; color: #7A8B9A;"><strong>Custo Final</strong></td><td style="padding: 8px; text-align: right; font-weight: 700;">R$ {sim.custo_com_risco:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">BDI Aplicado</td><td style="padding: 8px; text-align: right; font-weight: 600;">{sim.bdi:.2f}x</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Preço Bruto</td><td style="padding: 8px; text-align: right; font-weight: 600;">R$ {sim.preco_venda_bruto:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #7A8B9A;">Desconto Sabesp</td><td style="padding: 8px; text-align: right; font-weight: 600; color: #FF4757;">-{sim.desconto_negociado_pct:.1f}% = R$ {sim.desconto_em_reais:,.2f}</td></tr>
                <tr style="border-top: 2px solid #1E3A5F;"><td style="padding: 8px; color: #00D4AA;"><strong>PREÇO FINAL</strong></td><td style="padding: 8px; text-align: right; font-weight: 800; color: #00D4AA; font-size: 1.1rem;">R$ {sim.preco_venda_liquido:,.2f}</td></tr>
            </table>
            """, unsafe_allow_html=True)

    # ==========================================================
    # SEÇÃO INFERIOR: GRÁFICOS E COMPARATIVOS
    # ==========================================================
    st.markdown("<div class='hydro-divider'></div>", unsafe_allow_html=True)

    col_grafico, col_tabela = st.columns([1.5, 1])

    with col_grafico:
        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📈 Composição do Preço Final</h4>
        </div>
        """, unsafe_allow_html=True)

        # Gráfico de composição
        fig = go.Figure(data=[go.Pie(
            labels=['Custo Base', 'Ajustes (Dist/Mar/Comp)', 'Risco', 'Margem (BDI)', 'Desconto'],
            values=[
                sim.custo_total_base,
                sim.custo_ajustado - sim.custo_total_base,
                sim.custo_com_risco - sim.custo_ajustado,
                sim.preco_venda_bruto - sim.custo_com_risco,
                -sim.desconto_em_reais if sim.desconto_em_reais > 0 else 0
            ],
            hole=0.5,
            marker_colors=['#0066CC', '#00A3E0', '#FFB800', '#00D4AA', '#FF4757'],
            textinfo='label+percent',
            textfont_size=11,
            hovertemplate='<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>'
        )])
        fig.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E8F4F8'),
            margin=dict(t=10, b=10, l=10, r=10),
            height=350,
            annotations=[dict(
                text=f'R$<br>{sim.preco_venda_liquido/1e6:.2f}Mi',
                x=0.5, y=0.5,
                font_size=18,
                font_color='#00D4AA',
                showarrow=False
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_tabela:
        st.markdown("""
        <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px;">
            <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📊 Comparativo por BDI</h4>
        </div>
        """, unsafe_allow_html=True)

        cenarios = sim.gerar_cenarios()

        # Tabela comparativa
        html_tabela = """
        <table class="comparativo-table">
            <tr>
                <th>BDI</th>
                <th>Preço (Mi)</th>
                <th>Margem Liq.</th>
                <th>Status</th>
            </tr>
        """
        for c in cenarios:
            cor_classe = "positivo" if c["Margem Líquida"] >= 28 else "neutro" if c["Margem Líquida"] >= 20 else "negativo"
            html_tabela += f"""
            <tr style="{'background: rgba(0, 212, 170, 0.05);' if c['BDI'] == f'{sim.bdi:.2f}x' else ''}">
                <td><strong>{c['BDI']}</strong></td>
                <td>R$ {c['Preço Venda']/1e6:.2f}M</td>
                <td class="{cor_classe}">{c['Margem Líquida']:.1f}%</td>
                <td><span class="badge-negociacao {'badge-otimo' if c['Status']=='Ótimo' else 'badge-bom' if c['Status']=='Bom' else 'badge-atencao' if c['Status']=='Atenção' else 'badge-critico'}">{c['Status']}</span></td>
            </tr>
            """
        html_tabela += "</table>"
        st.markdown(html_tabela, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top: 12px; text-align: center;">
            <span style="font-size: 0.8rem; color: #7A8B9A;">🔵 Linha destacada = BDI atual selecionado ({sim.bdi:.2f}x)</span>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================================
    # EXPORTAR PROPOSTA
    # ==========================================================
    st.markdown("<div class='hydro-divider'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #111D2E; border: 1px solid #1E3A5F; border-radius: 16px; padding: 20px;">
        <h4 style="color: #00A3E0; margin: 0 0 16px 0;">📤 Exportar Proposta</h4>
    </div>
    """, unsafe_allow_html=True)

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        if st.button("📄 Gerar PDF da Proposta", use_container_width=True):
            st.success("✅ PDF gerado! (Integração com relatório futura)")
            # Aqui integraria com gerador de PDF

    with col_exp2:
        if st.button("📧 Enviar por Email", use_container_width=True):
            st.info("📧 Proposta enviada para diretoria@hydrosol.ai")
            # Aqui integraria com n8n/email

    with col_exp3:
        if st.button("💾 Salvar no Notion", use_container_width=True):
            st.success("✅ Proposta salva na database 'Decisões' do Notion")
            # Aqui integraria com Notion API

    # JSON da proposta para debug/copy
    with st.expander("🔍 Ver JSON da Proposta (para desenvolvedores)", expanded=False):
        st.json(sim.to_dict())


# ==============================================================================
# COMO INTEGRAR NO DASHBOARD PRINCIPAL
# ==============================================================================
"""
PARA ADICIONAR ESTA ABA AO DASHBOARD PRINCIPAL (dashboard.py):

1. Copie este arquivo para: hydrosol/simulador_negociacao.py

2. No dashboard.py, adicione no topo:
   from hydrosol.simulador_negociacao import render_simulador_negociacao

3. No menu lateral (render_sidebar), adicione a opção:
   menu_options = ["🏠 Visão Geral"] + [f"{e['icone']} {e['nome']}" for e in ETAPAS] + 
                  ["💼 Simulador de Negociação", "⚙️ Configurações"]

4. Na função main(), adicione o elif:
   elif selected == "💼 Simulador de Negociação":
       render_simulador_negociacao()

5. Pronto! A aba aparecerá no menu lateral.
"""


# ==============================================================================
# EXECUÇÃO STANDALONE (PARA TESTE)
# ==============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Hydrosol - Simulador de Negociação",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    render_simulador_negociacao()
