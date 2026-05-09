"""
================================================================================
HYDROSOL AI - AGENTES LANGGRAPH v5.1
Orquestracao de Agentes Autonomos para Gestao de ETE/ETA
Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
================================================================================
Stack: LangGraph + LangChain + Python
Funcoes: Agente de Margem | Agente de Risco | Agente de Cronograma | Agente de NF
================================================================================
"""

import json
import os
from typing import Dict, List, TypedDict, Annotated, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import requests

# LangGraph / LangChain
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

# ==============================================================================
# TIPOS E ESTADOS
# ==============================================================================

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AgentType(Enum):
    MARGEM = "agente_margem"
    RISCO = "agente_risco"
    CRONOGRAMA = "agente_cronograma"
    NOTA_FISCAL = "agente_nota_fiscal"
    COORDENADOR = "agente_coordenador"

class TipoAcao(Enum):
    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    REVISAR = "revisar"
    ALERTAR = "alertar"
    AUTOMATIZAR = "automatizar"

# Estado compartilhado entre agentes (LangGraph State)
class HydrosolState(TypedDict):
    """Estado global do grafo de agentes Hydrosol."""
    # Contexto do projeto
    projeto_id: str
    projeto_nome: str
    vazao_ls: float
    grupo: str
    etapa_atual: int

    # Dados financeiros
    custo_real: float
    custo_orcado: float
    margem_atual: float
    margem_alvo: float

    # Dados operacionais
    prazo_atual: Optional[datetime]
    prazo_alvo: Optional[datetime]
    dias_atraso: int

    # Notas fiscais
    nfs_pendentes: List[Dict]
    nf_atual: Optional[Dict]

    # Riscos
    riscos_ativos: List[Dict]
    nivel_risco: AlertLevel

    # Comunicacao
    mensagens: List[Dict]  # Historico de mensagens entre agentes
    alertas_pendentes: List[Dict]

    # Decisoes
    decisao_requerida: bool
    acao_sugerida: Optional[TipoAcao]
    justificativa: str

    # Controle do grafo
    proximo_agente: str
    iteracao: int
    max_iteracoes: int

# ==============================================================================
# FERRAMENTAS COMPARTILHADAS (Tools)
# ==============================================================================

@tool
def calcular_margem(custo_real: float, custo_orcado: float, receita: float) -> Dict:
    """Calcula margem bruta e liquida de um projeto."""
    margem_bruta = receita - custo_real
    margem_bruta_pct = (margem_bruta / receita) * 100 if receita > 0 else 0
    margem_liquida_pct = margem_bruta_pct * 0.85  # Desconto impostos/admin
    desvio_orcamento = ((custo_real - custo_orcado) / custo_orcado) * 100 if custo_orcado > 0 else 0

    return {
        "margem_bruta_rs": margem_bruta,
        "margem_bruta_pct": round(margem_bruta_pct, 2),
        "margem_liquida_pct": round(margem_liquida_pct, 2),
        "desvio_orcamento_pct": round(desvio_orcamento, 2),
        "status": "Dentro do target" if margem_liquida_pct >= 28 else "Abaixo do target" if margem_liquida_pct >= 20 else "Critico"
    }

@tool
def avaliar_risco(nivel_risco: str, impacto_financeiro: float, probabilidade: float) -> Dict:
    """Avalia risco e retorna score e acoes recomendadas."""
    score = impacto_financeiro * probabilidade / 1e6  # Score em milhoes

    if score > 50:
        nivel = AlertLevel.EMERGENCY
        acoes = ["Bloquear pagamentos", "Convocar reuniao de crise", "Notificar diretoria"]
    elif score > 20:
        nivel = AlertLevel.CRITICAL
        acoes = ["Revisar cronograma", "Realocar recursos", "Alertar coordenador"]
    elif score > 5:
        nivel = AlertLevel.WARNING
        acoes = ["Monitorar diariamente", "Preparar plano de contingencia"]
    else:
        nivel = AlertLevel.INFO
        acoes = ["Acompanhamento normal"]

    return {
        "score_risco": round(score, 2),
        "nivel": nivel.value,
        "acoes_recomendadas": acoes,
        "requer_aprovacao": nivel in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]
    }

