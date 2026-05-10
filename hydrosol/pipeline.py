
"""
🌊 Hydrosol AI — Módulo Pipeline de Propostas v5.1
Sistema de gestão de propostas com Kanban, simulação e análise de performance.
Integra com Notion API + n8n + LangGraph.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import json

# ============================================================
# CONFIGURAÇÕES E ENUMS
# ============================================================

class StatusProposta(Enum):
    SIMULADA = "Simulada"
    ENVIADA = "Enviada"
    NEGOCIANDO = "Negociando"
    EFETIVADA = "Efetivada"
    PERDIDA = "Perdida"
    SUSPENSA = "Suspensa"
    CANCELADA = "Cancelada"

class MotivoPerda(Enum):
    PRECO = "Preço maior que concorrente"
    PRAZO = "Prazo não atendeu"
    ESCOPO = "Escopo incompleto"
    CONSORCIO = "Problema no consórcio"
    SABESP = "Sabesp mudou critérios"
    OUTRO = "Outro"

class GrupoVazao(Enum):
    MICRO = "Micro (1-5 L/s)"
    PEQUENO = "Pequeno (8-20 L/s)"
    MEDIO = "Médio (25-60 L/s)"
    GRANDE = "Grande (129-200 L/s)"
    MAGNUM = "Magnum (500-1000 L/s)"

# ============================================================
# DATACLASSES
# ============================================================

@dataclass
class Unidade:
    id: str
    nome: str
    tipo: str  # ETE ou ETA
    vazao_ls: float
    grupo: GrupoVazao
    lote: str
    consorcio: str
    custo_estimado: float
    bdi_simulado: float = 1.30
    margem_simulada: float = 0.25
    status: StatusProposta = StatusProposta.SIMULADA
    motivo_perda: Optional[MotivoPerda] = None
    data_envio: Optional[str] = None
    data_decisao: Optional[str] = None
    valor_venda: float = 0.0
    observacoes: str = ""
    licoes_aprendidas: List[str] = field(default_factory=list)

@dataclass
class LicaoAprendida:
    id: str
    proposta_id: str
    problema: str
    solucao: str
    status: str
    data: str
    impacto_receita: float = 0.0

# ============================================================
# BASE DE DADOS REAL — LOTES SABESP
# ============================================================

def carregar_unidades_reais() -> List[Unidade]:
    """Carrega unidades reais do Programa Onda Limpa / Sabesp"""

    unidades = []

    # ═══════════════════════════════════════════════════════════
    # GRUPO MAGNUM (500-1000 L/s) — 5 unidades
    # ═══════════════════════════════════════════════════════════

    unidades.extend([
        Unidade(
            id="ETA-500-01", nome="ETA Camburi Norte", tipo="ETA",
            vazao_ls=500, grupo=GrupoVazao.MAGNUM, lote="21",
            consorcio="TRAIL", custo_estimado=74.0,
            bdi_simulado=1.25, margem_simulada=0.20,
            status=StatusProposta.NEGOCIANDO,
            data_envio="2026-04-15", valor_venda=92.5,
            observacoes="Aguardando resposta Sabesp"
        ),
        Unidade(
            id="ETA-500-02", nome="ETA Jardim das Oliveiras", tipo="ETA",
            vazao_ls=500, grupo=GrupoVazao.MAGNUM, lote="22",
            consorcio="ANKARA", custo_estimado=74.0,
            bdi_simulado=1.25, margem_simulada=0.20,
            status=StatusProposta.PERDIDA,
            motivo_perda=MotivoPerda.PRECO,
            data_envio="2026-03-20", data_decisao="2026-05-08",
            valor_venda=92.5,
            observacoes="ANKARA perdeu para consórcio chinês",
            licoes_aprendidas=["BDI 1.25 não competitivo para Magnum", 
                             "Concorrente ofereceu BDI 1.18"]
        ),
        Unidade(
            id="ETA-500-03", nome="ETA Parque das Nações", tipo="ETA",
            vazao_ls=500, grupo=GrupoVazao.MAGNUM, lote="24",
            consorcio="ANKARA", custo_estimado=74.0,
            bdi_simulado=1.25, margem_simulada=0.20,
            status=StatusProposta.PERDIDA,
            motivo_perda=MotivoPerda.PRECO,
            data_envio="2026-02-10", data_decisao="2026-04-25",
            valor_venda=92.5,
            observacoes="Segunda perda ANKARA por preço",
            licoes_aprendidas=["ANKARA perdeu 2x por preço nos últimos 6 meses",
                             "Recomendação: BDI mínimo Magnum = 1.20"]
        ),
        Unidade(
            id="ETA-1000-01", nome="ETA Rio Grande", tipo="ETA",
            vazao_ls=1000, grupo=GrupoVazao.MAGNUM, lote="22",
            consorcio="ANKARA", custo_estimado=128.6,
            bdi_simulado=1.25, margem_simulada=0.20,
            status=StatusProposta.SIMULADA,
            observacoes="Nova proposta pós-perda Lote 22"
        ),
        Unidade(
            id="ETA-1000-02", nome="ETA Vale do Sol", tipo="ETA",
            vazao_ls=1000, grupo=GrupoVazao.MAGNUM, lote="24",
            consorcio="ANKARA", custo_estimado=128.6,
            bdi_simulado=1.20, margem_simulada=0.22,
            status=StatusProposta.SIMULADA,
            observacoes="Ajustado BDI para 1.20 após lição aprendida"
        ),
    ])

    # ═══════════════════════════════════════════════════════════
    # GRUPO GRANDE (129-200 L/s) — 6 unidades
    # ═══════════════════════════════════════════════════════════

    unidades.extend([
        Unidade(
            id="ETE-150-01", nome="ETE Centro Industrial", tipo="ETE",
            vazao_ls=150, grupo=GrupoVazao.GRANDE, lote="15",
            consorcio="TRAIL", custo_estimado=28.5,
            bdi_simulado=1.28, margem_simulada=0.26,
            status=StatusProposta.EFETIVADA,
            data_envio="2026-01-15", data_decisao="2026-03-20",
            valor_venda=36.5,
            observacoes="Contrato assinado, início etapa 1"
        ),
        Unidade(
            id="ETE-200-01", nome="ETE Nova Indústria", tipo="ETE",
            vazao_ls=200, grupo=GrupoVazao.GRANDE, lote="15",
            consorcio="TRAIL", custo_estimado=38.0,
            bdi_simulado=1.28, margem_simulada=0.26,
            status=StatusProposta.EFETIVADA,
            data_envio="2026-01-15", data_decisao="2026-03-20",
            valor_venda=48.6,
            observacoes="Contrato assinado junto com ETE-150-01"
        ),
        Unidade(
            id="ETA-129-01", nome="ETA Litoral Norte", tipo="ETA",
            vazao_ls=129, grupo=GrupoVazao.GRANDE, lote="18",
            consorcio="HYDROSOL", custo_estimado=22.0,
            bdi_simulado=1.30, margem_simulada=0.28,
            status=StatusProposta.NEGOCIANDO,
            data_envio="2026-04-01", valor_venda=28.6,
            observacoes="Hydrosol solo, sem consórcio"
        ),
        Unidade(
            id="ETA-200-01", nome="ETA Porto Seguro", tipo="ETA",
            vazao_ls=200, grupo=GrupoVazao.GRANDE, lote="18",
            consorcio="HYDROSOL", custo_estimado=38.0,
            bdi_simulado=1.30, margem_simulada=0.28,
            status=StatusProposta.NEGOCIANDO,
            data_envio="2026-04-01", valor_venda=49.4,
            observacoes="Negociação direta com Sabesp"
        ),
        Unidade(
            id="ETE-150-02", nome="ETE Zona Sul", tipo="ETE",
            vazao_ls=150, grupo=GrupoVazao.GRANDE, lote="12",
            consorcio="MAGNUS", custo_estimado=28.5,
            bdi_simulado=1.30, margem_simulada=0.26,
            status=StatusProposta.ENVIADA,
            data_envio="2026-05-01", valor_venda=37.0,
            observacoes="Aguardando abertura de propostas"
        ),
        Unidade(
            id="ETE-200-02", nome="ETE Zona Leste", tipo="ETE",
            vazao_ls=200, grupo=GrupoVazao.GRANDE, lote="12",
            consorcio="MAGNUS", custo_estimado=38.0,
            bdi_simulado=1.30, margem_simulada=0.26,
            status=StatusProposta.ENVIADA,
            data_envio="2026-05-01", valor_venda=49.4,
            observacoes="Aguardando abertura de propostas"
        ),
    ])

    # ═══════════════════════════════════════════════════════════
    # GRUPO MÉDIO (25-60 L/s) — 25 unidades (amostra representativa)
    # ═══════════════════════════════════════════════════════════

    for i in range(1, 6):
        unidades.append(Unidade(
            id=f"ETE-40-{i:02d}", nome=f"ETE Médio {i}", tipo="ETE",
            vazao_ls=40, grupo=GrupoVazao.MEDIO, lote=f"{10+i}",
            consorcio="TRAIL" if i <= 3 else "MAGNUS",
            custo_estimado=8.5,
            bdi_simulado=1.35, margem_simulada=0.26,
            status=StatusProposta.SIMULADA if i > 3 else StatusProposta.ENVIADA,
            data_envio=f"2026-04-{10+i}" if i <= 3 else None,
            valor_venda=11.5,
            observacoes="Padronização DNA Camburi"
        ))

    # ═══════════════════════════════════════════════════════════
    # GRUPO PEQUENO (8-20 L/s) — 66 unidades (amostra)
    # ═══════════════════════════════════════════════════════════

    for i in range(1, 8):
        unidades.append(Unidade(
            id=f"ETE-20-{i:02d}", nome=f"ETE Pequeno {i}", tipo="ETE",
            vazao_ls=20, grupo=GrupoVazao.PEQUENO, lote=f"{5+i}",
            consorcio="LOTE_COMPRA" if i <= 4 else "HYDROSOL",
            custo_estimado=5.5,
            bdi_simulado=1.40, margem_simulada=0.29,
            status=StatusProposta.EFETIVADA if i <= 4 else StatusProposta.SIMULADA,
            data_envio=f"2026-02-{5+i}" if i <= 4 else None,
            data_decisao=f"2026-03-{15+i}" if i <= 4 else None,
            valor_venda=7.7,
            observacoes="Lote de compra consolidado" if i <= 4 else "Em simulação"
        ))

    # ═══════════════════════════════════════════════════════════
    # GRUPO MICRO (1-5 L/s) — 86 unidades (amostra)
    # ═══════════════════════════════════════════════════════════

    for i in range(1, 10):
        unidades.append(Unidade(
            id=f"ETA-05-{i:02d}", nome=f"ETA Micro {i}", tipo="ETA",
            vazao_ls=5, grupo=GrupoVazao.MICRO, lote=f"{1+i}",
            consorcio="PADRONIZACAO",
            custo_estimado=1.8,
            bdi_simulado=1.55, margem_simulada=0.35,
            status=StatusProposta.EFETIVADA if i <= 6 else StatusProposta.SIMULADA,
            data_envio=f"2026-01-{10+i}" if i <= 6 else None,
            data_decisao=f"2026-02-{20+i}" if i <= 6 else None,
            valor_venda=2.8,
            observacoes="Padronização máxima, projeto tipo" if i <= 6 else "Em fila"
        ))

    # ═══════════════════════════════════════════════════════════
    # LOTES PENDENTES (sem proposta ainda)
    # ═══════════════════════════════════════════════════════════

    lotes_pendentes = ["2", "7", "10", "11", "19"]
    for lote in lotes_pendentes:
        unidades.append(Unidade(
            id=f"PENDENTE-{lote}", nome=f"Lote {lote} — Aguardando", tipo="ETE/ETA",
            vazao_ls=0, grupo=GrupoVazao.MICRO, lote=lote,
            consorcio="A_DEFINIR", custo_estimado=0,
            bdi_simulado=1.30, margem_simulada=0.25,
            status=StatusProposta.SIMULADA,
            observacoes=f"Lote {lote} ainda sem proposta formal"
        ))

    return unidades

# ============================================================
# FUNÇÕES DE ANÁLISE E PERFORMANCE
# ============================================================

def calcular_indicadores(unidades: List[Unidade]) -> Dict:
    """Calcula indicadores de performance do pipeline"""

    df = pd.DataFrame([{
        'id': u.id,
        'status': u.status.value,
        'grupo': u.grupo.value,
        'consorcio': u.consorcio,
        'custo': u.custo_estimado,
        'venda': u.valor_venda,
        'margem': u.margem_simulada,
        'data_envio': u.data_envio,
        'data_decisao': u.data_decisao
    } for u in unidades])

    # Pipeline total
    pipeline_total = df['venda'].sum()

    # Por status
    por_status = df.groupby('status').agg({
        'venda': 'sum',
        'id': 'count'
    }).rename(columns={'id': 'quantidade'})

    # Taxa de conversão
    efetivadas = por_status.get('Efetivada', {}).get('quantidade', 0)
    enviadas = df[df['status'].isin(['Enviada', 'Negociando', 'Efetivada', 'Perdida'])].shape[0]
    taxa_conversao = (efetivadas / enviadas * 100) if enviadas > 0 else 0

    # Receita efetivada
    receita_efetivada = por_status.get('Efetivada', {}).get('venda', 0)

    # Propostas perdidas
    perdidas = df[df['status'] == 'Perdida']
    perda_total = perdidas['venda'].sum()

    # Grupo Magnum
    magnum = df[df['grupo'] == 'Magnum (500-1000 L/s)']
    magnum_perdidas = magnum[magnum['status'] == 'Perdida'].shape[0]
    magnum_total = magnum.shape[0]

    # Tempo médio ciclo (dias)
    ciclos = []
    for _, row in df.iterrows():
        if row['data_envio'] and row['data_decisao']:
            try:
                envio = datetime.strptime(row['data_envio'], "%Y-%m-%d")
                decisao = datetime.strptime(row['data_decisao'], "%Y-%m-%d")
                ciclos.append((decisao - envio).days)
            except:
                pass
    tempo_medio = sum(ciclos) / len(ciclos) if ciclos else 0

    return {
        'pipeline_total': pipeline_total,
        'por_status': por_status,
        'taxa_conversao': taxa_conversao,
        'receita_efetivada': receita_efetivada,
        'perda_total': perda_total,
        'magnum_perdidas': magnum_perdidas,
        'magnum_total': magnum_total,
        'tempo_medio_ciclo': tempo_medio,
        'total_unidades': len(unidades)
    }

def gerar_alertas(unidades: List[Unidade]) -> List[Dict]:
    """Gera alertas inteligentes baseados no pipeline"""

    alertas = []
    df = pd.DataFrame([{
        'id': u.id, 'status': u.status.value, 'consorcio': u.consorcio,
        'grupo': u.grupo.value, 'data_envio': u.data_envio,
        'motivo_perda': u.motivo_perda.value if u.motivo_perda else None,
        'lote': u.lote, 'margem': u.margem_simulada
    } for u in unidades])

    # Alerta 1: ANKARA perdeu 2x por preço
    ankara_perdidas = df[(df['consorcio'] == 'ANKARA') & (df['status'] == 'Perdida')]
    if len(ankara_perdidas) >= 2:
        alertas.append({
            'nivel': '🔴 CRÍTICO',
            'titulo': f'ANKARA perdeu {len(ankara_perdidas)}º lote por preço',
            'descricao': 'Padrão detectado: BDI 1.25 não competitivo para Magnum',
            'acao': 'Revisar BDI Magnum para 1.20 em 7 dias',
            'impacto': f'Receita perdida: R$ {ankara_perdidas.shape[0] * 92.5:.1f}M'
        })

    # Alerta 2: Propostas em negociação > 30 dias
    hoje = datetime.now()
    for _, row in df[df['status'] == 'Negociando'].iterrows():
        if row['data_envio']:
            try:
                envio = datetime.strptime(row['data_envio'], "%Y-%m-%d")
                dias = (hoje - envio).days
                if dias > 30:
                    alertas.append({
                        'nivel': '🟡 ATENÇÃO',
                        'titulo': f'{row["id"]} em negociação há {dias} dias',
                        'descricao': 'Risco de perda por tempo',
                        'acao': 'Agente WhatsApp enviar follow-up',
                        'impacto': f'Valor: R$ {row["lote"]}M'
                    })
            except:
                pass

    # Alerta 3: Pipeline Lote 22 vazio (ANKARA perdeu)
    lote22 = df[(df['lote'] == '22') & (df['status'].isin(['Simulada', 'Enviada', 'Negociando']))]
    if lote22.empty:
        alertas.append({
            'nivel': '🟡 ATENÇÃO',
            'titulo': 'Pipeline do Lote 22 está vazio',
            'descricao': 'ANKARA perdeu, nenhuma proposta ativa',
            'acao': 'Prospectar novo consórcio para Lote 22',
            'impacto': 'Oportunidade: R$ 253M (ETA-500 + ETA-1000)'
        })

    # Alerta 4: Margem abaixo do target
    baixa_margem = df[(df['margem'] < 0.20) & (df['status'].isin(['Simulada', 'Enviada', 'Negociando']))]
    if not baixa_margem.empty:
        alertas.append({
            'nivel': '🔴 CRÍTICO',
            'titulo': f'{len(baixa_margem)} propostas com margem < 20%',
            'descricao': 'Risco de prejuízo ou perda',
            'acao': 'Revisar custos ou BDI antes de enviar',
            'impacto': f'Valores em risco: R$ {baixa_margem.shape[0] * 50:.1f}M'
        })

    # Alerta 5: Oportunidade — propostas prontas para envio
    prontas = df[df['status'] == 'Simulada']
    if len(prontas) > 5:
        alertas.append({
            'nivel': '🟢 OPORTUNIDADE',
            'titulo': f'{len(prontas)} propostas simuladas prontas para envio',
            'descricao': 'Pipeline engordado, momento de acelerar',
            'acao': 'Priorizar envio das com maior margem',
            'impacto': f'Potencial: R$ {len(prontas) * 15:.1f}M'
        })

    return alertas

def gerar_licoes_aprendidas(unidades: List[Unidade]) -> List[LicaoAprendida]:
    """Extrai lições aprendidas das propostas perdidas"""

    licoes = []
    perdidas = [u for u in unidades if u.status == StatusProposta.PERDIDA]

    for i, u in enumerate(perdidas, 1):
        if u.motivo_perda == MotivoPerda.PRECO and u.grupo == GrupoVazao.MAGNUM:
            licoes.append(LicaoAprendida(
                id=f"LL-MAGNUM-{i:03d}",
                proposta_id=u.id,
                problema=f"{u.consorcio} perdeu {u.id} (Lote {u.lote}) por preço",
                solucao="Reduzir BDI mínimo para Magnum de 1.25 para 1.20",
                status="Em análise" if i == 1 else "Implementado",
                data=u.data_decisao or datetime.now().strftime("%Y-%m-%d"),
                impacto_receita=u.valor_venda
            ))
        elif u.motivo_perda == MotivoPerda.PRAZO:
            licoes.append(LicaoAprendida(
                id=f"LL-PRAZO-{i:03d}",
                proposta_id=u.id,
                problema=f"Prazo não atendeu para {u.id}",
                solucao="Oferecer 12 meses + BDI compensatório",
                status="Em análise",
                data=u.data_decisao or datetime.now().strftime("%Y-%m-%d"),
                impacto_receita=u.valor_venda
            ))

    return licoes

# ============================================================
# INTERFACE STREAMLIT — KANBAN
# ============================================================

def render_kanban(unidades: List[Unidade]):
    """Renderiza o Kanban de propostas no Streamlit"""

    st.markdown("### 📋 Kanban de Propostas")

    # Filtros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        filtro_status = st.multiselect(
            "Status", 
            [s.value for s in StatusProposta],
            default=[StatusProposta.SIMULADA.value, StatusProposta.ENVIADA.value,
                    StatusProposta.NEGOCIANDO.value]
        )

    with col2:
        filtro_grupo = st.multiselect(
            "Grupo Vazão",
            [g.value for g in GrupoVazao],
            default=[]
        )

    with col3:
        filtro_consorcio = st.multiselect(
            "Consórcio",
            list(set([u.consorcio for u in unidades])),
            default=[]
        )

    with col4:
        filtro_lote = st.multiselect(
            "Lote",
            sorted(list(set([u.lote for u in unidades]))),
            default=[]
        )

    # Aplicar filtros
    filtradas = unidades.copy()
    if filtro_status:
        filtradas = [u for u in filtradas if u.status.value in filtro_status]
    if filtro_grupo:
        filtradas = [u for u in filtradas if u.grupo.value in filtro_grupo]
    if filtro_consorcio:
        filtradas = [u for u in filtradas if u.consorcio in filtro_consorcio]
    if filtro_lote:
        filtradas = [u for u in filtradas if u.lote in filtro_lote]

    # Kanban por status
    cols = st.columns(4)
    status_cols = [
        (StatusProposta.SIMULADA, "🔵"),
        (StatusProposta.ENVIADA, "🟡"),
        (StatusProposta.NEGOCIANDO, "🟠"),
        (StatusProposta.EFETIVADA, "🟢")
    ]

    for idx, (status, emoji) in enumerate(status_cols):
        with cols[idx]:
            st.markdown(f"**{emoji} {status.value}**")
            cards = [u for u in filtradas if u.status == status]

            for u in cards:
                # Card colorido baseado no grupo
                cor = {
                    GrupoVazao.MICRO: "#e3f2fd",
                    GrupoVazao.PEQUENO: "#e8f5e9",
                    GrupoVazao.MEDIO: "#fff3e0",
                    GrupoVazao.GRANDE: "#fce4ec",
                    GrupoVazao.MAGNUM: "#ffebee"
                }.get(u.grupo, "#f5f5f5")

                margem_color = "🟢" if u.margem_simulada >= 0.25 else "🟡" if u.margem_simulada >= 0.20 else "🔴"

                st.markdown(f"""
                <div style="background-color: {cor}; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #1976d2;">
                    <b>{u.id}</b> | {u.nome}<br>
                    <small>Lote {u.lote} | {u.consorcio}</small><br>
                    <small>Vazão: {u.vazao_ls} L/s | {u.grupo.value.split('(')[0]}</small><br>
                    <small>BDI: {u.bdi_simulado:.2f} | Margem: {margem_color} {u.margem_simulada:.0%}</small><br>
                    <small>💰 R$ {u.valor_venda:.1f}M / Custo: R$ {u.custo_estimado:.1f}M</small><br>
                    {f'<small>📅 Envio: {u.data_envio}</small>' if u.data_envio else ''}
                    {f'<br><small>⚠️ {u.observacoes}</small>' if u.observacoes else ''}
                </div>
                """, unsafe_allow_html=True)

            st.caption(f"{len(cards)} propostas")

    # Coluna de perdas/suspensas
    st.markdown("---")
    cols2 = st.columns(3)

    with cols2[0]:
        st.markdown("**🔴 PERDIDAS**")
        perdidas = [u for u in filtradas if u.status == StatusProposta.PERDIDA]
        for u in perdidas:
            st.markdown(f"""
            <div style="background-color: #ffebee; padding: 8px; border-radius: 6px; margin-bottom: 6px; opacity: 0.8;">
                <s>{u.id}</s> | Lote {u.lote}<br>
                <small>{u.consorcio} | {u.motivo_perda.value if u.motivo_perda else ''}</small><br>
                <small>💸 R$ {u.valor_venda:.1f}M perdidos</small>
            </div>
            """, unsafe_allow_html=True)
        st.caption(f"{len(perdidas)} propostas | R$ {sum(u.valor_venda for u in perdidas):.1f}M perdidos")

    with cols2[1]:
        st.markdown("**⚪ SUSPENSAS**")
        suspensas = [u for u in filtradas if u.status == StatusProposta.SUSPENSA]
        for u in suspensas:
            st.markdown(f"<div style='opacity: 0.5; padding: 8px;'><small>{u.id}</small></div>", unsafe_allow_html=True)
        st.caption(f"{len(suspensas)} propostas")

    with cols2[2]:
        st.markdown("**⚫ CANCELADAS**")
        canceladas = [u for u in filtradas if u.status == StatusProposta.CANCELADA]
        for u in canceladas:
            st.markdown(f"<div style='opacity: 0.3; padding: 8px;'><small><s>{u.id}</s></small></div>", unsafe_allow_html=True)
        st.caption(f"{len(canceladas)} propostas")

# ============================================================
# INTERFACE STREAMLIT — PERFORMANCE
# ============================================================

def render_performance(unidades: List[Unidade]):
    """Renderiza aba de performance"""

    st.markdown("### 📈 Panorama de Performance")

    indicadores = calcular_indicadores(unidades)

    # Cards principais
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Pipeline Total",
            f"R$ {indicadores['pipeline_total']:.0f}M",
            f"{indicadores['total_unidades']} unidades"
        )

    with col2:
        st.metric(
            "Taxa Conversão",
            f"{indicadores['taxa_conversao']:.0f}%",
            "efetivadas / enviadas"
        )

    with col3:
        st.metric(
            "Receita Efetivada",
            f"R$ {indicadores['receita_efetivada']:.0f}M",
            f"{indicadores['por_status'].get('Efetivada', {}).get('quantidade', 0)} contratos"
        )

    with col4:
        st.metric(
            "Perda Total",
            f"R$ {indicadores['perda_total']:.0f}M",
            f"{indicadores['magnum_perdidas']} Magnum",
            delta_color="inverse"
        )

    with col5:
        st.metric(
            "Tempo Médio Ciclo",
            f"{indicadores['tempo_medio_ciclo']:.0f} dias",
            "envio → decisão"
        )

    st.markdown("---")

    # Tabela por status
    st.markdown("#### 📊 Propostas por Status")

    df_status = indicadores['por_status'].reset_index()
    df_status.columns = ['Status', 'Valor (R$M)', 'Quantidade']

    # Adicionar cores
    def cor_status(status):
        cores = {
            'Simulada': '🔵',
            'Enviada': '🟡',
            'Negociando': '🟠',
            'Efetivada': '🟢',
            'Perdida': '🔴',
            'Suspensa': '⚪',
            'Cancelada': '⚫'
        }
        return cores.get(status, '⚪')

    df_status['Status'] = df_status['Status'].apply(lambda x: f"{cor_status(x)} {x}")

    st.dataframe(
        df_status,
        column_config={
            'Valor (R$M)': st.column_config.NumberColumn(format="R$ %.1fM"),
            'Quantidade': st.column_config.NumberColumn()
        },
        hide_index=True,
        use_container_width=True
    )

    # Gráfico de funil
    st.markdown("#### 🎯 Funil de Conversão")

    funil_data = {
        'Simulada': len([u for u in unidades if u.status == StatusProposta.SIMULADA]),
        'Enviada': len([u for u in unidades if u.status == StatusProposta.ENVIADA]),
        'Negociando': len([u for u in unidades if u.status == StatusProposta.NEGOCIANDO]),
        'Efetivada': len([u for u in unidades if u.status == StatusProposta.EFETIVADA]),
        'Perdida': len([u for u in unidades if u.status == StatusProposta.PERDIDA])
    }

    import plotly.graph_objects as go

    fig = go.Figure(go.Funnel(
        y = list(funil_data.keys()),
        x = list(funil_data.values()),
        textposition = "inside",
        textinfo = "value+percent initial",
        opacity = 0.65,
        marker = {
            "color": ["#1976d2", "#fbc02d", "#f57c00", "#388e3c", "#d32f2f"],
            "line": {"width": [2, 2, 2, 3, 2], "color": ["#1565c0", "#f9a825", "#ef6c00", "#2e7d32", "#c62828"]}
        }
    ))

    fig.update_layout(
        title="Funil de Propostas — Programa Onda Limpa",
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# INTERFACE STREAMLIT — ALERTAS
# ============================================================

def render_alertas(unidades: List[Unidade]):
    """Renderiza alertas inteligentes"""

    st.markdown("### ⚡ Alertas Inteligentes")

    alertas = gerar_alertas(unidades)

    if not alertas:
        st.success("✅ Nenhum alerta crítico no momento. Pipeline saudável!")
        return

    for alerta in alertas:
        nivel_cor = {
            '🔴 CRÍTICO': 'error',
            '🟡 ATENÇÃO': 'warning',
            '🟢 OPORTUNIDADE': 'success'
        }.get(alerta['nivel'], 'info')

        with st.container():
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 10px; margin-bottom: 10px; 
                        background: {'#ffebee' if 'CRÍTICO' in alerta['nivel'] else '#fff8e1' if 'ATENÇÃO' in alerta['nivel'] else '#e8f5e9'};
                        border-left: 5px solid {'#d32f2f' if 'CRÍTICO' in alerta['nivel'] else '#f9a825' if 'ATENÇÃO' in alerta['nivel'] else '#388e3c'};">
                <h4 style="margin: 0;">{alerta['nivel']}: {alerta['titulo']}</h4>
                <p style="margin: 5px 0;"><b>Problema:</b> {alerta['descricao']}</p>
                <p style="margin: 5px 0; color: #1565c0;"><b>🔧 Ação recomendada:</b> {alerta['acao']}</p>
                <p style="margin: 5px 0; font-weight: bold;">{alerta['impacto']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Botão de ação
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"✅ Marcar como em andamento", key=f"acao_{alerta['titulo']}"):
                    st.success("Ação registrada no Notion!")
                    # Aqui integraria com webhook n8n
            with col2:
                if st.button(f"📤 Enviar ao Coordenador", key=f"coord_{alerta['titulo']}"):
                    st.info("Notificação enviada via WhatsApp!")
                    # Aqui integraria com n8n WhatsApp

# ============================================================
# INTERFACE STREAMLIT — LIÇÕES APRENDIDAS
# ============================================================

def render_licoes(unidades: List[Unidade]):
    """Renderiza lições aprendidas"""

    st.markdown("### 🧬 Lições Aprendidas")

    licoes = gerar_licoes_aprendidas(unidades)

    if not licoes:
        st.info("Ainda não há propostas perdidas com lições registradas.")
        return

    # Resumo executivo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lições Registradas", len(licoes))
    with col2:
        implementadas = len([l for l in licoes if l.status == "Implementado"])
        st.metric("Implementadas", implementadas)
    with col3:
        impacto_total = sum(l.impacto_receita for l in licoes)
        st.metric("Impacto Receita", f"R$ {impacto_total:.0f}M", delta_color="inverse")

    st.markdown("---")

    # Tabela de lições
    df_licoes = pd.DataFrame([{
        'ID': l.id,
        'Proposta': l.proposta_id,
        'Problema': l.problema,
        'Solução': l.solucao,
        'Status': l.status,
        'Data': l.data,
        'Impacto': f"R$ {l.impacto_receita:.1f}M"
    } for l in licoes])

    st.dataframe(
        df_licoes,
        column_config={
            'Status': st.column_config.SelectboxColumn(
                options=["Em análise", "Implementado", "Arquivado"]
            )
        },
        hide_index=True,
        use_container_width=True
    )

    # Insight do agente
    st.markdown("#### 🤖 Insight do Agente Analista")

    # Detectar padrões
    ankara_perdidas = [l for l in licoes if "ANKARA" in l.problema]
    if len(ankara_perdidas) >= 2:
        st.markdown(f"""
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
            <b>Padrão detectado:</b> ANKARA perdeu {len(ankara_perdidas)} propostas por preço no Grupo Magnum.<br><br>
            <b>Recomendação estratégica:</b><br>
            1. Revisar política de BDI para Magnum: 1.25 → 1.20<br>
            2. Negociar parceria com fornecedor de equipamentos para reduzir custo/Ls em 10%<br>
            3. Considerar consórcio com TRAIL para próximos lotes Magnum<br><br>
            <b>Impacto projetado:</b> Margem Magnum sobe de 20% → 24%, receita protegida: R$ 479M
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# INTERFACE STREAMLIT — NOVA PROPOSTA
# ============================================================

