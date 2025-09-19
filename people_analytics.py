import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import base64
from io import BytesIO
from pdfminer.high_level import extract_text

# Configuração da página
st.set_page_config(
    page_title="People Analytics - Dashboard Multiperíodo",
    page_icon="📊",
    layout="wide"
)

# Adicionar CSS para o botão de download e abas
st.markdown("""
<style>
.download-btn {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 10px 2px;
    cursor: pointer;
    border-radius: 4px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #f0f2f6;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}

.stTabs [aria-selected="true"] {
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Título do dashboard
st.title("📊 People Analytics - Dashboard Multiperíodo")
st.markdown("Faça upload de arquivos PDF ou CSV com os dados para gerar o dashboard automaticamente")

# Botão para exportar como PDF
st.markdown("""
<div style="text-align: right; margin-bottom: 20px;">
    <button class="download-btn" onclick="exportToPDF()">📥 Exportar como PDF</button>
</div>
""", unsafe_allow_html=True)

# JavaScript para exportar como PDF
st.markdown("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

<script>
function exportToPDF() {
    // Mostrar mensagem de carregamento
    const loadingElement = document.createElement('div');
    loadingElement.style.position = 'fixed';
    loadingElement.style.top = '50%';
    loadingElement.style.left = '50%';
    loadingElement.style.transform = 'translate(-50%, -50%)';
    loadingElement.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    loadingElement.style.color = 'white';
    loadingElement.style.padding = '20px';
    loadingElement.style.borderRadius = '5px';
    loadingElement.style.zIndex = '10000';
    loadingElement.innerHTML = '<h3>Gerando PDF, aguarde...</h3>';
    document.body.appendChild(loadingElement);
    
    // Capturar o conteúdo principal
    const element = document.querySelector('.main');
    
    setTimeout(() => {
        html2canvas(element, {
            scale: 2,
            useCORS: true,
            logging: false
        }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jspdf.jsPDF('p', 'mm', 'a4');
            const imgProps = pdf.getImageProperties(imgData);
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
            
            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save('dashboard_people_analytics.pdf');
            
            // Remover mensagem de carregamento
            document.body.removeChild(loadingElement);
            
            // Mostrar mensagem de sucesso
            const successElement = document.createElement('div');
            successElement.style.position = 'fixed';
            successElement.style.top = '20px';
            successElement.style.right = '20px';
            successElement.style.backgroundColor = '#4CAF50';
            successElement.style.color = 'white';
            successElement.style.padding = '10px 20px';
            successElement.style.borderRadius = '5px';
            successElement.style.zIndex = '10000';
            successElement.innerHTML = '<strong>✓ Sucesso!</strong> PDF baixado.';
            document.body.appendChild(successElement);
            
            setTimeout(() => {
                document.body.removeChild(successElement);
            }, 3000);
        });
    }, 500);
}
</script>
""", unsafe_allow_html=True)

# Inicializar dados na sessão
if 'dados_mensais' not in st.session_state:
    st.session_state.dados_mensais = {}
if 'equipe' not in st.session_state:
    st.session_state.equipe = {}

