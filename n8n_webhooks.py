"""
================================================================================
HYDROSOL AI - WEBHOOKS N8N v5.1
Automacao de Notas Fiscais e Alertas WhatsApp
Programa Onda Limpa / Sabesp | R$ 1,23 Bi | 49 Unidades
================================================================================
Este arquivo contem os payloads JSON para configuracao nos workflows do n8n.
Copie cada secao para o node "Code" ou "Function" correspondente no n8n.
================================================================================
"""

# ==============================================================================
# WORKFLOW 1: RECEBIMENTO E VALIDACAO DE NOTA FISCAL
# ==============================================================================
"""
--- NOME DO WORKFLOW N8N: "Hydrosol - Recebimento NF" ---
TRIGGER: Webhook (POST /webhook/nf-recebida)
"""

WEBHOOK_NF_RECEBIDA = {
    "name": "Hydrosol - Recebimento NF",
    "nodes": [
        {
            "type": "n8n-nodes-base.webhook",
            "name": "Webhook NF Recebida",
            "webhookId": "nf-recebida",
            "httpMethod": "POST",
            "responseMode": "responseNode",
            "path": "nf-recebida"
        },
        {
            "type": "n8n-nodes-base.code",
            "name": "Validar NF",
            "jsCode": """
// ============================================
// NODE: Validar NF (JavaScript - n8n)
// ============================================
const nf = $input.first().json;

// Extrair dados da NF
const numeroNF = nf.numero || nf.numero_nf || "DESCONHECIDO";
const valor = parseFloat(nf.valor || nf.valor_total || 0);
const cnpj = nf.cnpj_fornecedor || nf.cnpj || "";
const projetoId = nf.projeto_id || nf.id_projeto || "GERAL";
const projetoNome = nf.projeto_nome || "Projeto nao identificado";
const dataEmissao = nf.data_emissao || new Date().toISOString();
const descricao = nf.descricao || nf.item || "Servico/Material";

// Limites por projeto (em producao, consultar database)
const LIMITES = {
    "ETE-SERIE": 500000,
    "ETE-MEDIO": 2000000,
    "ETE-MAGNUM": 10000000,
    "ETA": 5000000,
    "GERAL": 100000
};

const limite = LIMITES[projetoId] || LIMITES["GERAL"];
const percentualLimite = (valor / limite) * 100;

// Regras de validacao
let status = "PENDENTE";
let fluxo = "manual";  // manual | automatico | coordenador
let prioridade = "normal";

if (valor <= 100000) {
    // Ate 100k: aprovacao automatica
    status = "APROVADA_AUTO";
    fluxo = "automatico";
    prioridade = "baixa";
} else if (valor <= limite * 0.5) {
    // Ate 50% do limite: aprovacao do gestor
    status = "PENDENTE_GESTOR";
    fluxo = "manual";
    prioridade = "normal";
} else if (valor <= limite) {
    // Ate 100% do limite: aprovacao coordenador
    status = "PENDENTE_COORDENADOR";
    fluxo = "coordenador";
    prioridade = "alta";
} else {
    // Acima do limite: BLOQUEADA
    status = "BLOQUEADA";
    fluxo = "coordenador";
    prioridade = "critica";
}

// Verificar fornecedor na lista aprovada (simulacao)
const FORNECEDORES_APROVADOS = [
    "12.345.678/0001-90",
    "98.765.432/0001-10",
    "11.222.333/0001-44"
];
const fornecedorAprovado = FORNECEDORES_APROVADOS.includes(cnpj.replace(/[^0-9]/g, ""));

if (!fornecedorAprovado && status !== "BLOQUEADA") {
    status = "PENDENTE_CADASTRO";
    fluxo = "manual";
}

return [{
    json: {
        nf: {
            numero: numeroNF,
            valor: valor,
            cnpj: cnpj,
            projeto_id: projetoId,
            projeto_nome: projetoNome,
            data_emissao: dataEmissao,
            descricao: descricao
        },
        validacao: {
            status: status,
            fluxo: fluxo,
            prioridade: prioridade,
            limite_projeto: limite,
            percentual_limite: percentualLimite.toFixed(2),
            fornecedor_aprovado: fornecedorAprovado,
            timestamp_validacao: new Date().toISOString()
        }
    }
}];
"""
        },
        {
            "type": "n8n-nodes-base.switch",
            "name": "Roteamento por Fluxo",
            "rules": {
                "rules": [
                    {"value": "automatico", "output": 0},
                    {"value": "manual", "output": 1},
                    {"value": "coordenador", "output": 2}
                ]
            }
        },
        {
            "type": "n8n-nodes-base.httpRequest",
            "name": "Notificar WhatsApp - Aprovada",
            "method": "POST",
            "url": "http://localhost:5678/webhook/whatsapp",
            "body": {
                "numero": "{{$env.WHATSAPP_COORDENADOR}}",
                "mensagem": "✅ *NF APROVADA AUTOMATICAMENTE*\\n\\nProjeto: {{$json.nf.projeto_nome}}\\nNF: {{$json.nf.numero}}\\nValor: R$ {{$json.nf.valor.toLocaleString('pt-BR')}}\\nStatus: Aprovada\\nData: {{new Date().toLocaleString('pt-BR')}}",
                "tipo": "nf_aprovada_auto"
            }
        },
        {
            "type": "n8n-nodes-base.httpRequest",
            "name": "Notificar WhatsApp - Pendente",
            "method": "POST",
            "url": "http://localhost:5678/webhook/whatsapp",
            "body": {
                "numero": "{{$env.WHATSAPP_GESTOR}}",
                "mensagem": "📋 *NF PENDENTE DE APROVACAO*\\n\\nProjeto: {{$json.nf.projeto_nome}}\\nNF: {{$json.nf.numero}}\\nValor: R$ {{$json.nf.valor.toLocaleString('pt-BR')}}\\nLimite: {{$json.validacao.percentual_limite}}% do projeto\\nStatus: {{$json.validacao.status}}\\n\\nAcesse: https://hydrosol.ai/dashboard/nf",
                "tipo": "nf_pendente"
            }
        },
        {
            "type": "n8n-nodes-base.httpRequest",
            "name": "Alerta Coordenador - Critico",
            "method": "POST",
            "url": "http://localhost:5678/webhook/whatsapp",
            "body": {
                "numero": "{{$env.WHATSAPP_COORDENADOR}}",
                "mensagem": "🚨 *NF CRITICA - REQUER APROVACAO*\\n\\nProjeto: {{$json.nf.projeto_nome}}\\nNF: {{$json.nf.numero}}\\nValor: R$ {{$json.nf.valor.toLocaleString('pt-BR')}}\\n⚠️ ULTRAPASSA {{$json.validacao.percentual_limite}}% DO LIMITE DO PROJETO\\n\\n*ACAO REQUERIDA IMEDIATA*\\nDashboard: https://hydrosol.ai/dashboard",
                "tipo": "nf_critica"
            }
        },
        {
            "type": "n8n-nodes-base.notion",
            "name": "Registrar no Notion",
            "operation": "create",
            "databaseId": "{{$env.NOTION_DB_NF}}",
            "properties": {
                "Nome": "{{$json.nf.numero}}",
                "Projeto": "{{$json.nf.projeto_nome}}",
                "Valor": "{{$json.nf.valor}}",
                "Status": "{{$json.validacao.status}}",
                "Prioridade": "{{$json.validacao.prioridade}}",
                "Fornecedor": "{{$json.nf.cnpj}}",
                "Data Emissao": "{{$json.nf.data_emissao}}"
            }
        }
    ]
}


