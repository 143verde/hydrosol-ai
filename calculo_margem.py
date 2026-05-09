"""
================================================================================
HYDROSOL AI - MODULO: CALCULO PARAMETRICO DE MARGEM v5.1
Programa Onda Limpa / Sabesp | DNA ETE Camburi (57 L/s)
================================================================================
Baseado em: ETE Camburi como modelo de custos e engenharia
Fator de Escala: R$ 363.300/L/s para ETEs de 10 L/s
Premissa: Escalas menores = +37% custo/Ls, BDI 1.45, margem ~31%
Fatores de Ajuste: Distancia, Maresia, Complexidade, Urgencia
================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import math

# ==============================================================================
# ENUMS E CONSTANTES
# ==============================================================================

class FatorAjuste(Enum):
    DISTANCIA = "distancia"
    MARESIA = "maresia"
    COMPLEXIDADE = "complexidade"
    URGENCIA = "urgencia"

class NivelFator(Enum):
    BAIXO = 1.0
    MEDIO = 1.15
    ALTO = 1.35
    CRITICO = 1.60

class GrupoETE(Enum):
    SERIE = "Serie"           # 20 L/s - Padronizacao + Compra em Lote
    MEDIO = "Medio"           # 40-150 L/s - Replicacao DNA Camburi
    MAGNUM = "Magnum"         # 500-1000 L/s - Agentes de Risco
    ETA = "ETA"               # Variavel - Gestao de Alto Valor

# ==============================================================================
# DNA ETE CAMBURI - REFERENCIA BASE
# ==============================================================================

@dataclass
class DNACamburi:
    """
    DNA Tecnico da ETE Camburi (57 L/s)
    Referencia para todos os calculos parametricos do programa.
    """
    # Dados Basicos
    nome: str = "ETE Camburi"
    vazao_ls: float = 57.0
    vazao_m3d: float = 4924.8  # 57 * 86.4

    # Custos Reais (base)
    custo_total_rs: float = 15_800_000.0  # ~R$ 15,8M
    custo_por_ls: float = 277_192.98      # 15.8M / 57
    custo_por_m3d: float = 3_208.13       # 15.8M / 4924.8

    # Composicao de Custos (%)
    composicao: Dict[str, float] = field(default_factory=lambda: {
        "civil": 0.35,          # Obras civis
        "eletromecanico": 0.28, # Equipamentos eletromecanicos
        "instrumentacao": 0.12, # Instrumentacao e controle
        "eletrica": 0.10,       # Instalacoes eletricas
        "automacao": 0.08,      # Sistemas de automacao
        "terraplenagem": 0.05,  # Terraplenagem e preparo
        "imprevistos": 0.02     # Reserva tecnica
    })

    # Parametros Operacionais
    area_m2: float = 1_200.0
    potencia_instalada_kw: float = 85.0
    consumo_energia_kwh_m3: float = 0.45
    mao_de_obra_permanente: int = 4

    # BDI e Margem
    bdi_padrao: float = 1.35
    margem_liquida_padrao: float = 0.28  # 28%

    # Prazos (meses)
    prazo_projeto: int = 2
    prazo_fabricacao: int = 6
    prazo_instalacao: int = 8
    prazo_total: int = 18

# Instancia global do DNA
DNA_CAMBURI = DNACamburi()

# ==============================================================================
# FATORES DE AJUSTE PARAMETRICO
# ==============================================================================

@dataclass
class FatoresAjuste:
    """
    Fatores de ajuste multiplicadores para calculo parametrico.
    Cada fator representa uma variavel de risco/custo do projeto.
    """
    distancia: float = 1.0      # Logistica e transporte
    maresia: float = 1.0        # Corrosao e materiais especiais
    complexidade: float = 1.0   # Dificuldade tecnica/terreno
    urgencia: float = 1.0       # Prazo comprimido

    # Descricoes para UI
    descricoes: Dict[str, str] = field(default_factory=lambda: {
        "distancia": "Distancia do polo industrial (km)",
        "maresia": "Exposicao a ambiente maritimo/costero",
        "complexidade": "Dificuldade de acesso e terreno",
        "urgencia": "Prazo de entrega comprimido"
    })

    # Niveis disponiveis para cada fator
    niveis: Dict[str, Dict[str, Tuple[float, str]]] = field(default_factory=lambda: {
        "distancia": {
            "Baixo (< 50km)": (1.00, "Proximo ao polo industrial"),
            "Medio (50-150km)": (1.15, "Distancia moderada"),
            "Alto (150-300km)": (1.35, "Logistica complexa"),
            "Critico (> 300km)": (1.60, "Transporte especializado necessario")
        },
        "maresia": {
            "Baixo (Interior)": (1.00, "Sem exposicao a salinidade"),
            "Medio (Costa protegida)": (1.15, "Protecao parcial contra maresia"),
            "Alto (Litoral direto)": (1.35, "Exposicao direta, materiais especiais"),
            "Critico (Ambiente agressivo)": (1.60, "Corrosao severa, tratamentos especiais")
        },
        "complexidade": {
            "Baixo (Terreno plano)": (1.00, "Facil implantacao"),
            "Medio (Terreno irregular)": (1.15, "Preparo adicional necessario"),
            "Alto (Area restrita/urbana)": (1.35, "Restricoes de acesso e logistica"),
            "Critico (Terreno problematico)": (1.60, "Fundacoes especiais, desmonte")
        },
        "urgencia": {
            "Baixo (Prazo normal)": (1.00, "Cronograma padrao 18 meses"),
            "Medio (Prazo reduzido)": (1.15, "Aceleracao parcial do cronograma"),
            "Alto (Entrega rapida)": (1.35, "Turnos extras, recursos dedicados"),
            "Critico (Emergencia)": (1.60, "Mobilizacao maxima, custos premium")
        }
    })

    @property
    def fator_total(self) -> float:
        """Calcula o fator composto multiplicativo."""
        return self.distancia * self.maresia * self.complexidade * self.urgencia

    @property
    def fator_composto_percentual(self) -> float:
        """Retorna o impacto percentual total dos fatores."""
        return (self.fator_total - 1.0) * 100

    def to_dict(self) -> Dict:
        return {
            "distancia": self.distancia,
            "maresia": self.maresia,
            "complexidade": self.complexidade,
            "urgencia": self.urgencia,
            "fator_total": self.fator_total,
            "impacto_percentual": f"+{self.fator_composto_percentual:.1f}%"
        }

# ==============================================================================
# CALCULADOR PARAMETRICO DE MARGEM
# ==============================================================================

@dataclass
class ResultadoMargem:
    """
    Resultado completo do calculo parametrico de margem.
    """
    # Identificacao
    projeto_nome: str
    grupo: str
    vazao_ls: float

    # Custos
    custo_base_por_ls: float
    custo_ajustado_por_ls: float
    custo_total_base: float
    custo_total_ajustado: float

    # Fatores
    fatores: FatoresAjuste
    fator_escala: float

    # Preco e BDI
    preco_venda: float
    bdi_aplicado: float
    receita_bruta: float

    # Margens
    margem_bruta_rs: float
    margem_bruta_pct: float
    margem_liquida_rs: float
    margem_liquida_pct: float

    # Comparativos
    vs_dna_camburi_pct: float
    status_margem: str  # "Dentro do target", "Abaixo do target", "Acima do target"

    # Detalhamento
    detalhamento: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "projeto": self.projeto_nome,
            "grupo": self.grupo,
            "vazao_ls": self.vazao_ls,
            "custo_base_total": self.custo_total_base,
            "custo_ajustado_total": self.custo_total_ajustado,
            "fator_escala": self.fator_escala,
            "fatores_ajuste": self.fatores.to_dict(),
            "preco_venda": self.preco_venda,
            "bdi": self.bdi_aplicado,
            "margem_bruta_pct": self.margem_bruta_pct,
            "margem_liquida_pct": self.margem_liquida_pct,
            "status": self.status_margem,
            "vs_camburi": self.vs_dna_camburi_pct
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class CalculadorParametrico:
    """
    Motor de calculo parametrico de margem para o ecossistema Hydrosol.
    Baseado no DNA da ETE Camburi como referencia.
    """

    # Constantes de escala
    CUSTO_TARGET_10LS: float = 363_300.0  # R$/L/s para ETE de 10 L/s
    PREMIUM_ESCALA_MENOR: float = 0.37     # +37% para escalas menores
    BDI_SERIE: float = 1.45                # BDI para grupo Serie (margem ~31%)
    BDI_PADRAO: float = 1.35               # BDI padrao (margem ~28%)
    BDI_MAGNUM: float = 1.30               # BDI para grupo Magnum (volume)

    # Fatores de escala por grupo
    FATORES_ESCALA: Dict[str, float] = {
        "Serie": 1.37,      # 20 L/s - custo/Ls +37% vs Camburi
        "Medio": 1.00,      # 40-150 L/s - replica DNA Camburi
        "Magnum": 0.85,     # 500-1000 L/s - economia de escala
        "ETA": 1.10         # Variavel - leve premium
    }

    # BDI por grupo
    BDI_POR_GRUPO: Dict[str, float] = {
        "Serie": 1.45,
        "Medio": 1.35,
        "Magnum": 1.30,
        "ETA": 1.38
    }

    def __init__(self, dna: DNACamburi = None):
        self.dna = dna or DNA_CAMBURI

    def calcular_custo_base(self, vazao_ls: float, grupo: str) -> float:
        """
        Calcula o custo base por L/s considerando o fator de escala do grupo.

        Para ETEs de 10 L/s: usa custo target de R$ 363.300/L/s
        Para outros: aplica fator de escala sobre o DNA Camburi
        """
        if vazao_ls <= 10:
            # ETEs muito pequenas - usar custo target direto
            return self.CUSTO_TARGET_10LS

        fator_escala = self.FATORES_ESCALA.get(grupo, 1.0)
        custo_base = self.dna.custo_por_ls * fator_escala

        return custo_base

    def calcular(
        self,
        projeto_nome: str,
        vazao_ls: float,
        grupo: str = "Serie",
        fatores: FatoresAjuste = None,
        bdi_custom: float = None,
        custo_extra_rs: float = 0.0
    ) -> ResultadoMargem:
        """
        Executa o calculo parametrico completo de margem.

        Args:
            projeto_nome: Nome identificador do projeto
            vazao_ls: Vazao em L/s
            grupo: Grupo do portfolio (Serie/Medio/Magnum/ETA)
            fatores: Objeto FatoresAjuste (distancia, maresia, etc.)
            bdi_custom: BDI customizado (opcional)
            custo_extra_rs: Custos adicionais nao contemplados (R$)

        Returns:
            ResultadoMargem com todos os calculos
        """
        fatores = fatores or FatoresAjuste()

        # 1. Custo base por L/s
        custo_base_ls = self.calcular_custo_base(vazao_ls, grupo)

        # 2. Aplicar fatores de ajuste
        custo_ajustado_ls = custo_base_ls * fatores.fator_total

        # 3. Custos totais
        custo_total_base = custo_base_ls * vazao_ls
        custo_total_ajustado = custo_ajustado_ls * vazao_ls + custo_extra_rs

        # 4. BDI e Preco de venda
        bdi = bdi_custom or self.BDI_POR_GRUPO.get(grupo, self.BDI_PADRAO)
        preco_venda = custo_total_ajustado * bdi

        # 5. Margens
        margem_bruta_rs = preco_venda - custo_total_ajustado
        margem_bruta_pct = (margem_bruta_rs / preco_venda) * 100

        # Margem liquida estimada (descontando ~15% de impostos/admin)
        margem_liquida_rs = margem_bruta_rs * 0.85
        margem_liquida_pct = (margem_liquida_rs / preco_venda) * 100

        # 6. Comparativo com DNA Camburi
        custo_camburi_equivalente = self.dna.custo_por_ls * vazao_ls
        vs_camburi = ((custo_total_ajustado / custo_camburi_equivalente) - 1) * 100

        # 7. Status da margem
        if margem_liquida_pct >= 31:
            status = "Acima do target"
        elif margem_liquida_pct >= 28:
            status = "Dentro do target"
        elif margem_liquida_pct >= 20:
            status = "Abaixo do target - Atenção"
        else:
            status = "Critico - Revisar urgente"

        # 8. Detalhamento
        detalhamento = {
            "composicao_custos": self._calcular_composicao(custo_total_ajustado),
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
            projeto_nome=projeto_nome,
            grupo=grupo,
            vazao_ls=vazao_ls,
            custo_base_por_ls=custo_base_ls,
            custo_ajustado_por_ls=custo_ajustado_ls,
            custo_total_base=custo_total_base,
            custo_total_ajustado=custo_total_ajustado,
            fatores=fatores,
            fator_escala=self.FATORES_ESCALA.get(grupo, 1.0),
            preco_venda=preco_venda,
            bdi_aplicado=bdi,
            receita_bruta=preco_venda,
            margem_bruta_rs=margem_bruta_rs,
            margem_bruta_pct=margem_bruta_pct,
            margem_liquida_rs=margem_liquida_rs,
            margem_liquida_pct=margem_liquida_pct,
            vs_dna_camburi_pct=vs_camburi,
            status_margem=status,
            detalhamento=detalhamento
        )

    def _calcular_composicao(self, custo_total: float) -> Dict[str, float]:
        """Distribui o custo total segundo a composicao do DNA Camburi."""
        return {
            categoria: custo_total * percentual
            for categoria, percentual in self.dna.composicao.items()
        }

    def simular_cenario(
        self,
        projeto_nome: str,
        vazao_ls: float,
        grupo: str,
        cenarios: List[Dict]
    ) -> List[ResultadoMargem]:
        """
        Simula multiplos cenarios de fatores para um mesmo projeto.

        Args:
            cenarios: Lista de dicts com keys: distancia, maresia, complexidade, urgencia

        Returns:
            Lista de ResultadoMargem, um para cada cenario
        """
        resultados = []
        for i, cenario in enumerate(cenarios):
            fatores = FatoresAjuste(
                distancia=cenario.get("distancia", 1.0),
                maresia=cenario.get("maresia", 1.0),
                complexidade=cenario.get("complexidade", 1.0),
                urgencia=cenario.get("urgencia", 1.0)
            )
            resultado = self.calcular(
                projeto_nome=f"{projeto_nome} - Cenario {i+1}",
                vazao_ls=vazao_ls,
                grupo=grupo,
                fatores=fatores
            )
            resultados.append(resultado)
        return resultados

    def comparar_grupos(self, vazao_ls: float) -> Dict[str, ResultadoMargem]:
        """
        Compara o mesmo projeto em todos os grupos do portfolio.
        Util para analise de viabilidade por segmento.
        """
        resultados = {}
        for grupo in ["Serie", "Medio", "Magnum", "ETA"]:
            resultado = self.calcular(
                projeto_nome=f"Comparativo {grupo}",
                vazao_ls=vazao_ls,
                grupo=grupo
            )
            resultados[grupo] = resultado
        return resultados


# ==============================================================================
# FUNCOES DE EXPORTACAO E RELATORIO
# ==============================================================================

def gerar_relatorio_json(resultado: ResultadoMargem) -> str:
    """Gera relatorio JSON formatado do resultado."""
    return resultado.to_json(indent=2)


def gerar_relatorio_texto(resultado: ResultadoMargem) -> str:
    """Gera relatorio em texto legivel."""
    r = resultado
    f = r.fatores

    relatorio = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           HYDROSOL AI - RELATORIO PARAMETRICO DE MARGEM v5.1                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 PROJETO: {r.projeto_nome}
📦 GRUPO: {r.grupo} | VAZAO: {r.vazao_ls} L/s

──────────────────────────────────────────────────────────────────────────────
💰 CUSTOS
──────────────────────────────────────────────────────────────────────────────
  Custo base por L/s:        R$ {r.custo_base_por_ls:,.2f}
  Custo ajustado por L/s:    R$ {r.custo_ajustado_por_ls:,.2f}
  Custo total base:          R$ {r.custo_total_base:,.2f}
  Custo total ajustado:      R$ {r.custo_total_ajustado:,.2f}

──────────────────────────────────────────────────────────────────────────────
📊 FATORES DE AJUSTE
──────────────────────────────────────────────────────────────────────────────
  Distancia:     {f.distancia:.2f}x  |  Maresia:      {f.maresia:.2f}x
  Complexidade:  {f.complexidade:.2f}x  |  Urgencia:      {f.urgencia:.2f}x
  ─────────────────────────────────────────
  FATOR TOTAL:   {f.fator_total:.2f}x  (+{f.fator_composto_percentual:.1f}%)

──────────────────────────────────────────────────────────────────────────────
💵 PRECO E MARGEM
──────────────────────────────────────────────────────────────────────────────
  BDI aplicado:              {r.bdi_aplicado:.2f}x
  Preco de venda:            R$ {r.preco_venda:,.2f}

  Margem BRUTA:              R$ {r.margem_bruta_rs:,.2f}  ({r.margem_bruta_pct:.1f}%)
  Margem LIQUIDA:            R$ {r.margem_liquida_rs:,.2f}  ({r.margem_liquida_pct:.1f}%)

──────────────────────────────────────────────────────────────────────────────
🎯 ANALISE
──────────────────────────────────────────────────────────────────────────────
  Status: {r.status_margem}
  vs DNA Camburi: {r.vs_dna_camburi_pct:+.1f}%

═══════════════════════════════════════════════════════════════════════════════
"""
    return relatorio


