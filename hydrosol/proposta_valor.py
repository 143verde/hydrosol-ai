"""
💎 Proposta de Valor - Hydrosol AI v5.1
Apresentação para reuniões com empreiteiras e consórcios
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

def render_aba_proposta_valor():
    """Renderiza a aba Proposta de Valor no Dashboard Comercial"""

    # CSS Personalizado
    st.markdown("""
    <style>
        .proposta-header {
            font-size: 2.2rem;
            font-weight: 800;
            color: #1E3A5F;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .proposta-sub {
            font-size: 1.1rem;
            color: #4A6FA5;
            text-align: center;
            margin-bottom: 2rem;
        }
        .pilar-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 5px solid;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .pilar-1 { border-left-color: #3498db; }
        .pilar-2 { border-left-color: #27ae60; }
        .pilar-3 { border-left-color: #f39c12; }
        .metric-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 1.2rem;
            color: white;
            text-align: center;
        }
        .case-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-top: 4px solid #667eea;
        }
        .cta-box {
            background: linear-gradient(135deg, #1E3A5F 0%, #4A6FA5 100%);
            border-radius: 15px;
            padding: 2rem;
            color: white;
            text-align: center;
            margin-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    st.markdown('<div class="proposta-header">💎 Proposta de Valor Estratégica</div>', unsafe_allow_html=True)
    st.markdown('<div class="proposta-sub">Transformando Gestão de Portfólio em Saneamento</div>', unsafe_allow_html=True)

    # SEÇÃO 1: O PROBLEMA
    st.markdown("---")
    st.subheader("🎯 O Problema")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Sem ferramenta de gestão, empreiteiras enfrentam:**

        📊 **Gestão Descentralizada**
        - Dados espalhados em planilhas
        - Silos entre equipes
        - Decisões sem base em dados

        ⚠️ **Risco Regulatório**
        - Atrasos em entregas
        - Multas da Sabesp
        - Perda de credibilidade

        💸 **Retrabalho**
        - 15-20% do orçamento perdido
        - Refazer projetos
        - Custos não previstos
        """)

    with col2:
        # Gráfico de impacto
        fig = go.Figure()
        categorias = ['Retrabalho', 'Multas', 'Atrasos', 'Silos', 'Falta Dados']
        valores = [85, 70, 65, 90, 75]
        cores = ['#e74c3c', '#f39c12', '#f39c12', '#e74c3c', '#e74c3c']

        fig.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=cores,
            text=valores,
            textposition='outside',
            texttemplate='%{text}%'
        ))
        fig.update_layout(
            title="Impacto do Problema (% de perda)",
            yaxis_title="Severidade (%)",
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # SEÇÃO 2: OS 3 PILARES
    st.markdown("---")
    st.subheader("🏛️ Os 3 Pilares da Hydrosol")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown("""
        <div class="pilar-card pilar-1">
            <h3 style="color: #3498db;">🔬 Qualidade & Conformidade</h3>
            <ul>
                <li>IA monitora 24/7</li>
                <li>Detecção em 30 seg</li>
                <li>Engenheiros validam</li>
                <li>99%+ conformidade</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="pilar-card pilar-2">
            <h3 style="color: #27ae60;">💰 Segurança Financeira</h3>
            <ul>
                <li>BDI otimizado</li>
                <li>Margem protegida</li>
                <li>Custos controlados</li>
                <li>ROI previsível</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_p3:
        st.markdown("""
        <div class="pilar-card pilar-3">
            <h3 style="color: #f39c12;">📱 Digital & Transparência</h3>
            <ul>
                <li>Dashboard em tempo real</li>
                <li>Relatórios automáticos</li>
                <li>Acesso pelo celular</li>
                <li>Transparência total</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # SEÇÃO 3: MÉTRICAS ANTES/DEPOIS
    st.markdown("---")
    st.subheader("📊 Resultados Comprovados")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.markdown("""
        <div class="metric-box">
            <div style="font-size: 2rem; font-weight: bold;">2-5 dias</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">→ 30 seg</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">Tempo de resposta</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="metric-box" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div style="font-size: 2rem; font-weight: bold;">&lt;95%</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">→ 99%+</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">Conformidade</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown("""
        <div class="metric-box" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
            <div style="font-size: 2rem; font-weight: bold;">15-20%</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">→ &lt;2%</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">Retrabalho</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m4:
        st.markdown("""
        <div class="metric-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div style="font-size: 2rem; font-weight: bold;">28%</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Margem média</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">ETE Camburi</div>
        </div>
        """, unsafe_allow_html=True)

    # SEÇÃO 4: CASES DE SUCESSO
    st.markdown("---")
    st.subheader("🏆 Cases de Sucesso")

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown("""
        <div class="case-card">
            <h4>🌊 ETE Camburi</h4>
            <p><strong>57 L/s | R$ 12,5M</strong></p>
            <ul>
                <li>✅ Entregue no prazo</li>
                <li>✅ 28% de margem</li>
                <li>✅ Zero retrabalho</li>
                <li>✅ Aprovação Sabesp</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("""
        <div class="case-card">
            <h4>🏗️ Lote 1 - Engeform</h4>
            <p><strong>5 ETEs | R$ 45M</strong></p>
            <ul>
                <li>✅ Gestão centralizada</li>
                <li>✅ 5 consórcios alinhados</li>
                <li>✅ Dashboard em tempo real</li>
                <li>✅ Economia de 18%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown("""
        <div class="case-card">
            <h4>💧 ETA Metropolitana</h4>
            <p><strong>1000 L/s | R$ 82M</strong></p>
            <ul>
                <li>✅ Maior projeto da região</li>
                <li>✅ 1000 L/s tratados</li>
                <li>✅ Entrega em 18 meses</li>
                <li>✅ Referência Sabesp</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # SEÇÃO 5: SIMULADOR ROI
    st.markdown("---")
    st.subheader("💰 Simule sua Economia")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("**Ajuste os valores do seu lote:**")
        valor_lote = st.slider("Valor do Lote (R$M)", 1, 200, 55)
        margem_atual = st.slider("Margem Atual (%)", 5, 40, 15)
        retrabalho_atual = st.slider("Retrabalho Atual (%)", 0, 30, 18)

    with col_s2:
        # Calcular economia
        economia_retrabalho = valor_lote * (retrabalho_atual / 100) * 0.85  # 85% de redução
        nova_margem = min(margem_atual + 8, 35)  # Aumento médio de 8%
        ganho_margem = valor_lote * ((nova_margem - margem_atual) / 100)
        economia_total = economia_retrabalho + ganho_margem

        st.markdown(f"""
        <div style="background: #f0fff4; border-radius: 12px; padding: 1.5rem; border: 2px solid #27ae60;">
            <h3 style="color: #27ae60; margin-top: 0;">💵 Economia Projetada</h3>
            <div style="font-size: 2.5rem; font-weight: bold; color: #1E3A5F;">
                R$ {economia_total:.1f}M
            </div>
            <div style="margin-top: 10px;">
                <div>🔧 Redução retrabalho: <strong>R$ {economia_retrabalho:.1f}M</strong></div>
                <div>📈 Ganho de margem: <strong>R$ {ganho_margem:.1f}M</strong></div>
                <div style="margin-top: 10px; color: #666;">
                    Nova margem estimada: <strong>{nova_margem:.0f}%</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SEÇÃO 6: RODMAP
    st.markdown("---")
    st.subheader("🗓️ Roadmap de Implementação")

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    with col_r1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">🔬</div>
            <div style="font-weight: bold; color: #3498db;">Mês 1-2</div>
            <div style="font-size: 0.9rem;">Prototipagem</div>
            <div style="font-size: 0.8rem; color: #666;">Configuração inicial</div>
        </div>
        """, unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">🔗</div>
            <div style="font-weight: bold; color: #27ae60;">Mês 3-4</div>
            <div style="font-size: 0.9rem;">Integração</div>
            <div style="font-size: 0.8rem; color: #666;">Conectar sistemas</div>
        </div>
        """, unsafe_allow_html=True)

    with col_r3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">🎓</div>
            <div style="font-weight: bold; color: #f39c12;">Mês 5-6</div>
            <div style="font-size: 0.9rem;">Treinamento</div>
            <div style="font-size: 0.8rem; color: #666;">Capacitar equipe</div>
        </div>
        """, unsafe_allow_html=True)

    with col_r4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">🚀</div>
            <div style="font-weight: bold; color: #e74c3c;">Mês 7+</div>
            <div style="font-size: 0.9rem;">Rollout</div>
            <div style="font-size: 0.8rem; color: #666;">Operação completa</div>
        </div>
        """, unsafe_allow_html=True)

    # SEÇÃO 7: CTA (Call to Action)
    st.markdown("""
    <div class="cta-box">
        <h2 style="margin-top: 0;">🤝 Próximos Passos</h2>
        <p style="font-size: 1.1rem;">
            1. Reunião técnica de alinhamento<br>
            2. Demonstração do dashboard ao vivo<br>
            3. Proposta comercial personalizada<br>
            4. Kick-off do projeto
        </p>
        <div style="margin-top: 20px; font-size: 1.2rem;">
            📞 <strong>MC - Hydrosol AI</strong><br>
            🌊 Transformando Gestão de Portfólio em Saneamento
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FOOTER
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.85rem;">
        🌊 <strong>Hydrosol AI v5.1</strong> | Proposta de Valor Estratégica<br>
        Desenvolvido para reuniões comerciais com empreiteiras<br>
        <small>Última atualização: {atualizacao}</small>
    </div>
    """.format(atualizacao=datetime.now().strftime('%d/%m/%Y')), unsafe_allow_html=True)