# ==============================================================================
# WORKFLOW 2: ALERTAS WHATSAPP AUTOMATIZADOS
# ==============================================================================
"""
--- NOME DO WORKFLOW N8N: "Hydrosol - Alertas WhatsApp" ---
TRIGGER: Webhook (POST /webhook/whatsapp)
"""

WEBHOOK_WHATSAPP_ALERTAS = {
    "name": "Hydrosol - Alertas WhatsApp",
    "description": "Recebe alertas do LangGraph e envia mensagens WhatsApp Business",
    "nodes": [
        {
            "type": "n8n-nodes-base.webhook",
            "name": "Webhook Alertas",
            "webhookId": "whatsapp",
            "httpMethod": "POST",
            "responseMode": "onReceived",
            "path": "whatsapp"
        },
        {
            "type": "n8n-nodes-base.code",
            "name": "Formatar Mensagem",
            "jsCode": """
// ============================================
// NODE: Formatar Mensagem WhatsApp (n8n)
// ============================================
const payload = $input.first().json;

// Templates de mensagem por tipo
const TEMPLATES = {
    "nf_aprovada": (d) => `✅ *NF APROVADA*\\n\\nProjeto: ${d.projeto}\\nNF: ${d.nf}\\nValor: R$ ${d.valor.toLocaleString('pt-BR')}\\nData: ${new Date().toLocaleString('pt-BR')}`,

    "nf_pendente": (d) => `⚠️ *NF PENDENTE*\\n\\nProjeto: ${d.projeto}\\nNF: ${d.nf}\\nValor: R$ ${d.valor.toLocaleString('pt-BR')}\\nStatus: Aguardando aprovacao\\n\\nAcesse: https://hydrosol.ai/dashboard`,

    "nf_critica": (d) => `🚨 *NF CRITICA*\\n\\nProjeto: ${d.projeto}\\nNF: ${d.nf}\\nValor: R$ ${d.valor.toLocaleString('pt-BR')}\\n⚠️ ULTRAPASSA LIMITE DO PROJETO\\n\\n*ACAO IMEDIATA NECESSARIA*`,

    "margem_alerta": (d) => `📊 *ALERTA DE MARGEM*\\n\\nProjeto: ${d.projeto}\\nMargem Atual: ${d.margem}%\\nTarget: 28-31%\\nStatus: ${d.status}\\n\\nRecomendacao: ${d.recomendacao}`,

    "margem_critica": (d) => `🚨 *MARGEM CRITICA*\\n\\nProjeto: ${d.projeto}\\nMargem Atual: ${d.margem}%\\n⚠️ ABAIXO DO MINIMO ACEITAVEL (20%)\\n\\n*ACAO URGENTE:*\\n${d.acoes.join('\\n')}\\n\\nDashboard: https://hydrosol.ai/dashboard`,

    "risco_alerta": (d) => `⚠️ *ALERTA DE RISCO*\\n\\nProjeto: ${d.projeto}\\nRisco: ${d.descricao}\\nScore: ${d.score}\\nNivel: ${d.nivel}\\n\\nAcoes: ${d.acoes.join('\\n')}`,

    "cronograma_atraso": (d) => `⏱️ *ATRASO NO CRONOGRAMA*\\n\\nProjeto: ${d.projeto}\\nDias de atraso: ${d.dias_atraso}\\nDesvio: ${d.desvio}%\\n\\nAcoes sugeridas: ${d.acoes}`,

    "decisao_coordenador": (d) => `👤 *DECISAO REQUERIDA*\\n\\nProjeto: ${d.projeto}\\nEtapa: ${d.etapa}/13\\n\\nALERTAS:\\n${d.alertas}\\n\\nACAO SUGERIDA: ${d.acao}\\n\\nAcesse o dashboard para decidir.`,

    "boletim_diario": (d) => `🌊 *BOLETIM DIARIO - HYDROSOL AI*\\n\\nData: ${new Date().toLocaleDateString('pt-BR')}\\n\\n📊 Resumo do dia:\\n- Projetos monitorados: ${d.total_projetos}\\n- Alertas: ${d.alertas}\\n- NFs processadas: ${d.nfs}\\n- Margem media: ${d.margem_media}%\\n\\nDashboard: https://hydrosol.ai/dashboard`
};

const tipo = payload.tipo || "generico";
const template = TEMPLATES[tipo] || ((d) => `🌊 *HYDROSOL AI*\\n\\n${JSON.stringify(d, null, 2)}`);

const mensagemFormatada = template(payload);

return [{
    json: {
        numero: payload.numero || $env.WHATSAPP_COORDENADOR,
        mensagem: mensagemFormatada,
        tipo: tipo,
        timestamp: new Date().toISOString(),
        origem: payload.origem || "n8n-webhook"
    }
}];
"""
        },
        {
            "type": "n8n-nodes-base.whatsappBusiness",
            "name": "Enviar WhatsApp",
            "operation": "sendTemplate",
            "phoneNumberId": "{{$env.WHATSAPP_PHONE_ID}}",
            "template": "hydrosol_alerta_generico",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "{{$json.mensagem}}"}
                    ]
                }
            ]
        },
        {
            "type": "n8n-nodes-base.notion",
            "name": "Log no Notion",
            "operation": "create",
            "databaseId": "{{$env.NOTION_DB_LOGS}}",
            "properties": {
                "Tipo": "{{$json.tipo}}",
                "Destinatario": "{{$json.numero}}",
                "Mensagem": "{{$json.mensagem}}",
                "Status": "Enviado",
                "Data": "{{$json.timestamp}}"
            }
        }
    ]
}


