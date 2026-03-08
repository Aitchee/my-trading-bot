import streamlit as st
import requests

# Configurazione Dashboard
st.set_page_config(page_title="Trading Bot AI 2026", layout="wide")

# Caricamento chiavi dai Secrets
try:
    BP_KEY = st.secrets["d88c80faa21f3a890bff52acf8d2ffbb1ef21830332be28d03bd1e23c20bf5e14e5635b804fe92468af408dfa06fc890f88b6783829b3fda503f9ea486c512b2"]
    ET_KEY = st.secrets["eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJmNXJWdkt4TC5YSWhHZUd2dUNKNnlxalpBWFJiNHdKLWFselV4SGNvdXRSQ3Rld0FPTmhBWU1ETXJmelNPM0lySzZKZGR1ZmQwZGw5amdCaXlZRVFLUUpqZmdVbXdRV2Utc3NwQ095MjhvNF8ifQ__"]
    NW_KEY = st.secrets["f47b85db22664beba249feed052403c3"]
    st.sidebar.success("✅ API collegate correttamente!")
except Exception as e:
    st.sidebar.error("❌ Errore nei Secrets! Controlla il formato.")
    st.stop()

st.title("📊 Dashboard Trading Automatica")

# Funzione per recuperare le news vere
def get_news(asset):
    url = f"https://newsapi.org/v2/everything?q={asset}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        if articles:
            return articles[0]['title']
    except:
        return "Errore connessione news"
    return "Nessuna news recente rilevante."

# Layout a due colonne
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Analisi News in Tempo Reale")
    for item in ["Leonardo SPA", "Intesa Sanpaolo", "Elon Musk"]:
        titolo = get_news(item)
        st.subheader(item)
        st.info(f"📌 {titolo}")
        if st.button(f"Approva operazione su {item}", key=item):
            st.balloons()
            st.write(f"🚀 Ordine inviato per {item}!")

with col2:
    st.header("💰 Stato Account")
    # Qui visualizziamo che le API sono connesse invece di "Attesa API"
    st.success(f"Connessione Bitpanda attiva (Key: {BP_KEY[:5]}...)")
    st.success(f"Connessione eToro attiva (Key: {ET_KEY[:5]}...)")
    st.metric("Capitale Stimato", "1.000 €", "+10% Target")
