import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide")

# --- CONEXÃO COM O SUPABASE ---
# Inicializa a conexão. Usa os "secrets" que configuramos no Streamlit Cloud.
# A anotação @st.cache_resource garante que a conexão seja feita apenas uma vez.
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- FUNÇÕES DE CONSULTA DE DADOS ---
# Função para buscar dados de uma tabela específica.
# A anotação @st.cache_data garante que a mesma consulta não seja refeita
# repetidamente, economizando recursos. O ttl (time to live) de 10 min
# significa que os dados ficam em cache por 10 minutos antes de buscar de novo.
@st.cache_data(ttl=600)
def fetch_data(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar dados da tabela {table_name}: {e}")
        return None

# --- INTERFACE DO USUÁRIO (UI) ---
st.title("🚢 Bússola Offshore")
st.header("Painel de Inteligência Macro")

st.markdown("---") # Linha divisória

# --- EXIBIÇÃO DOS DADOS ---
st.subheader("Gestoras Acompanhadas")

# Busca os dados da tabela 'asset_managers'
asset_managers_data = fetch_data("asset_managers")

# Verifica se os dados foram recebidos
if asset_managers_data:
    # Converte os dados para um formato de tabela com a biblioteca Pandas
    df = pd.DataFrame(asset_managers_data).sort_values(by="id")

    # Renomeia as colunas para uma melhor apresentação
    df_display = df[['name', 'logo_url']].rename(columns={'name': 'Nome da Gestora', 'logo_url': 'URL do Logo'})

    # Exibe a tabela na tela
    st.dataframe(df_display, use_container_width=True)
    st.success("Dados das gestoras carregados com sucesso do Supabase!")
else:
    st.warning("Não foi possível carregar os dados das gestoras.")