# ==============================================================================
# WORKFLOW 3: MONITORAMENTO AUTOMATICO (CRON)
# ==============================================================================
"""
--- NOME DO WORKFLOW N8N: "Hydrosol - Monitoramento Automatico" ---
TRIGGER: Schedule (a cada 1 hora)
"""

WORKFLOW_MONITORAMENTO = {
    "name": "Hydrosol - Monitoramento Automatico",
    "trigger": {
        "type": "schedule",
        "interval": "1h"
    },
    "nodes": [
        {
            "type": "n8n-nodes-base.code",
            "name": "Verificar Projetos",
            "jsCode": """
// ============================================
// NODE: Verificar Projetos (n8n - Cron Job)
// ============================================
// Em producao, consultar database/Notion/API
const PROJETOS = [
    {id: "ETE-001", nome: "ETE Onda Limpa #01", vazao: 20, grupo: "Serie", custo_real: 8500000, custo_orcado: 7600000, progresso: 35, dias_atraso: 0},
    {id: "ETE-002", nome: "ETE Onda Limpa #02", vazao: 20, grupo: "Serie", custo_real: 3200000, custo_orcado: 3800000, progresso: 15, dias_atraso: 5},
    {id: "ETE-028", nome: "ETE Onda Limpa #28", vazao: 100, grupo: "Medio", custo_real: 52000000, custo_orcado: 48000000, progresso: 60, dias_atraso: 12},
    {id: "ETA-045", nome: "ETA Onda Limpa #45", vazao: 500, grupo: "Magnum", custo_real: 380000000, custo_orcado: 350000000, progresso: 25, dias_atraso: 0}
];

const alertas = [];

for (const projeto of PROJETOS) {
    // Calcular margem
    const receita = projeto.custo_orcado * 1.35;
    const margemBruta = receita - projeto.custo_real;
    const margemLiquida = (margemBruta / receita) * 100 * 0.85;

    // Verificar margem
    if (margemLiquida < 20) {
        alertas.push({
            tipo: "margem_critica",
            projeto: projeto.nome,
            margem: margemLiquida.toFixed(1),
            status: "CRITICO",
            acoes: ["Revisar custos imediatamente", "Convocar reuniao de emergencia", "Bloquear novos gastos"],
            prioridade: "critica"
        });
    } else if (margemLiquida < 28) {
        alertas.push({
            tipo: "margem_alerta",
            projeto: projeto.nome,
            margem: margemLiquida.toFixed(1),
            status: "ATENCAO",
            recomendacao: "Revisar contratos e negociar com fornecedores",
            prioridade: "alta"
        });
    }

    // Verificar cronograma
    if (projeto.dias_atraso > 15) {
        alertas.push({
            tipo: "cronograma_atraso",
            projeto: projeto.nome,
            dias_atraso: projeto.dias_atraso,
            desvio: ((projeto.dias_atraso / 540) * 100).toFixed(1),
            acoes: "Acelerar producao e realocar equipe",
            prioridade: projeto.dias_atraso > 30 ? "critica" : "alta"
        });
    }
}

return [{
    json: {
        timestamp: new Date().toISOString(),
        total_projetos: PROJETOS.length,
        alertas_gerados: alertas.length,
        alertas: alertas,
        margem_media: (PROJETOS.reduce((a, p) => {
            const r = p.custo_orcado * 1.35;
            return a + (((r - p.custo_real) / r) * 100 * 0.85);
        }, 0) / PROJETOS.length).toFixed(1)
    }
}];
"""
        },
        {
            "type": "n8n-nodes-base.switch",
            "name": "Tem Alertas?",
            "rules": {
                "rules": [
                    {"value": 0, "output": 0, "condition": "equal"},
                    {"value": 1, "output": 1, "condition": "gte"}
                ]
            }
        },
        {
            "type": "n8n-nodes-base.splitInBatches",
            "name": "Processar Alertas",
            "batchSize": 1
        },
        {
            "type": "n8n-nodes-base.httpRequest",
            "name": "Enviar Alerta WhatsApp",
            "method": "POST",
            "url": "http://localhost:5678/webhook/whatsapp",
            "body": {
                "numero": "{{$env.WHATSAPP_COORDENADOR}}",
                "tipo": "{{$json.alertas[0].tipo}}",
                "projeto": "{{$json.alertas[0].projeto}}",
                "margem": "{{$json.alertas[0].margem}}",
                "status": "{{$json.alertas[0].status}}",
                "dias_atraso": "{{$json.alertas[0].dias_atraso}}",
                "desvio": "{{$json.alertas[0].desvio}}",
                "acoes": "{{$json.alertas[0].acoes}}",
                "recomendacao": "{{$json.alertas[0].recomendacao}}",
                "origem": "monitoramento_automatico"
            }
        },
        {
            "type": "n8n-nodes-base.notion",
            "name": "Registrar Alerta",
            "operation": "create",
            "databaseId": "{{$env.NOTION_DB_ALERTAS}}",
            "properties": {
                "Projeto": "{{$json.alertas[0].projeto}}",
                "Tipo": "{{$json.alertas[0].tipo}}",
                "Prioridade": "{{$json.alertas[0].prioridade}}",
                "Descricao": "{{JSON.stringify($json.alertas[0])}}",
                "Status": "Pendente",
                "Data": "{{new Date().toISOString()}}"
            }
        }
    ]
}