# Função para processar PDF
def processar_pdf(arquivo_pdf, mes_ano):
    try:
        # Extrair texto do PDF
        texto = extract_text(arquivo_pdf)
        
        # Padroniza quebras de linha
        texto = texto.replace('\n', ' ')
        
        # Expressões regulares para extrair dados
        padroes = {
            "desligamentos": r"Desligamentos:\s*(\d+)",
            "media_colaboradores": r"Média de colaboradores:\s*(\d+)",
            "tempo_dias": r"(\d+)\s*dias",
            "faltas": r"Faltas:\s*(\d+)",
            "atestados": r"Atestados:\s*(\d+)",
            "dias_possiveis": r"Dias possíveis:\s*(\d+)",
            "horas_extras_valor": r"R\$\s*([\d.,]+)",
            "ferias_vencidas": r"Férias vencidas:\s*(\d+)",
            "ferias_programadas": r"Férias programadas:\s*(\d+)",
            "admissoes": r"Admissões:\s*(\d+)",
            "desligamentos_periodo": r"Desligamento:\s*(\d+)",
            "idade_media": r"Idade média:\s*([\d.]+)",
            "idade_minima": r"Idade mínima:\s*(\d+)",
            "idade_maxima": r"Idade máxima:\s*(\d+)",
        }
        
        dados = {"mes_ano": mes_ano}
        
        # Extrair dados usando regex
        for chave, padrao in padroes.items():
            correspondencia = re.search(padrao, texto)
            if correspondencia:
                try:
                    if chave in ["idade_media", "horas_extras_valor"]:
                        # Converter para float, tratando vírgula como separador decimal
                        valor = correspondencia.group(1).replace('.', '').replace(',', '.')
                        dados[chave] = float(valor)
                    else:
                        dados[chave] = int(correspondencia.group(1))
                except:
                    pass
        
        # Calcular métricas derivadas
        if "desligamentos" in dados and "media_colaboradores" in dados:
            dados["turnover"] = dados["desligamentos"] / dados["media_colaboradores"] if dados["media_colaboradores"] > 0 else 0
        
        if "faltas" in dados and "atestados" in dados and "dias_possiveis" in dados:
            dados["absenteismo"] = (dados["faltas"] + dados["atestados"]) / dados["dias_possiveis"] if dados["dias_possiveis"] > 0 else 0
        
        if "tempo_dias" in dados:
            dados["anos_casa"] = dados["tempo_dias"] // 365
            dados["meses_casa"] = (dados["tempo_dias"] % 365) // 30
        
        # Extrair dados da equipe
        equipe = {}
        departamentos = ["Fiscal", "Contábil", "Pessoal"]
        
        for depto in departamentos:
            padrao_depto = rf"Depto {depto}.*?Cargo.*?Admissão.*?Salário(.*?)(?=Depto|$)"
            match = re.search(padrao_depto, texto, re.DOTALL | re.IGNORECASE)
            if match:
                linhas = match.group(1).strip().split('\n')
                equipe[depto] = []
                
                for i in range(0, len(linhas), 4):
                    if i + 3 < len(linhas):
                        nome = linhas[i].strip()
                        cargo = linhas[i+1].strip()
                        admissao = linhas[i+2].strip()
                        salario = linhas[i+3].strip()
                        
                        if nome and cargo and admissao and salario:
                            # Converter salário para float
                            try:
                                salario_valor = float(salario.replace('R$', '').replace('.', '').replace(',', '.').strip())
                            except:
                                salario_valor = 0
                                
                            equipe[depto].append({
                                "nome": nome,
                                "cargo": cargo,
                                "admissao": admissao,
                                "salario": salario_valor
                            })
        
        return dados, equipe
        
    except Exception as e:
        st.error(f"Erro ao processar PDF: {str(e)}")
        return None, None

# Upload de arquivo
st.sidebar.header("📤 Upload de Arquivos")
mes_ano = st.sidebar.text_input("Mês/Ano de Referência (ex: Agosto/2025)", "Agosto/2025")
arquivo = st.sidebar.file_uploader("Faça upload do relatório (PDF)", type=["pdf"])

if arquivo is not None and mes_ano:
    if st.sidebar.button("Processar Arquivo"):
        with st.spinner("Processando arquivo..."):
            dados_processados, equipe_processada = processar_pdf(arquivo, mes_ano)
            
            if dados_processados:
                st.session_state.dados_mensais[mes_ano] = dados_processados
                st.session_state.equipe[mes_ano] = equipe_processada
                st.sidebar.success(f"Arquivo {mes_ano} processado com sucesso!")

# Se não há dados, usar dados de exemplo
if not st.session_state.dados_mensais:
    st.info("Faça upload de arquivos PDF para processar seus dados. Usando dados de exemplo para demonstração.")
    
    # Dados de exemplo
    exemplo_dados = {
        "Agosto/2025": {
            "mes_ano": "Agosto/2025",
            "desligamentos": 1,
            "media_colaboradores": 38,
            "turnover": 0.03,
            "tempo_dias": 792,
            "anos_casa": 2,
            "meses_casa": 2,
            "faltas": 0,
            "atestados": 12,
            "dias_possiveis": 20,
            "absenteismo": 0.6,
            "horas_extras_valor": 3673.62,
            "ferias_vencidas": 18,
            "ferias_programadas": 3,
            "admissoes": 1,
            "desligamentos_periodo": 1,
            "idade_media": 32.8,
            "idade_minima": 22,
            "idade_maxima": 56,
        }
    }
    
    st.session_state.dados_mensais = exemplo_dados

