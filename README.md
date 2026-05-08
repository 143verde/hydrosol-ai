# 🌊 Hydrosol AI Dashboard v5.1

**Programa Onda Limpa / Sabesp** | R$ 1,23 Bi | 49 Unidades

Sistema de gestao inteligente para ETEs/ETAs com orquestracao de agentes de IA,
automatizacao via n8n e calculo parametrico de margem baseado no DNA da ETE Camburi.

---

## 📁 Estrutura de Pastas

```
hydrosol-ai/
│
├── hydrosol/                          # Pacote Python principal
│   ├── __init__.py                    # Torna a pasta um pacote importavel
│   ├── calculo_margem.py              # Modulo de calculo parametrico
│   ├── agentes.py                     # Orquestracao LangGraph
│   ├── n8n_webhooks.py                # Configuracao webhooks n8n
│   └── dashboard.py                   # App Streamlit (interface)
│
├── data/                              # Dados locais (CSV, JSON)
│   └── projetos.json
│
├── assets/                            # Imagens, logos, CSS custom
│   └── logo_hydrosol.png
│
├── tests/                             # Testes unitarios
│   └── test_calculo_margem.py
│
├── .env                               # Variaveis de ambiente (NAO versionar)
├── .env.example                       # Template de variaveis
├── requirements.txt                   # Dependencias Python
├── README.md                          # Este arquivo
└── run_dashboard.sh                   # Script de execucao
```

---

## 🚀 Instalacao Rapida

### 1. Clone ou copie os arquivos

```bash
# Crie a pasta principal
mkdir hydrosol-ai
cd hydrosol-ai

# Crie a estrutura de pastas
mkdir -p hydrosol data assets tests
```

### 2. Coloque os arquivos nas pastas corretas

| Arquivo | Destino |
|---------|---------|
| `hydrosol_dashboard_v51_base.py` | → `hydrosol/dashboard.py` |
| `hydrosol_calculo_margem.py` | → `hydrosol/calculo_margem.py` |
| `hydrosol_agentes_langgraph.py` | → `hydrosol/agentes.py` |
| `hydrosol_n8n_webhooks.py` | → `hydrosol/n8n_webhooks.py` |
| `__init__.py` (gerado) | → `hydrosol/__init__.py` |
| `requirements.txt` (gerado) | → `requirements.txt` |
| `.env.example` (gerado) | → `.env.example` |

### 3. Crie o ambiente virtual (recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate
```

### 4. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 5. Configure as variaveis de ambiente

```bash
# Copie o template
cp .env.example .env

# Edite o arquivo .env com seus dados reais
# (token do Notion, IDs de databases, numeros WhatsApp, etc.)
```

### 6. Execute o dashboard

```bash
# Metodo 1: Direto
streamlit run hydrosol/dashboard.py

# Metodo 2: Via modulo Python
python -m streamlit run hydrosol/dashboard.py

# Metodo 3: Com variaveis de ambiente
python -c "from hydrosol.dashboard import main; main()"
```

Acesse: **http://localhost:8501**

---

## 📦 Dependencias

| Pacote | Versao | Funcao |
|--------|--------|--------|
| `streamlit` | >=1.35.0 | Interface web do dashboard |
| `streamlit-option-menu` | >=0.3.13 | Menu lateral estilizado |
| `plotly` | >=5.22.0 | Graficos interativos |
| `pandas` | >=2.2.0 | Manipulacao de dados |
| `numpy` | >=1.26.0 | Computacao numerica |
| `langgraph` | >=0.0.50 | Orquestracao de agentes |
| `langchain-core` | >=0.2.0 | Base para agentes |
| `requests` | >=2.31.0 | Chamadas HTTP (APIs) |
| `python-dotenv` | >=1.0.0 | Carregar .env |

---

## 🔗 Como os Modulos se Comunicam

```
hydrosol/
│
├── dashboard.py          # IMPORTA os outros 3 modulos
│   ├── from .calculo_margem import CalculadorParametrico, FatoresAjuste
│   ├── from .agentes import construir_grafo, criar_estado_inicial
│   └── from .n8n_webhooks import enviar_whatsapp, enviar_notion
│
├── calculo_margem.py     # Modulo independente (puro Python)
│   └── class CalculadorParametrico
│       └── calcular(), simular_cenario(), comparar_grupos()
│
├── agentes.py            # Depende de langgraph + langchain
│   └── def construir_grafo()
│       └── agente_margem, agente_risco, agente_cronograma...
│
└── n8n_webhooks.py       # Depende de requests
    └── Templates JSON para workflows n8n
```

### Exemplo de uso no dashboard.py:

```python
# No topo do arquivo dashboard.py
from hydrosol.calculo_margem import CalculadorParametrico, FatoresAjuste
from hydrosol.agentes import construir_grafo, criar_estado_inicial
from hydrosol.n8n_webhooks import enviar_whatsapp

# Na aba "Custos" (Etapa 6)
calc = CalculadorParametrico()
resultado = calc.calcular(
    projeto_nome="ETE #01",
    vazao_ls=20.0,
    grupo="Serie",
    fatores=FatoresAjuste(distancia=1.15, maresia=1.35)
)
st.write(f"Margem: {resultado.margem_liquida_pct}%")

# Na aba "Riscos" (Etapa 5)
grafo = construir_grafo()
estado = criar_estado_inicial(projeto_id="ETE-001")
resultado = grafo.invoke(estado)
```

---

## 🐛 Solucao de Problemas

### Erro: "No module named 'hydrosol'"

**Causa:** Python nao encontra o pacote `hydrosol`.

**Solucoes:**

```bash
# Opcao 1: Execute da pasta raiz (hydrosol-ai/)
cd hydrosol-ai
python -m streamlit run hydrosol/dashboard.py

# Opcao 2: Adicione ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run hydrosol/dashboard.py

# Opcao 3: Instale como pacote editavel
pip install -e .
# (requer setup.py ou pyproject.toml)
```

### Erro: "ModuleNotFoundError: No module named 'langgraph'"

```bash
# Instale as dependencias do agente
pip install langgraph langchain-core
```

### Erro: "Cannot import name 'option_menu'"

```bash
pip install streamlit-option-menu
```

---

## 📱 Configuracao do n8n

1. Instale o n8n:
   ```bash
   npm install n8n -g
   n8n start
   ```

2. Acesse: `http://localhost:5678`

3. Crie os workflows copiando os nodes do arquivo `hydrosol/n8n_webhooks.py`

4. Configure as variaveis de ambiente em **Settings > External Storage**

5. Ative os webhooks e teste com:
   ```bash
   curl -X POST http://localhost:5678/webhook/nf-recebida      -H "Content-Type: application/json"      -d '{"numero":"NF-001","valor":50000,"projeto_id":"ETE-SERIE"}'
   ```

---

## 📝 Licenca

Proprietario - Hydrosol AI Team