# ==============================================================================
# WORKFLOW 4: BOLETIM DIARIO (CRON - 08:00)
# ==============================================================================
"""
--- NOME DO WORKFLOW N8N: "Hydrosol - Boletim Diario" ---
TRIGGER: Schedule (todos os dias 08:00)
"""

WORKFLOW_BOLETIM_DIARIO = {
    "name": "Hydrosol - Boletim Diario",
    "trigger": {
        "type": "schedule",
        "cron": "0 8 * * *"
    },
    "nodes": [
        {
            "type": "n8n-nodes-base.code",
            "name": "Gerar Boletim",
            "jsCode": """
// ============================================
// NODE: Gerar Boletim Diario (n8n)
// ============================================
const hoje = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

// Em producao, consultar APIs/Notion
const boletim = {
    data: hoje,
    total_projetos: 49,
    projetos_ativos: 32,
    projetos_concluidos: 8,
    projetos_atrasados: 5,
    alertas_24h: 3,
    nfs_processadas_24h: 12,
    margem_media: 26.8,
    faturamento_mes: 48500000,
    custo_mes: 35600000,
    destaques: [
        "ETE #28 - Atraso de 12 dias, acao corretiva em andamento",
        "ETA #45 - NF critica aguardando aprovacao do coordenador",
        "Grupo Serie - 3 novas unidades em fase de producao"
    ]
};

return [{
    json: boletim
}];
"""
        },
        {
            "type": "n8n-nodes-base.httpRequest",
            "name": "Enviar Boletim WhatsApp",
            "method": "POST",
            "url": "http://localhost:5678/webhook/whatsapp",
            "body": {
                "numero": "{{$env.WHATSAPP_COORDENADOR}}",
                "tipo": "boletim_diario",
                "total_projetos": "{{$json.total_projetos}}",
                "alertas": "{{$json.alertas_24h}}",
                "nfs": "{{$json.nfs_processadas_24h}}",
                "margem_media": "{{$json.margem_media}}",
                "origem": "boletim_diario"
            }
        },
        {
            "type": "n8n-nodes-base.emailSend",
            "name": "Enviar Email Executivo",
            "toEmail": "{{$env.EMAIL_DIRETORIA}}",
            "subject": "🌊 Boletim Diario Hydrosol AI - {{new Date().toLocaleDateString('pt-BR')}}",
            "html": """
<h2 style="color:#0066CC;">🌊 Hydrosol AI - Boletim Diario</h2>
<p><strong>Data:</strong> {{$json.data}}</p>
<hr>
<h3>📊 Resumo Executivo</h3>
<ul>
<li>Projetos ativos: <strong>{{$json.projetos_ativos}}/{{$json.total_projetos}}</strong></li>
<li>Projetos atrasados: <strong style="color:#FF4757;">{{$json.projetos_atrasados}}</strong></li>
<li>Alertas 24h: <strong>{{$json.alertas_24h}}</strong></li>
<li>NFs processadas: <strong>{{$json.nfs_processadas_24h}}</strong></li>
<li>Margem media: <strong>{{$json.margem_media}}%</strong></li>
</ul>
<h3>💰 Financeiro</h3>
<p>Faturamento mes: R$ {{$json.faturamento_mes.toLocaleString('pt-BR')}}</p>
<p>Custo mes: R$ {{$json.custo_mes.toLocaleString('pt-BR')}}</p>
<h3>📋 Destaques</h3>
<ul>
{{$json.destaques.map(d => `<li>${d}</li>`).join('')}}
</ul>
<p><a href="https://hydrosol.ai/dashboard" style="background:#0066CC;color:white;padding:10px 20px;text-decoration:none;border-radius:8px;">Acessar Dashboard</a></p>
"""
        }
    ]
}


