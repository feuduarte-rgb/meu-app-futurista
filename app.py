import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="COMMAND CENTER HUD", layout="wide")

# --- ESTILO CSS FUTURISTA ---
st.markdown("""
    <style>
    .main { background-color: #050505; }
    [data-testid="stMetric"] {
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid #00f2ff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
    }
    div[data-testid="stMetricValue"] { color: #00f2ff; font-family: 'Share Tech Mono', monospace; }
    h1, h2, h3 { color: #00f2ff; text-transform: uppercase; letter-spacing: 3px; font-family: 'Orbitron', sans-serif; }
    .stSelectbox, .stMultiSelect { color: #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM DADOS ---
# Substitua pelo link da sua planilha privada (após configurar o Secrets no Streamlit)
# Ou use o link 'Publicado como CSV' para teste rápido
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1s-s0We_XaTyVIv5LwaJ4PvmXkxi2EsNzP2JsR97n94k/edit?gid=0#gid=0"

@st.cache_data(ttl=600)
def carregar_dados():
    # Lendo a planilha (usando nomes de colunas ou índices se necessário)
    df = pd.read_csv(URL_PLANILHA)
    
    # Mapeamento conforme sua descrição (Ajuste os nomes se forem diferentes na sua planilha)
    # Assumindo que a exportação do PBI traz cabeçalhos, vamos renomear para facilitar
    df.columns.values[26] = "Volume_Credito"  # Coluna AA (27ª coluna, índice 26)
    df.columns.values[28] = "Taxa"           # Coluna AC (29ª coluna, índice 28)
    df.columns.values[29] = "Tipo_Plano"     # Coluna AD (30ª coluna, índice 29)
    
    return df

try:
    data = carregar_dados()

    # --- SIDEBAR: FILTROS DE COMANDO ---
    st.sidebar.title("🛸 NAVIGATION")
    
    anos = sorted(data['Ano'].unique()) # Supondo que a coluna se chame 'Ano'
    ano_selecionado = st.sidebar.multiselect("PERÍODO (ANOS)", anos, default=anos)
    
    grupos = sorted(data['Grupo Economico'].unique())
    grupo_selecionado = st.sidebar.multiselect("GRUPO ECONÔMICO", grupos, default=grupos)
    
    pontos = sorted(data['Ponto de Vendas'].unique())
    ponto_selecionado = st.sidebar.multiselect("PONTO DE VENDA", pontos, default=pontos)

    # --- LÓGICA DE FILTRAGEM ---
    mask = (data['Ano'].isin(ano_selecionado)) & \
           (data['Grupo Economico'].isin(grupo_selecionado)) & \
           (data['Ponto de Vendas'].isin(ponto_selecionado))
    
    df_filtered = data[mask]

    # --- HEADER ---
    st.title("⚡ DATA ANALYTICS HUD")
    st.write(f"Monitorando {len(df_filtered)} registros ativos")

    # --- KPIs PRINCIPAIS ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        total_credito = df_filtered['Volume_Credito'].sum()
        st.metric("VOLUME CRÉDITO", f"R$ {total_credito:,.2f}")
    
    with c2:
        qtd_total = len(df_filtered) # Quantidade por linhas conforme solicitado
        st.metric("QUANTIDADE (UN)", f"{qtd_total}")
        
    with c3:
        taxa_media = df_filtered['Taxa'].mean()
        st.metric("TAXA MÉDIA", f"{taxa_media:.2f}%")
        
    with c4:
        ticket_medio = total_credito / qtd_total if qtd_total > 0 else 0
        st.metric("TICKET MÉDIO", f"R$ {ticket_medio:,.2f}")

    # --- GRÁFICOS COMPARATIVOS ---
    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Distribuição por Plano")
        fig_plano = px.bar(
            df_filtered.groupby('Tipo_Plano').agg({'Volume_Credito': 'sum'}).reset_index(),
            x='Tipo_Plano', y='Volume_Credito',
            template="plotly_dark", color_discrete_sequence=['#00f2ff']
        )
        st.plotly_chart(fig_plano, use_container_width=True)

    with col_right:
        st.subheader("📈 Evolução Mensal")
        # Supondo coluna 'Mes'
        fig_evolucao = px.line(
            df_filtered.groupby(['Ano', 'Mes']).size().reset_index(name='Qtd'),
            x='Mes', y='Qtd', color='Ano',
            template="plotly_dark", line_shape="spline",
            color_discrete_sequence=['#00f2ff', '#ff00ff']
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
    st.info("Verifique se os nomes das colunas na planilha coincidem com o código.")
