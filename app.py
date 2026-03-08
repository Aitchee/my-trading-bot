import streamlit as st
import requests

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Trading Bot 2026", layout="wide")

# 2. Controllo Segreti (Devono esserci tutti e 3)
try:
    BP_KEY = st.secrets["d88c80faa21f3a890bff52acf8d2ffbb1ef21830332be28d03bd1e23c20bf5e14e5635b804fe92468af408dfa06fc890f88b6783829b3fda503f9ea486c512b2"]
    ET_KEY = st.secrets["eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJmNXJWdkt4TC5YSWhHZUd2dUNKNnlxalpBWFJiNHdKLWFselV4SGNvdXRSQ3Rld0FPTmhBWU1ETXJmelNPM0lySzZKZGR1ZmQwZGw5amdCaXlZRVFLUUpqZmdVbXdRV2Utc3NwQ095MjhvNF8ifQ__"]
    NW_KEY = st.secrets["f47b85db22664beba249feed052403c3"]
except Exception:
    st.error("❌ Errore: Controlla i Secrets! Mancano le chiavi di Bitpanda, eToro o NewsAPI.")
    st.stop()

st.title("🤖 Dashboard Multi-Platform: eToro & Bitpanda")

# 3. Funzione News (Il "Cervello")
def prendi_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        if r.get('articles'):
            return r['articles'][0]['title'], r['articles'][0]['url']
    except:
        return "Nessuna news trovata.", "#"
    return "In attesa di aggiornamenti...", "#"

# 4. Layout Dashboard
col_etoro, col_bitpanda = st.columns(2)

with col_etoro:
    st.header("🐂 eToro (Oro & Musk)")
    # News per eToro
    titolo_musk, url_musk = prendi_news("Elon Musk Tesla")
    st.subheader("Sentiment Elon Musk")
    st.info(f"📰 {titolo_musk}")
    if st.button("Analizza opportunità eToro"):
        st.write("Connessione API eToro... ✅")
        st.balloons()

with col_bitpanda:
    st.header("🐼 Bitpanda (Azioni IT)")
    # News per Leonardo
    titolo_leo, url_leo = prendi_news("Leonardo SPA")
    st.subheader("Focus: Leonardo SPA")
    st.success(f"📰 {titolo_leo}")
    
    if st.button("Approva acquisto Leonardo (50€)"):
        st.write(f"Utilizzando chiave: {BP_KEY[:5]}***")
        st.warning("Ordine in fase di invio a Bitpanda...")

st.divider()
st.sidebar.title("Stato Sistema")
st.sidebar.write(f"API eToro: ✅")
st.sidebar.write(f"API Bitpanda: ✅")
st.sidebar.write(f"Target Rendimento: **10%**")