# ==============================================================================
# WORKFLOW 5: INTEGRACAO LANGGRAPH → N8N
# ==============================================================================
"""
--- NOME DO WORKFLOW N8N: "Hydrosol - Receptor LangGraph" ---
TRIGGER: Webhook (POST /webhook/langgraph)
"""

WORKFLOW_RECEPTOR_LANGGRAPH = {
    "name": "Hydrosol - Receptor LangGraph",
    "nodes": [
        {
            "type": "n8n-nodes-base.webhook",
            "name": "Webhook LangGraph",
            "webhookId": "langgraph",
            "httpMethod": "POST",
            "path": "langgraph"
        },
        {
            "type": "n8n-nodes-base.code",
            "name": "Processar Decisao",
            "jsCode": """
// ============================================
// NODE: Processar Decisao do LangGraph (n8n)
// ============================================
const payload = $input.first().json;

const decisao = {
    projeto_id: payload.projeto_id,
    projeto_nome: payload.projeto_nome,
    agente_origem: payload.agente,
    acao_sugerida: payload.acao,
    justificativa: payload.justificativa,
    margem: payload.margem,
    alertas: payload.alertas || [],
    timestamp_recebido: new Date().toISOString()
};

// Determinar fluxo baseado na acao
let fluxo = "registrar";
if (decisao.acao_sugerida === "alertar" || decisao.acao_sugerida === "rejeitar") {
    fluxo = "alertar_coordenador";
} else if (decisao.acao_sugerida === "automatizar") {
    fluxo = "executar_auto";
} else if (decisao.acao_sugerida === "revisar") {
    fluxo = "revisar_manual";
}

return [{
    json: {
        ...decisao,
        fluxo: fluxo,
        processado: true
    }
}];
"""
        },
        {
            "type": "n8n-nodes-base.switch",
            "name": "Roteamento Decisao",
            "rules": {
                "rules": [
                    {"value": "alertar_coordenador", "output": 0},
                    {"value": "executar_auto", "output": 1},
                    {"value": "revisar_manual", "output": 2},
                    {"value": "registrar", "output": 3}
                ]
            }
        },
        {
            "type": "n8n-nodes-base.httpRequest",
            "name": "Alertar Coordenador",
            "method": "POST",
            "url": "http://localhost:5678/webhook/whatsapp",
            "body": {
                "numero": "{{$env.WHATSAPP_COORDENADOR}}",
                "tipo": "decisao_coordenador",
                "projeto": "{{$json.projeto_nome}}",
                "etapa": "{{$json.etapa_atual}}",
                "alertas": "{{JSON.stringify($json.alertas)}}",
                "acao": "{{$json.acao_sugerida}}",
                "origem": "langgraph"
            }
        },
        {
            "type": "n8n-nodes-base.code",
            "name": "Executar Automatico",
            "jsCode": """
// Executa acao automatica (ex: aprovar NF ate 100k)
return [{
    json: {
        status: "executado",
        acao: $input.first().json.acao_sugerida,
        projeto: $input.first().json.projeto_nome,
        timestamp: new Date().toISOString()
    }
}];
"""
        },
        {
            "type": "n8n-nodes-base.notion",
            "name": "Registrar no Notion",
            "operation": "create",
            "databaseId": "{{$env.NOTION_DB_DECISOES}}",
            "properties": {
                "Projeto": "{{$json.projeto_nome}}",
                "Agente": "{{$json.agente_origem}}",
                "Acao": "{{$json.acao_sugerida}}",
                "Justificativa": "{{$json.justificativa}}",
                "Status": "{{$json.fluxo}}",
                "Data": "{{$json.timestamp_recebido}}"
            }
        }
    ]
}


