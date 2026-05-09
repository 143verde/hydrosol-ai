"""
================================================================================
HYDROSOL AI - PACOTE PRINCIPAL v5.1
Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
================================================================================
Estrutura de modulos:
  - calculo_margem    : Calculo parametrico de margem (DNA Camburi)
  - agentes           : Orquestracao LangGraph
  - n8n_webhooks      : Configuracao de webhooks n8n
  - dashboard         : Interface Streamlit (app principal)
================================================================================
"""

__version__ = "5.1.0"
__author__ = "Hydrosol AI Team"

# Facilitar imports
from .calculo_margem import (
    CalculadorParametrico,
    FatoresAjuste,
    DNACamburi,
    ResultadoMargem,
    gerar_relatorio_texto,
    gerar_relatorio_json,
    gerar_tabela_comparativa
)

from .agentes import (
    construir_grafo,
    criar_estado_inicial,
    HydrosolState,
    AlertLevel,
    AgentType,
    TipoAcao
)

__all__ = [
    "CalculadorParametrico",
    "FatoresAjuste",
    "DNACamburi",
    "ResultadoMargem",
    "construir_grafo",
    "criar_estado_inicial",
    "HydrosolState",
    "AlertLevel",
    "AgentType",
    "TipoAcao"
]