# Dados fixos (não extraídos do PDF)
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

# Criar abas para cada mês e visão geral
abas = list(st.session_state.dados_mensais.keys()) + ["Visão Geral"]
tabs = st.tabs(abas)

for i, mes in enumerate(st.session_state.dados_mensais.keys()):
    with tabs[i]:
        dados = st.session_state.dados_mensais[mes]
        
        st.header(f"Métricas de {mes}")
        
        # Layout do dashboard
        col1, col2, col3 = st.columns(3)

        with col1:
            # Card de Turnover
            st.metric(
                label="Turnover", 
                value=f"{dados.get('turnover', 0):.2%}",
                help="Número de desligamentos no período / nº médio de colaboradores ativos"
            )

        with col2:
            # Card de Tempo médio de casa
            if 'anos_casa' in dados and 'meses_casa' in dados:
                st.metric(
                    label="Tempo médio de casa", 
                    value=f"{dados['anos_casa']} anos e {dados['meses_casa']} meses"
                )

        with col3:
            # Card de Absenteísmo
            if 'absenteismo' in dados:
                st.metric(
                    label="Absenteísmo", 
                    value=f"{dados['absenteismo']:.2%}",
                    help="Número de faltas injustificadas + atestados / total de dias possíveis"
                )

        # Gráficos e visualizações
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de Folha de Pagamento por Centro de Custo
            st.subheader("Folha de Pagamento por Centro de Custo")
            folha_data = {
                "Centro de Custo": list(folha_pagamento.keys()),
                "Valor (R$)": list(folha_pagamento.values())
            }
            fig_folha = px.bar(folha_data, x="Centro de Custo", y="Valor (R$)", 
                               color="Centro de Custo", text_auto=True)
            st.plotly_chart(fig_folha, use_container_width=True, key=f"folha_{mes}")
            
            # Gráfico de Férias
            if 'ferias_vencidas' in dados and 'ferias_programadas' in dados:
                st.subheader("Situação de Férias")
                ferias_data = {
                    "Situação": ["Vencidas", "Programadas"],
                    "Quantidade": [dados["ferias_vencidas"], 
                                  dados["ferias_programadas"]]
                }
                fig_ferias = px.pie(ferias_data, values="Quantidade", names="Situação")
                st.plotly_chart(fig_ferias, use_container_width=True, key=f"ferias_{mes}")

        with col2:
            # Gráfico de Faixas Etárias
            st.subheader("Distribuição por Faixa Etária")
            faixas_data = {
                "Faixa Etária": list(faixas_etarias.keys()),
                "Quantidade": list(faixas_etarias.values())
            }
            fig_faixas = px.pie(faixas_data, values="Quantidade", names="Faixa Etária")
            st.plotly_chart(fig_faixas, use_container_width=True, key=f"faixas_{mes}")
            
            # Gráfico de Licenças
            st.subheader("Licenças e Afastamentos")
            licencas_data = {
                "Tipo": list(licencas.keys()),
                "Quantidade": list(licencas.values())
            }
            fig_licencas = px.bar(licencas_data, x="Tipo", y="Quantidade", 
                                  color="Tipo", text_auto=True)
            st.plotly_chart(fig_licencas, use_container_width=True, key=f"licencas_{mes}")

        # Informações adicionais
        col1, col2 = st.columns(2)

        with col1:
            if 'admissoes' in dados and 'desligamentos_periodo' in dados:
                st.subheader("Admissões x Demissões")
                adm_dem_data = {
                    "Tipo": ["Admissões", "Desligamentos"],
                    "Quantidade": [dados["admissoes"], 
                                  dados["desligamentos_periodo"]]
                }
                fig_adm_dem = px.bar(adm_dem_data, x="Tipo", y="Quantidade", 
                                     color="Tipo", text_auto=True)
                st.plotly_chart(fig_adm_dem, use_container_width=True, key=f"adm_dem_{mes}")

        with col2:
            if 'horas_extras_valor' in dados:
                st.subheader("Horas Extras")
                st.metric(
                    label="Valor Total (R$)", 
                    value=f"R$ {dados['horas_extras_valor']:,.2f}"
                )
            
            st.subheader("Banco de Horas")
            st.metric(
                label="Saldo Médio", 
                value="0 horas"
            )

        # Informações de idade
        if all(k in dados for k in ["idade_media", "idade_minima", "idade_maxima"]):
            st.subheader("Informações de Idade")
            col1, col2, col3 = st.columns(3)
            col1.metric("Idade Média", f"{dados['idade_media']} anos")
            col2.metric("Idade Mínima", f"{dados['idade_minima']} anos")
            col3.metric("Idade Máxima", f"{dados['idade_maxima']} anos")

        # Dados da equipe
        if mes in st.session_state.equipe and st.session_state.equipe[mes]:
            st.subheader("Equipe por Departamento")
            
            for depto, funcionarios in st.session_state.equipe[mes].items():
                with st.expander(f"Departamento {depto} ({len(funcionarios)} funcionários)"):
                    df_equipe = pd.DataFrame(funcionarios)
                    st.dataframe(df_equipe)
                    
                    # Estatísticas do departamento
                    if not df_equipe.empty:
                        st.metric("Total de Funcionários", len(funcionarios))
                        st.metric("Salário Médio", f"R$ {df_equipe['salario'].mean():.2f}")
                        st.metric("Salário Total", f"R$ {df_equipe['salario'].sum():.2f}")