def gerar_tabela_comparativa(resultados: List[ResultadoMargem]) -> str:
    """Gera tabela comparativa em formato markdown."""
    linhas = [
        "| Projeto | Vazao | Custo Total | Preco Venda | Margem Liquida | Status |",
        "|---------|-------|-------------|-------------|----------------|--------|"
    ]
    for r in resultados:
        linhas.append(
            f"| {r.projeto_nome} | {r.vazao_ls} L/s | "
            f"R$ {r.custo_total_ajustado/1e6:.2f}M | R$ {r.preco_venda/1e6:.2f}M | "
            f"{r.margem_liquida_pct:.1f}% | {r.status_margem} |"
        )
    return "\n".join(linhas)


# ==============================================================================
# EXEMPLOS DE USO / TESTES
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("HYDROSOL AI - CALCULADOR PARAMETRICO DE MARGEM v5.1")
    print("=" * 80)

    calc = CalculadorParametrico()

    # EXEMPLO 1: ETE de 10 L/s (custo target)
    print("\n" + "=" * 80)
    print("EXEMPLO 1: ETE de 10 L/s - Custo Target (R$ 363.300/L/s)")
    print("=" * 80)

    fatores_10ls = FatoresAjuste(
        distancia=1.15,      # Medio (50-150km)
        maresia=1.35,        # Alto (litoral direto)
        complexidade=1.15,   # Medio (terreno irregular)
        urgencia=1.00        # Baixo (prazo normal)
    )

    r1 = calc.calcular(
        projeto_nome="ETE Onda Limpa #01 - Grupo Serie",
        vazao_ls=10.0,
        grupo="Serie",
        fatores=fatores_10ls
    )
    print(gerar_relatorio_texto(r1))

    # EXEMPLO 2: ETE de 20 L/s (padrao grupo Serie)
    print("\n" + "=" * 80)
    print("EXEMPLO 2: ETE de 20 L/s - Grupo Serie (Padronizacao)")
    print("=" * 80)

    fatores_20ls = FatoresAjuste(
        distancia=1.00,      # Baixo (< 50km)
        maresia=1.15,        # Medio (costa protegida)
        complexidade=1.00,   # Baixo (terreno plano)
        urgencia=1.00        # Baixo (prazo normal)
    )

    r2 = calc.calcular(
        projeto_nome="ETE Onda Limpa #05 - Grupo Serie",
        vazao_ls=20.0,
        grupo="Serie",
        fatores=fatores_20ls
    )
    print(gerar_relatorio_texto(r2))

    # EXEMPLO 3: ETE de 100 L/s (grupo Medio - DNA Camburi)
    print("\n" + "=" * 80)
    print("EXEMPLO 3: ETE de 100 L/s - Grupo Medio (Replica DNA Camburi)")
    print("=" * 80)

    fatores_100ls = FatoresAjuste(
        distancia=1.35,      # Alto (150-300km)
        maresia=1.00,        # Baixo (interior)
        complexidade=1.15,   # Medio
        urgencia=1.15        # Medio (prazo reduzido)
    )

    r3 = calc.calcular(
        projeto_nome="ETE Onda Limpa #28 - Grupo Medio",
        vazao_ls=100.0,
        grupo="Medio",
        fatores=fatores_100ls
    )
    print(gerar_relatorio_texto(r3))

    # EXEMPLO 4: ETA de 500 L/s (grupo Magnum)
    print("\n" + "=" * 80)
    print("EXEMPLO 4: ETA de 500 L/s - Grupo Magnum (Alto Valor)")
    print("=" * 80)

    fatores_500ls = FatoresAjuste(
        distancia=1.60,      # Critico (> 300km)
        maresia=1.00,        # Baixo
        complexidade=1.35,   # Alto (area restrita)
        urgencia=1.35        # Alto (entrega rapida)
    )

    r4 = calc.calcular(
        projeto_nome="ETA Onda Limpa #45 - Grupo Magnum",
        vazao_ls=500.0,
        grupo="Magnum",
        fatores=fatores_500ls
    )
    print(gerar_relatorio_texto(r4))

    # EXEMPLO 5: Comparativo de cenarios
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Simulacao Multi-Cenario (ETE 20 L/s)")
    print("=" * 80)

    cenarios = [
        {"distancia": 1.0, "maresia": 1.0, "complexidade": 1.0, "urgencia": 1.0},   # Otimo
        {"distancia": 1.15, "maresia": 1.15, "complexidade": 1.15, "urgencia": 1.0}, # Moderado
        {"distancia": 1.35, "maresia": 1.35, "complexidade": 1.35, "urgencia": 1.35}, # Critico
    ]

    resultados_cenarios = calc.simular_cenario(
        projeto_nome="ETE Onda Limpa #10",
        vazao_ls=20.0,
        grupo="Serie",
        cenarios=cenarios
    )

    print("\n" + gerar_tabela_comparativa(resultados_cenarios))

    # EXEMPLO 6: Comparativo entre grupos
    print("\n" + "=" * 80)
    print("EXEMPLO 6: Comparativo entre Grupos (Vazao fixa: 100 L/s)")
    print("=" * 80)

    comparativo = calc.comparar_grupos(vazao_ls=100.0)
    resultados_comp = list(comparativo.values())
    print("\n" + gerar_tabela_comparativa(resultados_comp))

    print("\n" + "=" * 80)
    print("FIM DOS TESTES")
    print("=" * 80)
