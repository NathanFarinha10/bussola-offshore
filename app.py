import streamlit as st

st.set_page_config(layout="wide")

st.title("🚢 Bússola Offshore")
st.header("Painel de Inteligência Macro")

st.write("Nosso MVP está no ar!")
st.info("O próximo passo é conectar com o Supabase para trazer os dados reais.")

# Tentativa de ler os secrets (vamos usar isso no próximo sprint)
st.write("Tentando ler as configurações do Supabase:")
try:
    st.write("URL do Supabase:", st.secrets["SUPABASE_URL"])
    st.success("Secret 'SUPABASE_URL' lido com sucesso!")
except:
    st.error("Secret 'SUPABASE_URL' não encontrado. Configure no Streamlit Cloud!")

try:
    st.write("Chave do Supabase:", st.secrets["SUPABASE_KEY"][:5] + "...") # Mostra só os 5 primeiros caracteres
    st.success("Secret 'SUPABASE_KEY' lido com sucesso!")
except:
    st.error("Secret 'SUPABASE_KEY' não encontrado. Configure no Streamlit Cloud!")
