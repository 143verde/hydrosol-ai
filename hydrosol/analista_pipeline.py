
"""
🤖 Hydrosol AI — Agente Analista de Pipeline v5.1
Agente LangGraph para análise de propostas perdidas, padrões e recomendações estratégicas.
Integra com Notion API + n8n.
"""

from typing import TypedDict, List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# ============================================================
# TIPOS E ESTRUTURAS
# ============================================================

class EstadoAnalise(TypedDict):
    propostas_perdidas: List[Dict]
    propostas_efetivadas: List[Dict]
    padroes_detectados: List[Dict]
    recomendacoes: List[Dict]
    alertas: List[Dict]
    lições: List[Dict]

@dataclass
class PadraoDetectado:
    tipo: str  # "preço", "prazo", "escopo", "consórcio"
    frequencia: int
    consorcio_afetado: str
    grupo_vazao: str
    impacto_receita: float
    confianca: float  # 0.0 a 1.0
    evidencia: List[str]

@dataclass
class RecomendacaoEstrategica:
    id: str
    titulo: str
    descricao: str
    impacto_esperado: str
    investimento_necessario: str
    prazo_implementacao: str
    prioridade: str  # "P1", "P2", "P3"
    status: str  # "Em análise", "Aprovada", "Implementada"

# ============================================================
# AGENTE ANALISTA — MOTOR DE ANÁLISE
# ============================================================