@tool
def verificar_cronograma(data_inicio: str, data_fim: str, progresso_pct: float) -> Dict:
    """Verifica se o cronograma esta dentro do prazo."""
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    fim = datetime.strptime(data_fim, "%Y-%m-%d")
    hoje = datetime.now()

    duracao_total = (fim - inicio).days
    dias_passados = (hoje - inicio).days
    progresso_esperado = (dias_passados / duracao_total) * 100 if duracao_total > 0 else 0
    desvio = progresso_pct - progresso_esperado

    dias_atraso = int((desvio / 100) * duracao_total * -1) if desvio < 0 else 0

    return {
        "progresso_esperado": round(progresso_esperado, 1),
        "progresso_real": progresso_pct,
        "desvio_pct": round(desvio, 1),
        "dias_atraso": dias_atraso,
        "status": "No prazo" if desvio >= -5 else "Atrasado leve" if desvio >= -15 else "Atrasado critico"
    }

@tool
def validar_nota_fiscal(numero_nf: str, valor: float, cnpj_fornecedor: str, projeto_id: str) -> Dict:
    """Valida nota fiscal contra orcamento do projeto."""
    # Simulacao - em producao consultaria database
    limite_projeto = 5_000_000.0  # Exemplo

    status = "Aprovada" if valor <= limite_projeto else "Pendente Aprovacao"

    return {
        "numero_nf": numero_nf,
        "valor": valor,
        "status": status,
        "limite_projeto": limite_projeto,
        "saldo_restante": limite_projeto - valor,
        "requer_aprovacao_coordenador": valor > limite_projeto * 0.5,
        "pode_automatizar": valor <= 100_000.0  # NF ate 100k pode ser automatica
    }

@tool
def enviar_whatsapp(numero: str, mensagem: str, tipo: str = "alerta") -> Dict:
    """Envia mensagem via WhatsApp Business API (n8n webhook)."""
    # Endpoint do n8n (configurar no .env)
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_WHATSAPP", "http://localhost:5678/webhook/whatsapp")

    payload = {
        "numero": numero,
        "mensagem": mensagem,
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "origem": "LangGraph-Agente-Hydrosol"
    }

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        return {
            "status": "enviado" if response.status_code == 200 else "falha",
            "response_code": response.status_code,
            "payload": payload
        }
    except Exception as e:
        return {"status": "erro", "erro": str(e), "payload": payload}

@tool
def enviar_notion(database_id: str, dados: Dict) -> Dict:
    """Envia dados para database do Notion via API."""
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": dados
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return {"status": "sucesso" if response.status_code == 200 else "falha", "data": response.json()}
    except Exception as e:
        return {"status": "erro", "erro": str(e)}

# Lista de ferramentas disponiveis
TOOLS = [calcular_margem, avaliar_risco, verificar_cronograma, validar_nota_fiscal, enviar_whatsapp, enviar_notion]

# ==============================================================================
# AGENTES ESPECIALIZADOS (Nodes do Grafo)
# ==============================================================================

def agente_margem(state: HydrosolState) -> HydrosolState:
    """
    Agente de Margem: Monitora custos vs orcamento e protege o target de 28-31%.
    """
    print(f"\n🤖 [AGENTE MARGEM] Analisando projeto {state['projeto_nome']}...")

    # Calcular margem atual
    receita = state["custo_orcado"] * 1.35  # Estimativa baseada em BDI
    resultado = calcular_margem.invoke({
        "custo_real": state["custo_real"],
        "custo_orcado": state["custo_orcado"],
        "receita": receita
    })

    margem_liq = resultado["margem_liquida_pct"]
    state["margem_atual"] = margem_liq

    # Logica de decisao
    if margem_liq < 20:
        acao = TipoAcao.REJEITAR
        justificativa = f"Margem liquida critica: {margem_liq}%. Abaixo do minimo aceitavel (20%)."
        alerta = {
            "nivel": AlertLevel.EMERGENCY.value,
            "agente": AgentType.MARGEM.value,
            "mensagem": f"🚨 MARGEM CRITICA: {state['projeto_nome']} - {margem_liq}%",
            "acao": "Bloquear novos gastos e convocar reuniao de emergencia"
        }
    elif margem_liq < 28:
        acao = TipoAcao.REVISAR
        justificativa = f"Margem liquida {margem_liq}% abaixo do target (28-31%). Requer acao corretiva."
        alerta = {
            "nivel": AlertLevel.WARNING.value,
            "agente": AgentType.MARGEM.value,
            "mensagem": f"⚠️ Margem abaixo do target: {state['projeto_nome']} - {margem_liq}%",
            "acao": "Revisar custos e negociar com fornecedores"
        }
    else:
        acao = TipoAcao.APROVAR
        justificativa = f"Margem liquida {margem_liq}% dentro do target. Projeto saudavel."
        alerta = None

    state["acao_sugerida"] = acao
    state["justificativa"] = justificativa

    if alerta:
        state["alertas_pendentes"].append(alerta)
        state["decisao_requerida"] = True
        state["proximo_agente"] = AgentType.COORDENADOR.value
    else:
        state["decisao_requerida"] = False
        state["proximo_agente"] = AgentType.CRONOGRAMA.value

    state["mensagens"].append({
        "agente": AgentType.MARGEM.value,
        "timestamp": datetime.now().isoformat(),
        "acao": acao.value,
        "margem": margem_liq,
        "justificativa": justificativa
    })

    state["iteracao"] += 1
    return state