# Aba de visão geral
with tabs[-1]:
    st.header("Visão Geral - Todos os Meses")
    
    if len(st.session_state.dados_mensais) > 1:
        # Criar DataFrame com dados de todos os meses
        dados_gerais = []
        for mes, dados in st.session_state.dados_mensais.items():
            dados_gerais.append({
                "Mês": mes,
                "Turnover": dados.get("turnover", 0),
                "Absenteísmo": dados.get("absenteismo", 0),
                "Admissões": dados.get("admissoes", 0),
                "Desligamentos": dados.get("desligamentos_periodo", 0),
                "Colaboradores": dados.get("media_colaboradores", 0),
                "Horas Extras (R$)": dados.get("horas_extras_valor", 0),
            })
        
        df_geral = pd.DataFrame(dados_gerais)
        
        # Gráficos de evolução
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Evolução do Turnover")
            fig_turnover = px.line(df_geral, x="Mês", y="Turnover", 
                                  title="Evolução do Turnover ao Longo do Tempo")
            st.plotly_chart(fig_turnover, use_container_width=True, key="turnover_geral")
        
        with col2:
            st.subheader("Evolução do Absenteísmo")
            fig_absenteismo = px.line(df_geral, x="Mês", y="Absenteísmo", 
                                     title="Evolução do Absenteísmo ao Longo do Tempo")
            st.plotly_chart(fig_absenteismo, use_container_width=True, key="absenteismo_geral")
        
        # Tabela comparativa
        st.subheader("Comparativo entre Meses")
        st.dataframe(df_geral.set_index("Mês"))
        
        # Estatísticas consolidadas
        st.subheader("Estatísticas Consolidadas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Admissões", df_geral["Admissões"].sum())
            st.metric("Média de Turnover", f"{df_geral['Turnover'].mean():.2%}")
        
        with col2:
            st.metric("Total de Desligamentos", df_geral["Desligamentos"].sum())
            st.metric("Média de Absenteísmo", f"{df_geral['Absenteísmo'].mean():.2%}")
        
        with col3:
            st.metric("Média de Colaboradores", f"{df_geral['Colaboradores'].mean():.0f}")
            st.metric("Total em Horas Extras", f"R$ {df_geral['Horas Extras (R$)'].sum():,.2f}")
    
    else:
        st.info("Adicione mais meses para habilitar a visão geral comparativa.")

# Instruções para o usuário
st.sidebar.markdown("""
## 📋 Instruções de Uso

1. **Upload de arquivos**:
   - Digite o mês/ano de referência
   - Faça upload do arquivo PDF
   - Clique em "Processar Arquivo"

2. **Navegação**:
   - Cada mês processado terá sua própria aba
   - A última aba mostra a visão geral consolidada

3. **Exportar relatório**:
   - Use o botão "Exportar como PDF" no topo da página

4. **Dados da equipe**:
   - Os dados da equipe são extraídos automaticamente
   - Expanda os departamentos para ver detalhes
""")
