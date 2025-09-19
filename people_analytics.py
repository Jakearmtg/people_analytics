import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="People Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# CSS para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Título do dashboard
st.markdown('<h1 class="main-header">📊 People Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Sistema de análise de métricas de recursos humanos**")

# Inicializar dados na sessão
if 'dados_mensais' not in st.session_state:
    st.session_state.dados_mensais = {}

# Dados fixos (hardcoded para performance)
folha_pagamento = {
    "Fênix": 16072.35, 
    "Pessoal": 22224.47, 
    "Comercial": 15985.94, 
    "Escrita": 35751.12, 
    "Contábil": 44297.26,
    "Economic":  80829.93
    
}

faixas_etarias = {
    "≤ 25 anos": 9,
    "26–35 anos": 16,
    "36–45 anos": 11,
    "46–55 anos": 3,
    "≥ 56 anos": 1
}

licencas = {
    "maternidade": 0,
    "doenca": 1,
    "acidente": 0
}

# Sidebar para entrada de dados
with st.sidebar:
    st.header("📋 Entrada de Dados")
    mes_ano = st.text_input("Mês/Ano de Referência", "Agosto/2025")
    
    with st.expander("Inserir Métricas Principais"):
        col1, col2 = st.columns(2)
        with col1:
            desligamentos = st.number_input("Desligamentos", min_value=0, value=1)
            media_colab = st.number_input("Média Colaboradores", min_value=1, value=38)
            admissoes = st.number_input("Admissões", min_value=0, value=1)
        
        with col2:
            faltas = st.number_input("Faltas", min_value=0, value=0)
            atestados = st.number_input("Atestados", min_value=0, value=12)
            ferias_vencidas = st.number_input("Férias Vencidas", min_value=0, value=18)
        
        if st.button("💾 Salvar Dados do Mês"):
            turnover = desligamentos / media_colab if media_colab > 0 else 0
            absenteismo = (faltas + atestados) / 20 if 20 > 0 else 0  # 20 dias úteis padrão
            
            st.session_state.dados_mensais[mes_ano] = {
                "desligamentos": desligamentos,
                "media_colaboradores": media_colab,
                "turnover": turnover,
                "admissoes": admissoes,
                "faltas": faltas,
                "atestados": atestados,
                "absenteismo": absenteismo,
                "ferias_vencidas": ferias_vencidas,
                "ferias_programadas": 3,  # Valor padrão
                "horas_extras_valor": 3673.62,  # Valor padrão
            }
            st.success(f"Dados de {mes_ano} salvos!")

# Dados de exemplo se não houver dados
if not st.session_state.dados_mensais:
    st.info("💡 Use a barra lateral para adicionar dados. Mostrando dados de exemplo.")
    st.session_state.dados_mensais = {
        "Agosto/2025": {
            "desligamentos": 1,
            "media_colaboradores": 38,
            "turnover": 0.03,
            "admissoes": 1,
            "faltas": 0,
            "atestados": 12,
            "absenteismo": 0.6,
            "ferias_vencidas": 18,
            "ferias_programadas": 3,
            "horas_extras_valor": 3673.62,
        }
    }

# Criar abas para cada mês
abas = list(st.session_state.dados_mensais.keys())
tabs = st.tabs(abas)

for i, mes in enumerate(st.session_state.dados_mensais.keys()):
    with tabs[i]:
        dados = st.session_state.dados_mensais[mes]
        
        st.header(f"📈 Métricas de {mes}")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Turnover", f"{dados.get('turnover', 0):.2%}", help="Desligamentos / Média de colaboradores")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Absenteísmo", f"{dados.get('absenteismo', 0):.2%}", help="Faltas + Atestados / Dias úteis")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Admissões", dados.get('admissoes', 0))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Desligamentos", dados.get('desligamentos', 0))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de Folha de Pagamento
            st.subheader("💰 Folha de Pagamento por Centro de Custo")
            folha_df = pd.DataFrame({
                "Centro de Custo": list(folha_pagamento.keys()),
                "Valor (R$)": list(folha_pagamento.values())
            })
            fig_folha = px.bar(folha_df, x="Centro de Custo", y="Valor (R$)", 
                              color="Centro de Custo", text_auto=True)
            st.plotly_chart(fig_folha, use_container_width=True, key=f"folha_{mes}")
            
            # Gráfico de Férias
            st.subheader("🏖️ Situação de Férias")
            ferias_data = {
                "Situação": ["Vencidas", "Programadas"],
                "Quantidade": [dados.get("ferias_vencidas", 0), dados.get("ferias_programadas", 0)]
            }
            fig_ferias = px.pie(ferias_data, values="Quantidade", names="Situação")
            st.plotly_chart(fig_ferias, use_container_width=True, key=f"ferias_{mes}")
        
        with col2:
            # Gráfico de Faixas Etárias
            st.subheader("👥 Distribuição por Faixa Etária")
            faixas_df = pd.DataFrame({
                "Faixa Etária": list(faixas_etarias.keys()),
                "Quantidade": list(faixas_etarias.values())
            })
            fig_faixas = px.pie(faixas_df, values="Quantidade", names="Faixa Etária")
            st.plotly_chart(fig_faixas, use_container_width=True, key=f"faixas_{mes}")
            
            # Gráfico de Licenças
            st.subheader("🏥 Licenças e Afastamentos")
            licencas_df = pd.DataFrame({
                "Tipo": list(licencas.keys()),
                "Quantidade": list(licencas.values())
            })
            fig_licencas = px.bar(licencas_df, x="Tipo", y="Quantidade", 
                                 color="Tipo", text_auto=True)
            st.plotly_chart(fig_licencas, use_container_width=True, key=f"licencas_{mes}")
        
        # Métricas secundárias
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Detalhes Adicionais")
            st.write(f"**Média de colaboradores:** {dados.get('media_colaboradores', 0)}")
            st.write(f"**Faltas injustificadas:** {dados.get('faltas', 0)}")
            st.write(f"**Atestados médicos:** {dados.get('atestados', 0)}")
            st.write(f"**Férias vencidas:** {dados.get('ferias_vencidas', 0)}")
            st.write(f"**Férias programadas:** {dados.get('ferias_programadas', 0)}")
        
        with col2:
            st.subheader("⏰ Horas Extras")
            st.metric("Valor Total", f"R$ {dados.get('horas_extras_valor', 0):,.2f}")
            st.metric("Banco de Horas", "0 horas")
            st.metric("Saldo Médio", "0 horas")