def agente_risco(state: HydrosolState) -> HydrosolState:
    """
    Agente de Risco: Avalia riscos ativos e impacto financeiro.
    """
    print(f"\n🤖 [AGENTE RISCO] Avaliando riscos de {state['projeto_nome']}...")

    riscos = state.get("riscos_ativos", [])

    if not riscos:
        state["nivel_risco"] = AlertLevel.INFO
        state["proximo_agente"] = AgentType.NOTA_FISCAL.value
        state["mensagens"].append({
            "agente": AgentType.RISCO.value,
            "timestamp": datetime.now().isoformat(),
            "acao": "sem_riscos",
            "justificativa": "Nenhum risco ativo identificado."
        })
        return state

    # Avaliar risco mais critico
    risco_critico = max(riscos, key=lambda r: r.get("impacto", 0) * r.get("probabilidade", 0))

    resultado = avaliar_risco.invoke({
        "nivel_risco": risco_critico.get("tipo", "medio"),
        "impacto_financeiro": risco_critico.get("impacto", 0),
        "probabilidade": risco_critico.get("probabilidade", 0.5)
    })

    state["nivel_risco"] = AlertLevel(resultado["nivel"])

    if resultado["requer_aprovacao"]:
        alerta = {
            "nivel": resultado["nivel"],
            "agente": AgentType.RISCO.value,
            "mensagem": f"🔴 RISCO {resultado['nivel'].upper()}: {risco_critico.get('descricao', 'Risco nao especificado')}",
            "score": resultado["score_risco"],
            "acoes": resultado["acoes_recomendadas"]
        }
        state["alertas_pendentes"].append(alerta)
        state["decisao_requerida"] = True
        state["acao_sugerida"] = TipoAcao.ALERTAR
        state["justificativa"] = f"Risco score {resultado['score_risco']} requer atencao imediata."
        state["proximo_agente"] = AgentType.COORDENADOR.value
    else:
        state["decisao_requerida"] = False
        state["proximo_agente"] = AgentType.NOTA_FISCAL.value

    state["mensagens"].append({
        "agente": AgentType.RISCO.value,
        "timestamp": datetime.now().isoformat(),
        "score": resultado["score_risco"],
        "nivel": resultado["nivel"],
        "acoes": resultado["acoes_recomendadas"]
    })

    state["iteracao"] += 1
    return state