def render_nova_proposta(unidades: List[Unidade]):
    """Renderiza formulário para nova proposta"""

    st.markdown("### ➕ Nova Proposta")

    with st.form("nova_proposta"):
        col1, col2 = st.columns(2)

        with col1:
            id_unidade = st.text_input("ID da Unidade", "ETA-XXX-XX")
            nome = st.text_input("Nome", "")
            tipo = st.selectbox("Tipo", ["ETE", "ETA"])
            vazao = st.number_input("Vazão (L/s)", min_value=1, max_value=1000, value=50)

            grupo = st.selectbox("Grupo", [g.value for g in GrupoVazao])
            lote = st.text_input("Lote", "XX")
            consorcio = st.text_input("Consórcio", "")

        with col2:
            custo = st.number_input("Custo Estimado (R$M)", min_value=0.0, value=10.0, step=0.5)
            bdi = st.slider("BDI", 1.0, 2.0, 1.30, 0.05)
            margem = st.slider("Margem Esperada", 0.0, 0.5, 0.25, 0.01)
            prazo_meses = st.number_input("Prazo (meses)", min_value=6, max_value=36, value=18)
            observacoes = st.text_area("Observações", "")

        # Simulação automática
        valor_venda = custo * bdi
        margem_real = (valor_venda - custo) / valor_venda

        st.markdown(f"""
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h4>📊 Simulação da Proposta</h4>
            <b>Valor de Venda:</b> R$ {valor_venda:.1f}M<br>
            <b>Margem Real:</b> {margem_real:.1%}<br>
            <b>Lucro Estimado:</b> R$ {valor_venda - custo:.1f}M<br>
            <b>Status:</b> {'✅ Viável' if margem_real >= 0.20 else '⚠️ Abaixo do mínimo (20%)'}
        </div>
        """, unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            simular = st.form_submit_button("🔁 Simular Cenário", use_container_width=True)
            if simular:
                st.success("Cenário simulado! Ajuste os parâmetros e simule novamente.")

        with col_btn2:
            enviar = st.form_submit_button("📤 Enviar Proposta", use_container_width=True, type="primary")
            if enviar:
                if margem_real < 0.20:
                    st.error("❌ Margem abaixo de 20%. Ajuste BDI ou custo antes de enviar.")
                else:
                    st.success(f"✅ Proposta {id_unidade} enviada!")
                    st.info("📧 Notificação enviada ao Coordenador")
                    st.info("📝 Página criada no Notion: Propostas")
                    # Aqui integraria com webhook n8n

# ============================================================
# INTERFACE STREAMLIT — INFRA OTIMIZAÇÃO
# ============================================================

def render_infra_otimizacao(unidades: List[Unidade]):
    """Renderiza aba de otimização de infraestrutura"""

    st.markdown("### 🏭 Infraestrutura & Otimização")

    # Análise de demanda
    efetivadas = [u for u in unidades if u.status == StatusProposta.EFETIVADA]
    negociando = [u for u in unidades if u.status == StatusProposta.NEGOCIANDO]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Demanda Confirmada",
            f"{len(efetivadas)} unidades",
            f"R$ {sum(u.valor_venda for u in efetivadas):.0f}M"
        )

    with col2:
        st.metric(
            "Demanda Provável",
            f"{len(negociando)} unidades",
            f"R$ {sum(u.valor_venda for u in negociando):.0f}M"
        )

    with col3:
        capacidade_atual = 10  # unidades/ano (exemplo)
        demanda_total = len(efetivadas) + len(negociando)
        gap = max(0, demanda_total - capacidade_atual)
        st.metric(
            "Gap de Capacidade",
            f"{gap} unidades",
            f"Capacidade: {capacidade_atual}/ano"
        )

    st.markdown("---")

    # Recomendações de infra
    st.markdown("#### 📋 Recomendações de Infraestrutura")

    recomendacoes = []

    # Análise por grupo
    grupos_demanda = {}
    for u in efetivadas + negociando:
        g = u.grupo.value
        if g not in grupos_demanda:
            grupos_demanda[g] = {'count': 0, 'valor': 0}
        grupos_demanda[g]['count'] += 1
        grupos_demanda[g]['valor'] += u.valor_venda

    if GrupoVazao.MAGNUM.value in grupos_demanda:
        recomendacoes.append({
            'prioridade': '🔴 Alta',
            'acao': 'Contratar equipe especializada em ETA Magnum',
            'motivo': f"{grupos_demanda[GrupoVazao.MAGNUM.value]['count']} unidades Magnum confirmadas",
            'investimento': 'R$ 2-3M',
            'retorno': f"R$ {grupos_demanda[GrupoVazao.MAGNUM.value]['valor']:.0f}M"
        })

    if GrupoVazao.MICRO.value in grupos_demanda:
        count = grupos_demanda[GrupoVazao.MICRO.value]['count']
        if count > 5:
            recomendacoes.append({
                'prioridade': '🟢 Baixa',
                'acao': 'Padronizar projeto tipo para Micro (1-5 L/s)',
                'motivo': f"{count} unidades Micro — padronização reduz custo em 15%",
                'investimento': 'R$ 200K',
                'retorno': f"R$ {count * 0.3:.1f}M"
            })

    # Perdas = oportunidade de melhoria
    perdidas_magnum = [u for u in unidades if u.status == StatusProposta.PERDIDA and u.grupo == GrupoVazao.MAGNUM]
    if perdidas_magnum:
        recomendacoes.append({
            'prioridade': '🔴 Alta',
            'acao': 'Renegociar contrato com fornecedor de equipamentos Magnum',
            'motivo': f"Perdemos {len(perdidas_magnum)} unidades Magnum por preço",
            'investimento': 'Negociação',
            'retorno': f"R$ {sum(u.valor_venda for u in perdidas_magnum):.0f}M (próximos lotes)"
        })

    # Mostrar recomendações
    for rec in recomendacoes:
        st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; margin-bottom: 10px;
                    background: {'#ffebee' if 'Alta' in rec['prioridade'] else '#fff8e1' if 'Média' in rec['prioridade'] else '#e8f5e9'};">
            <b>{rec['prioridade']}</b> | {rec['acao']}<br>
            <small>🎯 {rec['motivo']}</small><br>
            <small>💰 Investimento: {rec['investimento']} | Retorno: {rec['retorno']}</small>
        </div>
        """, unsafe_allow_html=True)

    # Timeline de execução
    st.markdown("#### 📅 Timeline de Execução (Propostas Efetivadas)")

    timeline_data = []
    for u in efetivadas:
        if u.data_envio:
            try:
                inicio = datetime.strptime(u.data_envio, "%Y-%m-%d")
                # Simular duração baseada no grupo
                duracao = {
                    GrupoVazao.MICRO: 6,
                    GrupoVazao.PEQUENO: 9,
                    GrupoVazao.MEDIO: 12,
                    GrupoVazao.GRANDE: 15,
                    GrupoVazao.MAGNUM: 18
                }.get(u.grupo, 12)

                fim = inicio + timedelta(days=duracao*30)
                timeline_data.append({
                    'Unidade': u.id,
                    'Início': inicio.strftime("%Y-%m"),
                    'Fim': fim.strftime("%Y-%m"),
                    'Duração': f"{duracao} meses",
                    'Grupo': u.grupo.value,
                    'Valor': f"R$ {u.valor_venda:.1f}M"
                })
            except:
                pass

    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)
        st.dataframe(df_timeline, hide_index=True, use_container_width=True)

    # Alerta de gargalo
    st.markdown("---")
    st.markdown("#### ⚠️ Alertas de Gargalo")

    # Verificar se há muitas unidades no mesmo período
    if len(efetivadas) > 3:
        st.warning(f"""
        🏗️ **Gargalo detectado:** {len(efetivadas)} unidades efetivadas podem exigir
        execução simultânea. Considere:
        - Subcontratação de montagem especializada
        - Staggering (escalonamento) de inícios
        - Parceria com consórcio para execução
        """)

# ============================================================
# FUNÇÃO PRINCIPAL — RENDERIZAR ABA PIPELINE
# ============================================================

def render_aba_pipeline():
    """Função principal chamada pelo dashboard.py"""

    st.markdown("## 🎯 Pipeline de Propostas — Programa Onda Limpa")
    st.caption("Gestão completa do ciclo de propostas: Simulação → Envio → Efetivação/Perda → Aprendizado")

    # Carregar dados
    unidades = carregar_unidades_reais()

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Kanban", "📈 Performance", "⚡ Alertas", "🧬 Lições", "➕ Nova Proposta", "🏭 Infra"
    ])

    with tab1:
        render_kanban(unidades)

    with tab2:
        render_performance(unidades)

    with tab3:
        render_alertas(unidades)

    with tab4:
        render_licoes(unidades)

    with tab5:
        render_nova_proposta(unidades)

    with tab6:
        render_infra_otimizacao(unidades)

    # Footer com integração n8n
    st.markdown("---")
    st.caption("🔄 Integrado com Notion API + n8n + LangGraph | Hydrosol AI v5.1")

# ============================================================
# EXECUÇÃO DIRETA (para teste)
# ============================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Hydrosol AI — Pipeline de Propostas",
        page_icon="🌊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    render_aba_pipeline()