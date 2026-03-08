import streamlit as st
import requests

st.set_page_config(page_title="Trading Bot Debug", layout="wide")
st.title("🤖 Verifica Connessione Bot")

# --- 1. DEBUG: VEDIAMO COSA LEGGE IL SISTEMA ---
st.subheader("Stato dei Secrets")
nomi_trovati = list(st.secrets.keys())

if not nomi_trovati:
    st.error("❌ Il sistema non legge alcun nome nei Secrets. Controlla il box su Streamlit.")
else:
    st.success(f"✅ Nomi rilevati nei Secrets: {', '.join(nomi_trovati)}")

# --- 2. RECUPERO CHIAVI (FLESSIBILE) ---
# Cerchiamo le chiavi sia in maiuscolo che in minuscolo per sicurezza
BP_KEY = st.secrets.get("d88c80faa21f3a890bff52acf8d2ffbb1ef21830332be28d03bd1e23c20bf5e14e5635b804fe92468af408dfa06fc890f88b6783829b3fda503f9ea486c512b2") or st.secrets.get("d88c80faa21f3a890bff52acf8d2ffbb1ef21830332be28d03bd1e23c20bf5e14e5635b804fe92468af408dfa06fc890f88b6783829b3fda503f9ea486c512b2")
ET_KEY = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJmNXJWdkt4TC5YSWhHZUd2dUNKNnlxalpBWFJiNHdKLWFselV4SGNvdXRSQ3Rld0FPTmhBWU1ETXJmelNPM0lySzZKZGR1ZmQwZGw5amdCaXlZRVFLUUpqZmdVbXdRV2Utc3NwQ095MjhvNF8ifQ__") or st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJmNXJWdkt4TC5YSWhHZUd2dUNKNnlxalpBWFJiNHdKLWFselV4SGNvdXRSQ3Rld0FPTmhBWU1ETXJmelNPM0lySzZKZGR1ZmQwZGw5amdCaXlZRVFLUUpqZmdVbXdRV2Utc3NwQ095MjhvNF8ifQ__")
NW_KEY = st.secrets.get("f47b85db22664beba249feed052403c3") or st.secrets.get("f47b85db22664beba249feed052403c3")

if None in [BP_KEY, ET_KEY, NW_KEY]:
    st.warning("⚠️ Una o più chiavi mancano. Assicurati che i nomi nei Secrets siano IDENTICI a quelli nel codice.")
    st.stop()

# --- 3. TEST NEWS (Se le chiavi ci sono) ---
st.divider()
st.header("📰 News in Tempo Reale")

def test_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NW_KEY}&language=it"
    try:
        r = requests.get(url).json()
        return r['articles'][0]['title']
    except:
        return "Errore nella chiamata API News. Verifica la tua NewsAPI Key."

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Leonardo SPA:** {test_news('Leonardo SPA')}")
with col2:
    st.write(f"**Intesa Sanpaolo:** {test_news('Intesa Sanpaolo')}")

st.sidebar.write("✅ Bot Online")