def agente_cronograma(state: HydrosolState) -> HydrosolState:
    """
    Agente de Cronograma: Verifica prazos e progresso.
    """
    print(f"\n🤖 [AGENTE CRONOGRAMA] Verificando prazos de {state['projeto_nome']}...")

    # Simular dados de cronograma (em producao viriam do Notion/ERP)
    data_inicio = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    data_fim = (datetime.now() + timedelta(days=360)).strftime("%Y-%m-%d")
    progresso = 35.0  # 35% concluido

    resultado = verificar_cronograma.invoke({
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "progresso_pct": progresso
    })

    state["dias_atraso"] = resultado["dias_atraso"]

    if resultado["dias_atraso"] > 0:
        alerta = {
            "nivel": AlertLevel.WARNING.value if resultado["dias_atraso"] < 30 else AlertLevel.CRITICAL.value,
            "agente": AgentType.CRONOGRAMA.value,
            "mensagem": f"⏱️ ATRASO: {state['projeto_nome']} - {resultado['dias_atraso']} dias",
            "desvio": resultado["desvio_pct"]
        }
        state["alertas_pendentes"].append(alerta)
        state["acao_sugerida"] = TipoAcao.REVISAR
        state["justificativa"] = f"Projeto atrasado {resultado['dias_atraso']} dias. Desvio de {resultado['desvio_pct']}% do cronograma."

    state["proximo_agente"] = AgentType.RISCO.value
    state["iteracao"] += 1

    state["mensagens"].append({
        "agente": AgentType.CRONOGRAMA.value,
        "timestamp": datetime.now().isoformat(),
        "status": resultado["status"],
        "dias_atraso": resultado["dias_atraso"]
    })

    return state

def agente_nota_fiscal(state: HydrosolState) -> HydrosolState:
    """
    Agente de Nota Fiscal: Valida NFs pendentes e decide fluxo de aprovacao.
    """
    print(f"\n🤖 [AGENTE NF] Processando notas fiscais de {state['projeto_nome']}...")

    nfs = state.get("nfs_pendentes", [])

    if not nfs:
        state["proximo_agente"] = END
        state["mensagens"].append({
            "agente": AgentType.NOTA_FISCAL.value,
            "timestamp": datetime.now().isoformat(),
            "acao": "sem_nf",
            "justificativa": "Nenhuma NF pendente."
        })
        return state

    nf = nfs[0]  # Processar primeira NF da fila
    state["nf_atual"] = nf

    resultado = validar_nota_fiscal.invoke({
        "numero_nf": nf.get("numero", "000"),
        "valor": nf.get("valor", 0.0),
        "cnpj_fornecedor": nf.get("cnpj", ""),
        "projeto_id": state["projeto_id"]
    })

    if resultado["pode_automatizar"]:
        # NF ate 100k: aprovacao automatica
        acao = TipoAcao.AUTOMATIZAR
        justificativa = f"NF {resultado['numero_nf']} de R$ {resultado['valor']:,.2f} aprovada automaticamente (abaixo de R$ 100k)."

        # Notificar via WhatsApp
        enviar_whatsapp.invoke({
            "numero": "+5511999999999",  # Numero do coordenador
            "mensagem": f"✅ NF AUTOMATICA APROVADA\nProjeto: {state['projeto_nome']}\nNF: {resultado['numero_nf']}\nValor: R$ {resultado['valor']:,.2f}\nStatus: Aprovada automaticamente",
            "tipo": "nf_aprovada"
        })

    elif resultado["requer_aprovacao_coordenador"]:
        acao = TipoAcao.REVISAR
        justificativa = f"NF {resultado['numero_nf']} de R$ {resultado['valor']:,.2f} requer aprovacao do coordenador (acima de 50% do limite)."

        # Alertar coordenador
        enviar_whatsapp.invoke({
            "numero": "+5511999999999",
            "mensagem": f"⚠️ NF PENDENTE DE APROVACAO\nProjeto: {state['projeto_nome']}\nNF: {resultado['numero_nf']}\nValor: R$ {resultado['valor']:,.2f}\nLimite: R$ {resultado['limite_projeto']:,.2f}\nAcesse o dashboard para aprovar.",
            "tipo": "nf_pendente"
        })

        state["decisao_requerida"] = True
        state["proximo_agente"] = AgentType.COORDENADOR.value
    else:
        acao = TipoAcao.APROVAR
        justificativa = f"NF {resultado['numero_nf']} aprovada dentro dos limites."

    state["acao_sugerida"] = acao
    state["justificativa"] = justificativa

    state["mensagens"].append({
        "agente": AgentType.NOTA_FISCAL.value,
        "timestamp": datetime.now().isoformat(),
        "nf": resultado["numero_nf"],
        "valor": resultado["valor"],
        "acao": acao.value,
        "status": resultado["status"]
    })

    state["iteracao"] += 1
    return state