# ==============================================================================
# ENVIRONMENT VARIABLES NECESSARIAS
# ==============================================================================
"""
Adicione estas variaveis no n8n (Settings > External Storage > Environment):

NOTION_TOKEN=secret_xxxxxxxxxxxxxxxx
NOTION_DB_NF=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
NOTION_DB_ALERTAS=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
NOTION_DB_LOGS=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
NOTION_DB_DECISOES=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

WHATSAPP_PHONE_ID=123456789012345
WHATSAPP_COORDENADOR=+5511999999999
WHATSAPP_GESTOR=+5511888888888

EMAIL_DIRETORIA=diretoria@hydrosol.ai

N8N_WEBHOOK_BASE=http://localhost:5678/webhook
"""

# ==============================================================================
# EXECUCAO DE TESTE
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("HYDROSOL AI - WEBHOOKS N8N v5.1")
    print("Configuracao de Workflows para Automacao")
    print("=" * 80)

    print("\n📋 WORKFLOWS CONFIGURADOS:")
    print("   1. Recebimento NF (Webhook: POST /webhook/nf-recebida)")
    print("   2. Alertas WhatsApp (Webhook: POST /webhook/whatsapp)")
    print("   3. Monitoramento Automatico (Cron: a cada 1h)")
    print("   4. Boletim Diario (Cron: todos os dias 08:00)")
    print("   5. Receptor LangGraph (Webhook: POST /webhook/langgraph)")

    print("\n🔧 NODES PRINCIPAIS:")
    print("   - Webhook triggers")
    print("   - Code nodes (validacao JavaScript)")
    print("   - Switch nodes (roteamento condicional)")
    print("   - HTTP Request (chamadas entre workflows)")
    print("   - Notion (registro de dados)")
    print("   - WhatsApp Business (envio de mensagens)")
    print("   - Email Send (boletins executivos)")

    print("\n📤 EXEMPLO DE PAYLOAD PARA TESTE:")
    exemplo_nf = {
        "numero": "NF-2026-0042",
        "valor": 75000.00,
        "cnpj_fornecedor": "12.345.678/0001-90",
        "projeto_id": "ETE-SERIE",
        "projeto_nome": "ETE Onda Limpa #05",
        "data_emissao": "2026-05-07",
        "descricao": "Modulos eletromecanicos - Lote 3"
    }
    print(json.dumps(exemplo_nf, indent=2, ensure_ascii=False))

    print("\n📤 EXEMPLO DE PAYLOAD LANGGRAPH:")
    exemplo_langgraph = {
        "projeto_id": "ETE-001",
        "projeto_nome": "ETE Onda Limpa #01",
        "agente": "agente_margem",
        "acao": "alertar",
        "justificativa": "Margem liquida caiu para 19.5%",
        "margem": 19.5,
        "alertas": [
            {"nivel": "critical", "mensagem": "Margem abaixo do minimo aceitavel"}
        ],
        "etapa_atual": 6
    }
    print(json.dumps(exemplo_langgraph, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("CONFIGURACAO CONCLUIDA")
    print("=" * 80)
