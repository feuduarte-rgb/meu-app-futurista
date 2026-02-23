import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="COMMAND CENTER HUD", layout="wide")

# Estilo Futurista
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00f2ff; }
    [data-testid="stMetric"] { background: rgba(0, 242, 255, 0.05); border: 1px solid #00f2ff; border-radius: 10px; padding: 20px; }
    h1, h2, h3 { color: #00f2ff; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

# URL da sua planilha (Já com o truque do /export?format=csv)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1s-s0We_XaTyVIv5LwaJ4PvmXkxi2EsNzP2JsR97n94k/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL_PLANILHA)
    # Limpa espaços extras nos nomes das colunas
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df = load_data()

    # Mapeamento Automático por Posição (AA=26, AC=28, AD=29)
    # Isso evita erros de nomes nessas colunas específicas
    col_credito = df.columns[26] # Volume de Crédito (AA)
    col_taxa = df.columns[28]    # Taxa (AC)
    col_tipo = df.columns[29]    # Tipo de Plano (AD)

    # Tenta encontrar as colunas de filtro (Ano, Grupo, Ponto)
    # Se não encontrar o nome exato, ele pega a que for parecida
    def find_col(possible_names, df):
        for p in possible_names:
            for c in df.columns:
                if p.lower() in c.lower(): return c
        return None

    c_ano = find_col(['Ano', 'Year', 'Produção'], df)
    c_grupo = find_col(['Grupo Economico', 'Grupo', 'Econômico'], df)
    c_ponto = find_col(['Ponto de Venda', 'Ponto', 'Concessionária'], df)

    # --- VERIFICAÇÃO DE SEGURANÇA ---
    if not c_ano:
        st.error(f"⚠️ Não encontrei a coluna de 'Ano'. Colunas disponíveis: {list(df.columns)}")
        st.stop()

    # --- SIDEBAR: NAVEGAÇÃO ---
    st.sidebar.title("🛸 NAVIGATION")
    
    anos = sorted(df[c_ano].unique())
    ano_sel = st.sidebar.multiselect("PERÍODO (ANOS)", anos, default=anos)
    
    grupos = sorted(df[c_grupo].unique()) if c_grupo else ["Todos"]
    grupo_sel = st.sidebar.multiselect("GRUPO ECONÔMICO", grupos, default=grupos)

    # --- FILTRAGEM ---
    mask = df[c_ano].isin(ano_sel)
    if c_grupo: mask &= df[c_grupo].isin(grupo_sel)
    df_filtered = df[mask]

    # --- DASHBOARD ---
    st.title("⚡ DATA ANALYTICS HUD")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("VOLUME CRÉDITO", f"R$ {df_filtered[col_credito].sum():,.2f}")
    with col2:
        st.metric("QUANTIDADE (LINHAS)", len(df_filtered))
    with col3:
        st.metric("TAXA MÉDIA", f"{df_filtered[col_taxa].mean():.2f}%")

    st.markdown("---")
    
    # Gráfico Futurista
    fig = px.bar(df_filtered, x=col_tipo, y=col_credito, color=col_tipo,
                 title="DESEMPENHO POR TIPO DE PLANO", template="plotly_dark",
                 color_discrete_sequence=['#00f2ff', '#39ff14', '#ff00ff'])
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
    if 'df' in locals(): st.write("Colunas detectadas:", list(df.columns))