def agente_coordenador(state: HydrosolState) -> HydrosolState:
    """
    Agente Coordenador (Humano no Loop): Recebe alertas e decide acoes.
    Este agente representa o ponto de intervencao humana no fluxo.
    """
    print(f"\n👤 [AGENTE COORDENADOR] Decisao requerida para {state['projeto_nome']}...")

    alertas = state.get("alertas_pendentes", [])

    if not alertas:
        state["proximo_agente"] = END
        return state

    # Consolidar alertas em uma mensagem
    alertas_texto = "\\n".join([f"- [{a['nivel'].upper()}] {a['mensagem']}" for a in alertas])

    mensagem_coordenador = f"""
🌊 HYDROSOL AI - DECISAO REQUERIDA

Projeto: {state['projeto_nome']}
Etapa: {state['etapa_atual']}/13

ALERTAS PENDENTES:
{alertas_texto}

ACAO SUGERIDA: {state.get('acao_sugerida', 'Nenhuma').value}
JUSTIFICATIVA: {state.get('justificativa', 'N/A')}

Acesse o dashboard para tomar decisao.
"""

    # Enviar para coordenador via WhatsApp
    enviar_whatsapp.invoke({
        "numero": "+5511999999999",
        "mensagem": mensagem_coordenador,
        "tipo": "decisao_coordenador"
    })

    # Registrar no Notion
    enviar_notion.invoke({
        "database_id": os.getenv("NOTION_DB_ALERTAS", ""),
        "dados": {
            "Projeto": {"title": [{"text": {"content": state["projeto_nome"]}}]},
            "Status": {"select": {"name": "Pendente"}},
            "Prioridade": {"select": {"name": alertas[0]["nivel"]}},
            "Descricao": {"rich_text": [{"text": {"content": alertas[0]["mensagem"]}}]},
            "Data": {"date": {"start": datetime.now().isoformat()}}
        }
    })

    state["decisao_requerida"] = True
    state["proximo_agente"] = END  # Aguarda intervencao humana

    state["mensagens"].append({
        "agente": AgentType.COORDENADOR.value,
        "timestamp": datetime.now().isoformat(),
        "acao": "aguardando_decisao",
        "alertas_count": len(alertas)
    })

    state["iteracao"] += 1
    return state

# ==============================================================================
# CONDICIONAIS DE ROTEAMENTO
# ==============================================================================

def router(state: HydrosolState) -> str:
    """Roteia para o proximo agente baseado no estado atual."""

    # Limite de iteracoes
    if state["iteracao"] >= state["max_iteracoes"]:
        print("\n⛔ Limite de iteracoes atingido. Encerrando grafo.")
        return END

    # Se decisao requerida, vai para coordenador
    if state.get("decisao_requerida", False):
        return AgentType.COORDENADOR.value

    # Proximo agente definido pelo estado
    proximo = state.get("proximo_agente", END)

    if proximo == END or proximo is None:
        return END

    return proximo

# ==============================================================================
# CONSTRUCAO DO GRAFO LANGGRAPH
# ==============================================================================

def construir_grafo() -> StateGraph:
    """Constroi e retorna o grafo de agentes Hydrosol."""

    # Criar grafo
    workflow = StateGraph(HydrosolState)

    # Adicionar nodes (agentes)
    workflow.add_node(AgentType.MARGEM.value, agente_margem)
    workflow.add_node(AgentType.RISCO.value, agente_risco)
    workflow.add_node(AgentType.CRONOGRAMA.value, agente_cronograma)
    workflow.add_node(AgentType.NOTA_FISCAL.value, agente_nota_fiscal)
    workflow.add_node(AgentType.COORDENADOR.value, agente_coordenador)

    # Definir entry point
    workflow.set_entry_point(AgentType.CRONOGRAMA.value)

    # Adicionar edges condicionais
    workflow.add_conditional_edges(
        AgentType.CRONOGRAMA.value,
        router,
        {
            AgentType.RISCO.value: AgentType.RISCO.value,
            AgentType.COORDENADOR.value: AgentType.COORDENADOR.value,
            END: END
        }
    )

    workflow.add_conditional_edges(
        AgentType.RISCO.value,
        router,
        {
            AgentType.NOTA_FISCAL.value: AgentType.NOTA_FISCAL.value,
            AgentType.COORDENADOR.value: AgentType.COORDENADOR.value,
            END: END
        }
    )

    workflow.add_conditional_edges(
        AgentType.NOTA_FISCAL.value,
        router,
        {
            AgentType.COORDENADOR.value: AgentType.COORDENADOR.value,
            END: END
        }
    )

    workflow.add_conditional_edges(
        AgentType.MARGEM.value,
        router,
        {
            AgentType.CRONOGRAMA.value: AgentType.CRONOGRAMA.value,
            AgentType.COORDENADOR.value: AgentType.COORDENADOR.value,
            END: END
        }
    )

    workflow.add_conditional_edges(
        AgentType.COORDENADOR.value,
        router,
        {END: END}
    )

    return workflow.compile()

