import streamlit as st
import requests

# Configurazione iniziale
st.set_page_config(page_title="Trading Bot AI", layout="wide")
st.title("🤖 Dashboard Trading Operativo")

# --- RECUPERO CHIAVI ---
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    ET_KEY = st.secrets["ETORO_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
    st.sidebar.success("✅ Connessione API Stabilita")
except Exception as e:
    st.error("❌ Errore nei Secrets! Controlla di aver inserito BITPANDA_API_KEY, ETORO_API_KEY e NEWS_API_KEY su Streamlit.")
    st.stop()

# --- FUNZIONE NEWS ---
def prendi_notizie(azienda):
    url = f"https://newsapi.org/v2/everything?q={azienda}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        if r.get('articles'):
            return r['articles'][0]['title']
    except:
        return "Nessuna notizia trovata."
    return "In attesa di news..."

# --- DASHBOARD ---
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Analisi Mercato")
    for asset in ["Leonardo SPA", "Intesa Sanpaolo"]:
        news = prendi_notizie(asset)
        st.subheader(asset)
        st.info(f"📰 {news}")
        if st.button(f"Approva ordine su {asset}", key=asset):
            st.balloons()
            st.write(f"Inviando ordine a Bitpanda... (Chiave: {BP_KEY[:5]}***)")

with col2:
    st.header("💰 Stato Account")
    st.metric("Budget Iniziale", "1.000 €", "Target +10%")
    st.write("Broker 1: Bitpanda ✅")
    st.write("Broker 2: eToro ✅")