# Visão Geral entre meses
if len(st.session_state.dados_mensais) > 1:
    st.header("📋 Visão Geral - Comparativo entre Meses")
    
    dados_gerais = []
    for mes, dados in st.session_state.dados_mensais.items():
        dados_gerais.append({
            "Mês": mes,
            "Turnover": dados.get("turnover", 0),
            "Absenteísmo": dados.get("absenteismo", 0),
            "Admissões": dados.get("admissoes", 0),
            "Desligamentos": dados.get("desligamentos", 0),
            "Colaboradores": dados.get("media_colaboradores", 0),
        })
    
    df_geral = pd.DataFrame(dados_gerais)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolução do Turnover")
        fig_turnover = px.line(df_geral, x="Mês", y="Turnover", 
                              title="Evolução do Turnover")
        st.plotly_chart(fig_turnover, use_container_width=True, key="turnover_geral")
    
    with col2:
        st.subheader("Evolução do Absenteísmo")
        fig_absenteismo = px.line(df_geral, x="Mês", y="Absenteísmo", 
                                 title="Evolução do Absenteísmo")
        st.plotly_chart(fig_absenteismo, use_container_width=True, key="absenteismo_geral")
    
    # Tabela comparativa
    st.subheader("Tabela Comparativa")
    st.dataframe(df_geral.set_index("Mês").style.format({
        "Turnover": "{:.2%}",
        "Absenteísmo": "{:.2%}"
    }))

# Instruções na sidebar
st.sidebar.markdown("---")
st.sidebar.info("""
**📝 Instruções:**
1. Digite o mês/ano de referência
2. Preencha as métricas principais
3. Clique em "Salvar Dados do Mês"
4. Repita para outros períodos
5. Visualize os dados nas abas acima
""")

# Rodapé
st.markdown("---")
st.caption("People Analytics Dashboard • Desenvolvido para análise de métricas de RH • " + datetime.now().strftime("%d/%m/%Y"))