
# ============================================================
# FUNÇÃO PARA GERAR RELATÓRIO PDF - DASHBOARD COMERCIAL
# Adicionar no início do dashboard.py (após os imports)
# ============================================================

def gerar_relatorio_pipeline_pdf(dados_pipeline, periodo="Mensal"):
    """Gera relatório em HTML para impressão/PDF do Pipeline Comercial"""

    hoje = datetime.now().strftime("%d/%m/%Y")

    # Calcular métricas
    total_propostas = len(dados_pipeline)
    propostas_simulada = len([p for p in dados_pipeline if p.get('status') == 'Simulada'])
    propostas_enviada = len([p for p in dados_pipeline if p.get('status') == 'Enviada'])
    propostas_negociando = len([p for p in dados_pipeline if p.get('status') == 'Negociando'])
    propostas_efetivada = len([p for p in dados_pipeline if p.get('status') == 'Efetivada'])

    valor_total = sum([p.get('valor', 0) for p in dados_pipeline])
    margem_media = sum([p.get('margem', 0) for p in dados_pipeline]) / total_propostas if total_propostas > 0 else 0

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório Pipeline Comercial - Hydrosol</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            .header {{ text-align: center; border-bottom: 3px solid #1E3A5F; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #1E3A5F; margin: 0; font-size: 1.8rem; }}
            .header p {{ color: #666; margin: 5px 0; }}
            .kpi-container {{ display: flex; justify-content: space-between; margin: 30px 0; flex-wrap: wrap; }}
            .kpi-box {{ width: 18%; background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center; border-top: 4px solid; margin-bottom: 10px; }}
            .kpi-value {{ font-size: 1.8rem; font-weight: bold; color: #1E3A5F; }}
            .kpi-label {{ font-size: 0.8rem; color: #666; }}
            .status-simulada {{ border-color: #3498db; }}
            .status-enviada {{ border-color: #f1c40f; }}
            .status-negociando {{ border-color: #e67e22; }}
            .status-efetivada {{ border-color: #27ae60; }}
            .status-total {{ border-color: #667eea; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem; }}
            th {{ background: #1E3A5F; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            .valor {{ text-align: right; font-weight: bold; }}
            .margem-alta {{ color: #27ae60; }}
            .margem-media {{ color: #f39c12; }}
            .margem-baixa {{ color: #e74c3c; }}
            .footer {{ margin-top: 40px; text-align: center; color: #999; font-size: 0.8rem; border-top: 1px solid #ddd; padding-top: 20px; }}
            .section {{ margin: 25px 0; }}
            .section h2 {{ color: #1E3A5F; border-left: 4px solid #667eea; padding-left: 10px; font-size: 1.2rem; }}
            .alerta-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; border-radius: 4px; }}
            .alerta-vermelho {{ background: #f8d7da; border-left-color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Pipeline Comercial - Hydrosol AI</h1>
            <p>Relatório de Propostas e Negociações</p>
            <p><strong>Período:</strong> {periodo} | <strong>Data:</strong> {hoje} | <strong>Responsável:</strong> MC</p>
        </div>

        <div class="section">
            <h2>📈 KPIs do Pipeline</h2>
            <div class="kpi-container">
                <div class="kpi-box status-total">
                    <div class="kpi-value">{total_propostas}</div>
                    <div class="kpi-label">Total Propostas</div>
                </div>
                <div class="kpi-box status-simulada">
                    <div class="kpi-value">{propostas_simulada}</div>
                    <div class="kpi-label">Simuladas</div>
                </div>
                <div class="kpi-box status-enviada">
                    <div class="kpi-value">{propostas_enviada}</div>
                    <div class="kpi-label">Enviadas</div>
                </div>
                <div class="kpi-box status-negociando">
                    <div class="kpi-value">{propostas_negociando}</div>
                    <div class="kpi-label">Negociando</div>
                </div>
                <div class="kpi-box status-efetivada">
                    <div class="kpi-value">{propostas_efetivada}</div>
                    <div class="kpi-label">Efetivadas</div>
                </div>
            </div>
            <div class="kpi-container">
                <div class="kpi-box status-total" style="width: 48%;">
                    <div class="kpi-value">R$ {valor_total:,.0f}</div>
                    <div class="kpi-label">Valor Total Pipeline</div>
                </div>
                <div class="kpi-box status-total" style="width: 48%;">
                    <div class="kpi-value">{margem_media:.1f}%</div>
                    <div class="kpi-label">Margem Média</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📋 Propostas em Andamento</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Projeto</th>
                    <th>Consórcio</th>
                    <th>Status</th>
                    <th>Vazão</th>
                    <th>BDI</th>
                    <th>Margem</th>
                    <th>Valor (R$)</th>
                    <th>Custo (R$)</th>
                    <th>Envio</th>
                </tr>
    """

    for prop in dados_pipeline:
        margem_class = "margem-alta" if prop.get('margem', 0) >= 25 else "margem-media" if prop.get('margem', 0) >= 15 else "margem-baixa"
        html += f"""
                <tr>
                    <td>{prop.get('id', 'N/A')}</td>
                    <td>{prop.get('nome', 'N/A')}</td>
                    <td>{prop.get('consorcio', 'N/A')}</td>
                    <td>{prop.get('status', 'N/A')}</td>
                    <td>{prop.get('vazao', 'N/A')}</td>
                    <td>{prop.get('bdi', 'N/A')}</td>
                    <td class="{margem_class}">{prop.get('margem', 0):.1f}%</td>
                    <td class="valor">R$ {prop.get('valor', 0):,.0f}</td>
                    <td class="valor">R$ {prop.get('custo', 0):,.0f}</td>
                    <td>{prop.get('data_envio', 'N/A')}</td>
                </tr>
        """

    html += f"""
            </table>
        </div>

        <div class="section">
            <h2>⚠️ Alertas e Ações</h2>
            <div class="alerta-box">
                <strong>📊 Taxa de Conversão:</strong> {propostas_efetivada}/{total_propostas} propostas efetivadas ({(propostas_efetivada/total_propostas*100) if total_propostas > 0 else 0:.1f}%)
            </div>
            <div class="alerta-box alerta-vermelho">
                <strong>🔴 Atenção:</strong> {propostas_negociando} propostas em negociação precisam de follow-up!
            </div>
        </div>

        <div class="footer">
            <p>🌊 Hydrosol AI v5.1 - Sistema de Gestão de Portfólio</p>
            <p>Gerado em {hoje} | Relatório confidencial - Uso interno</p>
        </div>
    </body>
    </html>
    """

    return html