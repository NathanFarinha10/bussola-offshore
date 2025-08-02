import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Bússola Offshore")

# --- CONEXÃO COM O SUPABASE ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- FUNÇÕES DE DADOS ---
@st.cache_data(ttl=600)
def fetch_table(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar dados da tabela {table_name}: {e}")
        return []

# --- FUNÇÕES DE AUTENTICAÇÃO ---
def sign_up(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.success("Registo bem-sucedido! Por favor, verifique o seu email para confirmar a sua conta.")
    except Exception as e:
        st.error(f"Erro no registo: {e}")

def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        # Armazena a informação do utilizador na sessão
        st.session_state['user'] = res.user
        st.rerun() # Reinicia o script para refletir o estado de login
    except Exception as e:
        st.error(f"Erro no login: {e}")

def sign_out():
    st.session_state.pop('user', None)
    st.rerun()

# --- FUNÇÃO PRINCIPAL DO PAINEL ---
def main_dashboard():
    st.sidebar.write(f"Bem-vindo, {st.session_state.user.email}")
    if st.sidebar.button("Sair"):
        sign_out()

    st.title("🚢 Bússola Offshore")
    st.header("Painel de Inteligência Macro")

    synthesis_data = fetch_table("weekly_synthesis")
    if synthesis_data:
        latest_synthesis = max(synthesis_data, key=lambda x: datetime.fromisoformat(x['created_at']))
        st.info(f"💡 **Síntese da Semana:** {latest_synthesis['synthesis_text']}")
    else:
        st.warning("Nenhuma síntese da semana encontrada.")

    st.markdown("---")

    managers_data = fetch_table("asset_managers")
    macro_points_data = fetch_table("macro_data_points")

    if not macro_points_data or not managers_data:
        st.warning("Dados macro ou de gestoras não encontrados. Insira dados no Supabase para exibir o painel.")
    else:
        df_managers = pd.DataFrame(managers_data)
        df_macro = pd.DataFrame(macro_points_data)
        latest_week = df_macro['week_of'].max()
        st.subheader(f"Visão Consolidada | Semana de: {datetime.strptime(latest_week, '%Y-%m-%d').strftime('%d/%m/%Y')}")
        df_latest = df_macro[df_macro['week_of'] == latest_week]
        df_merged = pd.merge(df_latest, df_managers[['id', 'name']], left_on='manager_id', right_on='id')
        df_pivot = df_merged.pivot(index='indicator_name', columns='name', values='indicator_value').reset_index()
        df_pivot = df_pivot.rename(columns={'indicator_name': 'Indicador'})
        desired_column_order = ['Indicador'] + ['BlackRock', 'J.P. Morgan', 'PIMCO', 'Bridgewater', 'Vanguard', 'Goldman Sachs']
        final_columns = [col for col in desired_column_order if col in df_pivot.columns]
        df_display = df_pivot[final_columns]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.success("Painel de dados carregado com sucesso!")

# --- LÓGICA DE ROTEAMENTO ---
# Verifica se a chave 'user' existe no estado da sessão
if 'user' not in st.session_state:
    st.title("Acesso à Plataforma Bússola Offshore")
    choice = st.selectbox("Escolha uma ação", ["Login", "Registar"])

    if choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            if submit_button:
                sign_in(email, password)
    else:
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Registar")
            if submit_button:
                sign_up(email, password)
else:
    # Se o utilizador está logado, mostra o painel principal
    main_dashboard()