class AgenteAnalistaPipeline:
    """
    Agente autônomo que analisa o pipeline de propostas,
    detecta padrões de perda e gera recomendações estratégicas.
    """

    def __init__(self):
        self.historico_analises = []
        self.threshold_confianca = 0.7

    def analisar_pipeline(self, propostas: List[Dict]) -> EstadoAnalise:
        """
        Analisa todo o pipeline e retorna estado completo.

        Args:
            propostas: Lista de dicionários com dados das propostas

        Returns:
            EstadoAnalise com padrões, recomendações e alertas
        """

        estado = EstadoAnalise(
            propostas_perdidas=[],
            propostas_efetivadas=[],
            padroes_detectados=[],
            recomendacoes=[],
            alertas=[],
            lições=[]
        )

        # Separar propostas
        estado["propostas_perdidas"] = [p for p in propostas if p.get("status") == "Perdida"]
        estado["propostas_efetivadas"] = [p for p in propostas if p.get("status") == "Efetivada"]

        # Detectar padrões
        estado["padroes_detectados"] = self._detectar_padroes(estado["propostas_perdidas"])

        # Gerar recomendações
        estado["recomendacoes"] = self._gerar_recomendacoes(
            estado["padroes_detectados"],
            estado["propostas_perdidas"]
        )

        # Gerar alertas
        estado["alertas"] = self._gerar_alertas(
            estado["padroes_detectados"],
            propostas
        )

        # Extrair lições
        estado["lições"] = self._extrair_licoes(estado["propostas_perdidas"])

        # Registrar análise
        self.historico_analises.append({
            "data": datetime.now().isoformat(),
            "propostas_analisadas": len(propostas),
            "padroes_encontrados": len(estado["padroes_detectados"]),
            "recomendacoes_geradas": len(estado["recomendacoes"])
        })

        return estado

    def _detectar_padroes(self, perdidas: List[Dict]) -> List[PadraoDetectado]:
        """Detecta padrões nas propostas perdidas"""

        padroes = []

        if not perdidas:
            return padroes

        # Padrão 1: Consórcio repetidamente perde por preço
        consorcios = {}
        for p in perdidas:
            cons = p.get("consorcio", "Desconhecido")
            motivo = p.get("motivo_perda", "")
            if cons not in consorcios:
                consorcios[cons] = {"total": 0, "preco": 0, "prazo": 0, "outro": 0}
            consorcios[cons]["total"] += 1
            if "preço" in motivo.lower() or "preco" in motivo.lower():
                consorcios[cons]["preco"] += 1
            elif "prazo" in motivo.lower():
                consorcios[cons]["prazo"] += 1
            else:
                consorcios[cons]["outro"] += 1

        for cons, dados in consorcios.items():
            if dados["total"] >= 2 and dados["preco"] >= 2:
                # Calcular impacto
                impacto = sum(
                    p.get("valor_venda", 0) 
                    for p in perdidas 
                    if p.get("consorcio") == cons
                )

                padroes.append(PadraoDetectado(
                    tipo="preço",
                    frequencia=dados["preco"],
                    consorcio_afetado=cons,
                    grupo_vazao=self._inferir_grupo(perdidas, cons),
                    impacto_receita=impacto,
                    confianca=min(0.95, 0.6 + dados["preco"] * 0.15),
                    evidencia=[
                        f"{cons} perdeu {dados['preco']} propostas por preço",
                        f"Total de perdas: {dados['total']}",
                        f"Impacto: R$ {impacto:.1f}M"
                    ]
                ))

        # Padrão 2: Grupo Magnum com margem baixa
        magnum_perdidas = [p for p in perdidas if "magnum" in p.get("grupo", "").lower()]
        if len(magnum_perdidas) >= 2:
            impacto = sum(p.get("valor_venda", 0) for p in magnum_perdidas)
            padroes.append(PadraoDetectado(
                tipo="preço",
                frequencia=len(magnum_perdidas),
                consorcio_afetado="Múltiplos",
                grupo_vazao="Magnum",
                impacto_receita=impacto,
                confianca=0.85,
                evidencia=[
                    f"{len(magnum_perdidas)} unidades Magnum perdidas",
                    "BDI 1.25 não competitivo para este grupo",
                    f"Impacto: R$ {impacto:.1f}M"
                ]
            ))

        # Padrão 3: Prazo como fator de perda
        prazo_perdidas = [p for p in perdidas if "prazo" in p.get("motivo_perda", "").lower()]
        if len(prazo_perdidas) >= 2:
            impacto = sum(p.get("valor_venda", 0) for p in prazo_perdidas)
            padroes.append(PadraoDetectado(
                tipo="prazo",
                frequencia=len(prazo_perdidas),
                consorcio_afetado="Múltiplos",
                grupo_vazao="Variado",
                impacto_receita=impacto,
                confianca=0.75,
                evidencia=[
                    f"{len(prazo_perdidas)} propostas perdidas por prazo",
                    "Prazo médio de execução não atende expectativa Sabesp"
                ]
            ))

        return padroes

    def _gerar_recomendacoes(
        self, 
        padroes: List[PadraoDetectado], 
        perdidas: List[Dict]
    ) -> List[RecomendacaoEstrategica]:
        """Gera recomendações baseadas nos padrões detectados"""

        recomendacoes = []

        for padrao in padroes:
            if padrao.confianca < self.threshold_confianca:
                continue

            if padrao.tipo == "preço" and padrao.grupo_vazao == "Magnum":
                recomendacoes.append(RecomendacaoEstrategica(
                    id="REC-MAGNUM-001",
                    titulo="Revisar política de BDI para Grupo Magnum",
                    descricao=(
                        f"Análise detectou que {padrao.frequencia} propostas Magnum "
                        f"foram perdidas por preço (BDI 1.25). "
                        f"Concorrentes oferecem BDI entre 1.18-1.22. "
                        f"Reduzir BDI mínimo para 1.20 pode aumentar taxa de conversão em 15-20%."
                    ),
                    impacto_esperado=f"Proteger R$ {padrao.impacto_receita:.0f}M em receita futura",
                    investimento_necessario="Negociação com fornecedores (sem custo direto)",
                    prazo_implementacao="7 dias",
                    prioridade="P1",
                    status="Em análise"
                ))

                recomendacoes.append(RecomendacaoEstrategica(
                    id="REC-MAGNUM-002",
                    titulo="Negociar parceria estratégica com fornecedor de equipamentos",
                    descricao=(
                        "Reduzir custo/Ls em 10% através de contrato de volume "
                        "para equipamentos de ETA 500-1000 L/s."
                    ),
                    impacto_esperado="Margem sobe de 20% → 24% sem reduzir BDI",
                    investimento_necessario="R$ 500K (adiantamento para desconto)",
                    prazo_implementacao="30 dias",
                    prioridade="P1",
                    status="Em análise"
                ))

            elif padrao.tipo == "preço" and padrao.consorcio_afetado != "Múltiplos":
                recomendacoes.append(RecomendacaoEstrategica(
                    id=f"REC-CONS-{padrao.consorcio_afetado[:3].upper()}-001",
                    titulo=f"Revisar estratégia de pricing do consórcio {padrao.consorcio_afetado}",
                    descricao=(
                        f"{padrao.consorcio_afetado} perdeu {padrao.frequencia} propostas. "
                        f"Recomenda-se análise de competitividade de preços "
                        f"e possível reestruturação do consórcio."
                    ),
                    impacto_esperado=f"Recuperar R$ {padrao.impacto_receita:.0f}M em oportunidades",
                    investimento_necessario="Consultoria de pricing (R$ 50K)",
                    prazo_implementacao="15 dias",
                    prioridade="P2",
                    status="Em análise"
                ))

            elif padrao.tipo == "prazo":
                recomendacoes.append(RecomendacaoEstrategica(
                    id="REC-PRAZO-001",
                    titulo="Reduzir prazo de execução para grupos Pequeno e Micro",
                    descricao=(
                        f"{padrao.frequencia} propostas perdidas por prazo excessivo. "
                        f"Padronização de projeto tipo pode reduzir prazo de 18 para 12 meses "
                        f"para unidades até 20 L/s."
                    ),
                    impacto_esperado="Aumentar taxa de conversão em 10%",
                    investimento_necessario="R$ 200K (desenvolvimento projeto tipo)",
                    prazo_implementacao="45 dias",
                    prioridade="P2",
                    status="Em análise"
                ))

        # Recomendação genérica se não houver padrões específicos
        if not recomendacoes and perdidas:
            recomendacoes.append(RecomendacaoEstrategica(
                id="REC-GERAL-001",
                titulo="Implementar sistema de feedback pós-perda",
                descricao=(
                    "Criar processo formal para coletar motivos detalhados de perda "
                    "diretamente com a Sabesp e concorrentes."
                ),
                impacto_esperado="Melhorar qualidade de dados para análise futura",
                investimento_necessario="R$ 30K (processo + treinamento)",
                prazo_implementacao="15 dias",
                prioridade="P3",
                status="Em análise"
            ))

        return recomendacoes

    def _gerar_alertas(
        self, 
        padroes: List[PadraoDetectado],
        todas_propostas: List[Dict]
    ) -> List[Dict]:
        """Gera alertas operacionais"""

        alertas = []

        # Alerta de perda em série
        for padrao in padroes:
            if padrao.frequencia >= 3:
                alertas.append({
                    "nivel": "CRÍTICO",
                    "titulo": f"Série de perdas detectada: {padrao.consorcio_afetado}",
                    "mensagem": (
                        f"{padrao.frequencia} propostas perdidas consecutivas. "
                        f"Impacto acumulado: R$ {padrao.impacto_receita:.1f}M"
                    ),
                    "acao_recomendada": "Reunião de crise em 24h",
                    "prazo": "24 horas"
                })
            elif padrao.frequencia == 2:
                alertas.append({
                    "nivel": "ATENÇÃO",
                    "titulo": f"Padrão de perda emergente: {padrao.tipo}",
                    "mensagem": (
                        f"2 propostas perdidas por {padrao.tipo}. "
                        f"Monitorar próximas propostas do grupo {padrao.grupo_vazao}."
                    ),
                    "acao_recomendada": "Análise de pricing em 48h",
                    "prazo": "48 horas"
                })

        # Alerta de pipeline vazio
        lotes_ativos = set()
        for p in todas_propostas:
            if p.get("status") in ["Simulada", "Enviada", "Negociando"]:
                lotes_ativos.add(p.get("lote", ""))

        todos_lotes = set(p.get("lote", "") for p in todas_propostas)
        lotes_vazios = todos_lotes - lotes_ativos

        for lote in lotes_vazios:
            if lote:
                alertas.append({
                    "nivel": "ATENÇÃO",
                    "titulo": f"Pipeline vazio: Lote {lote}",
                    "mensagem": "Nenhuma proposta ativa neste lote.",
                    "acao_recomendada": "Prospectar novo consórcio",
                    "prazo": "7 dias"
                })

        return alertas

    def _extrair_licoes(self, perdidas: List[Dict]) -> List[Dict]:
        """Extrai lições aprendidas formatadas"""

        licoes = []

        for i, p in enumerate(perdidas, 1):
            licoes.append({
                "id": f"LL-{i:03d}",
                "proposta_id": p.get("id", "DESCONHECIDO"),
                "unidade": p.get("id", ""),
                "lote": p.get("lote", ""),
                "consorcio": p.get("consorcio", ""),
                "motivo_perda": p.get("motivo_perda", ""),
                "valor_perdido": p.get("valor_venda", 0),
                "data": p.get("data_decisao", datetime.now().strftime("%Y-%m-%d")),
                "recomendacao": self._gerar_recomendacao_licao(p),
                "status": "Nova"
            })

        return licoes

    def _gerar_recomendacao_licao(self, proposta: Dict) -> str:
        """Gera recomendação específica para uma lição"""

        motivo = proposta.get("motivo_perda", "").lower()
        grupo = proposta.get("grupo", "").lower()

        if "preço" in motivo:
            if "magnum" in grupo:
                return "Reduzir BDI mínimo Magnum para 1.20; negociar desconto com fornecedor"
            else:
                return "Revisar custos diretos; avaliar economia de escala"

        elif "prazo" in motivo:
            return "Padronizar projeto tipo; considerar modularização"

        elif "escopo" in motivo:
            return "Ampliar escopo proposta; incluir O&M no contrato"

        elif "consórcio" in motivo or "consorcio" in motivo:
            return "Avaliar reestruturação do consórcio; buscar parceiro local"

        else:
            return "Investigar motivo detalhado com Sabesp; registrar feedback"

    def _inferir_grupo(self, perdidas: List[Dict], consorcio: str) -> str:
        """Infere o grupo de vazão predominante para um consórcio"""

        grupos = [p.get("grupo", "") for p in perdidas if p.get("consorcio") == consorcio]
        if not grupos:
            return "Desconhecido"

        # Retorna o mais frequente
        from collections import Counter
        return Counter(grupos).most_common(1)[0][0]

    def gerar_relatorio_executivo(self, estado: EstadoAnalise) -> str:
        """Gera relatório em formato texto para envio via WhatsApp/email"""

        relatorio = f"""
🌊 *HYDROSOL AI — Relatório de Pipeline*
📅 {datetime.now().strftime("%d/%m/%Y %H:%M")}

*RESUMO EXECUTIVO*
• Propostas perdidas: {len(estado["propostas_perdidas"])}
• Receita em risco: R$ {sum(p.get('valor_venda', 0) for p in estado['propostas_perdidas']):.1f}M
• Padrões detectados: {len(estado['padroes_detectados'])}
• Recomendações: {len(estado['recomendacoes'])}

*PADRÕES CRÍTICOS*
"""

        for padrao in estado["padroes_detectados"]:
            relatorio += f"""
🔴 {padrao.tipo.upper()} — {padrao.consorcio_afetado}
   Frequência: {padrao.frequencia}x | Impacto: R$ {padrao.impacto_receita:.1f}M
   Confiança: {padrao.confianca:.0%}
"""

        relatorio += "
