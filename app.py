import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide")

# --- CONEXÃO COM O SUPABASE ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- FUNÇÕES DE CONSULTA DE DADOS ---
@st.cache_data(ttl=600) # Cache de 10 minutos
def fetch_table(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar dados da tabela {table_name}: {e}")
        return []

# --- INTERFACE DO USUÁRIO (UI) ---
st.title("🚢 Bússola Offshore")
st.header("Painel de Inteligência Macro")

# --- BUSCAR E EXIBIR A SÍNTESE DA SEMANA ---
synthesis_data = fetch_table("weekly_synthesis")
if synthesis_data:
    # Pega a síntese mais recente com base na data
    latest_synthesis = max(synthesis_data, key=lambda x: datetime.fromisoformat(x['created_at']))
    st.info(f"💡 **Síntese da Semana:** {latest_synthesis['synthesis_text']}")
else:
    st.warning("Nenhuma síntese da semana encontrada.")

st.markdown("---")

# --- BUSCAR E PROCESSAR OS DADOS DO PAINEL ---
# 1. Buscar os dados brutos
managers_data = fetch_table("asset_managers")
macro_points_data = fetch_table("macro_data_points")

if not macro_points_data or not managers_data:
    st.warning("Dados macro ou de gestoras não encontrados. Insira dados no Supabase para exibir o painel.")
else:
    # 2. Converter para DataFrames do Pandas
    df_managers = pd.DataFrame(managers_data)
    df_macro = pd.DataFrame(macro_points_data)

    # 3. Pegar a semana mais recente dos dados
    latest_week = df_macro['week_of'].max()
    st.subheader(f"Visão Consolidada | Semana de: {datetime.strptime(latest_week, '%Y-%m-%d').strftime('%d/%m/%Y')}")
    
    df_latest = df_macro[df_macro['week_of'] == latest_week]

    # 4. Juntar os nomes das gestoras com os pontos de dados
    df_merged = pd.merge(
        df_latest,
        df_managers[['id', 'name']],
        left_on='manager_id',
        right_on='id'
    )

    # 5. Pivotar a tabela para o formato final (a "mágica" do pandas)
    # Queremos os nomes das gestoras como colunas e os indicadores como linhas
    df_pivot = df_merged.pivot(
        index='indicator_name',
        columns='name',
        values='indicator_value'
    ).reset_index()

    # 6. Renomear e reordenar as colunas para melhor visualização
    df_pivot = df_pivot.rename(columns={'indicator_name': 'Indicador'})
    
    # Define a ordem desejada das colunas (gestoras)
    desired_column_order = ['Indicador'] + [
        'BlackRock', 'J.P. Morgan', 'PIMCO', 
        'Bridgewater', 'Vanguard', 'Goldman Sachs'
    ]
    
    # Garante que apenas colunas existentes sejam usadas, para evitar erros
    final_columns = [col for col in desired_column_order if col in df_pivot.columns]
    df_display = df_pivot[final_columns]

    # 7. Exibir a tabela final no Streamlit
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    st.success("Painel de dados carregado com sucesso!")