# ==============================================================================
# EXECUCAO
# ==============================================================================

def criar_estado_inicial(
    projeto_id: str = "ETE-001",
    projeto_nome: str = "ETE Onda Limpa #01",
    vazao_ls: float = 20.0,
    grupo: str = "Serie",
    custo_real: float = 8_500_000.0,
    custo_orcado: float = 7_600_000.0,
    riscos: List[Dict] = None,
    nfs: List[Dict] = None
) -> HydrosolState:
    """Cria estado inicial para execucao do grafo."""
    return {
        "projeto_id": projeto_id,
        "projeto_nome": projeto_nome,
        "vazao_ls": vazao_ls,
        "grupo": grupo,
        "etapa_atual": 3,
        "custo_real": custo_real,
        "custo_orcado": custo_orcado,
        "margem_atual": 0.0,
        "margem_alvo": 28.0,
        "prazo_atual": None,
        "prazo_alvo": None,
        "dias_atraso": 0,
        "nfs_pendentes": nfs or [{"numero": "NF-2026-001", "valor": 75_000.0, "cnpj": "12.345.678/0001-90"}],
        "nf_atual": None,
        "riscos_ativos": riscos or [{"tipo": "atraso_fornecedor", "impacto": 500_000.0, "probabilidade": 0.6, "descricao": "Atraso na entrega de equipamentos eletromecanicos"}],
        "nivel_risco": AlertLevel.INFO,
        "mensagens": [],
        "alertas_pendentes": [],
        "decisao_requerida": False,
        "acao_sugerida": None,
        "justificativa": "",
        "proximo_agente": AgentType.CRONOGRAMA.value,
        "iteracao": 0,
        "max_iteracoes": 10
    }


if __name__ == "__main__":
    print("=" * 80)
    print("HYDROSOL AI - AGENTES LANGGRAPH v5.1")
    print("Orquestracao de Agentes Autonomos")
    print("=" * 80)

    # Criar grafo
    grafo = construir_grafo()

    # Estado inicial
    estado = criar_estado_inicial()

    print(f"\n🚀 Iniciando fluxo para: {estado['projeto_nome']}")
    print(f"   Vazao: {estado['vazao_ls']} L/s | Grupo: {estado['grupo']}")
    print(f"   Custo Real: R$ {estado['custo_real']:,.2f} | Orcado: R$ {estado['custo_orcado']:,.2f}")

    # Executar grafo
    resultado_final = grafo.invoke(estado)

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DA EXECUCAO")
    print("=" * 80)

    print(f"\n📊 Iteracoes: {resultado_final['iteracao']}")
    print(f"🎯 Decisao requerida: {'Sim' if resultado_final['decisao_requerida'] else 'Nao'}")
    print(f"💰 Margem atual: {resultado_final['margem_atual']:.1f}%")
    print(f"⚠️  Nivel de risco: {resultado_final['nivel_risco'].value}")
    print(f"📋 Alertas pendentes: {len(resultado_final['alertas_pendentes'])}")

    print(f"\n📨 Mensagens trocadas ({len(resultado_final['mensagens'])}):")
    for msg in resultado_final['mensagens']:
        print(f"   [{msg['agente']}] {msg.get('acao', 'N/A')} - {msg.get('justificativa', '')[:60]}...")

    if resultado_final['alertas_pendentes']:
        print(f"\n🚨 ALERTAS:")
        for alerta in resultado_final['alertas_pendentes']:
            print(f"   [{alerta['nivel'].upper()}] {alerta['mensagem']}")

    print("\n" + "=" * 80)
    print("FLUXO CONCLUIDO")
    print("=" * 80)