*RECOMENDAÇÕES PRIORITÁRIAS*
"

        for rec in estado["recomendacoes"]:
            if rec.prioridade == "P1":
                relatorio += f"""
🔴 *{rec.titulo}*
   {rec.impacto_esperado}
   Prazo: {rec.prazo_implementacao}
"""

        relatorio += "
*AÇÕES IMEDIATAS*
"

        for alerta in estado["alertas"]:
            if alerta["nivel"] == "CRÍTICO":
                relatorio += f"""
⚠️ {alerta["titulo"]} — {alerta["prazo"]}
"""

        relatorio += "
🤖 *Análise gerada pelo Agente Analista de Pipeline*"

        return relatorio

# ============================================================
# FUNÇÃO PARA STREAMLIT
# ============================================================

def render_analista_pipeline(propostas: List[Dict] = None):
    """
    Renderiza interface do agente analista no Streamlit.
    Pode receber propostas como parâmetro ou usar dados de exemplo.
    """

    import streamlit as st

    st.markdown("## 🤖 Agente Analista de Pipeline")
    st.caption("Análise autônoma de padrões, perdas e recomendações estratégicas")

    # Dados de exemplo se não receber
    if propostas is None:
        propostas = [
            {"id": "ETA-500-02", "status": "Perdida", "consorcio": "ANKARA", 
             "grupo": "Magnum (500-1000 L/s)", "motivo_perda": "Preço maior que concorrente",
             "valor_venda": 92.5, "lote": "22", "data_decisao": "2026-05-08"},
            {"id": "ETA-500-03", "status": "Perdida", "consorcio": "ANKARA",
             "grupo": "Magnum (500-1000 L/s)", "motivo_perda": "Preço maior que concorrente",
             "valor_venda": 92.5, "lote": "24", "data_decisao": "2026-04-25"},
            {"id": "ETE-150-01", "status": "Efetivada", "consorcio": "TRAIL",
             "grupo": "Grande (129-200 L/s)", "valor_venda": 36.5, "lote": "15"},
        ]

    # Inicializar agente
    agente = AgenteAnalistaPipeline()

    # Executar análise
    with st.spinner("🤖 Agente analisando pipeline..."):
        estado = agente.analisar_pipeline(propostas)

    # Mostrar resultados
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Perdas Analisadas", len(estado["propostas_perdidas"]))
    with col2:
        st.metric("Padrões Detectados", len(estado["padroes_detectados"]))
    with col3:
        st.metric("Recomendações", len(estado["recomendacoes"]))
    with col4:
        st.metric("Alertas", len(estado["alertas"]))

    st.markdown("---")

    # Padrões detectados
    if estado["padroes_detectados"]:
        st.markdown("### 🔍 Padrões Detectados")

        for padrao in estado["padroes_detectados"]:
            cor = "#d32f2f" if padrao.confianca > 0.8 else "#f9a825"

            with st.container():
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; margin-bottom: 10px;
                            background: rgba(255,255,255,0.03); 
                            border-left: 4px solid {cor};">
                    <h4 style="margin: 0; color: {cor};">
                        {padrao.tipo.upper()} — {padrao.consorcio_afetado}
                    </h4>
                    <p style="margin: 5px 0; color: #b0bec5;">
                        Frequência: <b>{padrao.frequencia}x</b> | 
                        Impacto: <b>R$ {padrao.impacto_receita:.1f}M</b> |
                        Confiança: <b>{padrao.confianca:.0%}</b>
                    </p>
                    <p style="margin: 5px 0; color: #90a4ae; font-size: 12px;">
                        Grupo: {padrao.grupo_vazao}
                    </p>
                    <details>
                        <summary style="color: #64b5f6; cursor: pointer;">Ver evidências</summary>
                        <ul style="color: #90a4ae; font-size: 12px;">
                            {''.join(f'<li>{e}</li>' for e in padrao.evidencia)}
                        </ul>
                    </details>
                </div>
                """, unsafe_allow_html=True)

    # Recomendações
    if estado["recomendacoes"]:
        st.markdown("### 💡 Recomendações Estratégicas")

        for rec in estado["recomendacoes"]:
            cor = {"P1": "#d32f2f", "P2": "#f9a825", "P3": "#66bb6a"}.get(rec.prioridade, "#78909c")

            with st.container():
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; margin-bottom: 10px;
                            background: rgba(255,255,255,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: {cor}; font-weight: bold; font-size: 12px;">
                            ● {rec.prioridade}
                        </span>
                        <span style="color: #78909c; font-size: 11px;">{rec.prazo_implementacao}</span>
                    </div>
                    <h4 style="margin: 10px 0; color: #e3f2fd;">{rec.titulo}</h4>
                    <p style="color: #b0bec5; font-size: 13px;">{rec.descricao}</p>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                        <span style="color: #81c784; font-size: 12px;">🎯 {rec.impacto_esperado}</span>
                        <span style="color: #ffa726; font-size: 12px;">💰 {rec.investimento_necessario}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button(f"✅ Aprovar", key=f"aprovar_{rec.id}"):
                        st.success(f"Recomendação {rec.id} aprovada!")
                        # Aqui integraria com n8n para criar tarefa no Notion
                with col2:
                    if st.button(f"📤 Enviar ao Coordenador", key=f"coord_{rec.id}"):
                        st.info("Notificação enviada via WhatsApp!")

    # Relatório executivo
    st.markdown("---")
    st.markdown("### 📄 Relatório Executivo")

    relatorio = agente.gerar_relatorio_executivo(estado)

    st.text_area("Relatório para WhatsApp/Email", relatorio, height=300)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copiar Relatório"):
            st.success("Relatório copiado para clipboard!")
    with col2:
        if st.button("📤 Enviar via WhatsApp"):
            st.info("Enviando via n8n webhook...")
            # Aqui integraria com webhook n8n WhatsApp

# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":
    import streamlit as st

    st.set_page_config(
        page_title="Agente Analista — Hydrosol AI",
        page_icon="🤖",
        layout="wide"
    )

    render_analista_pipeline()