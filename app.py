import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & REFRESH
st.set_page_config(page_title="EDOARDO TERMINAL DEBUG", layout="wide")
st_autorefresh(interval=15000, key="debug_refresh_v9") # 15 secondi per non saturare

# 2. RECUPERO E PULIZIA (Trasparente)
RAW_KEY = st.secrets.get("BITPANDA_API_KEY", "CHIAVE_NON_TROVATA")
BITPANDA_KEY = RAW_KEY.strip().replace('"', '').replace("'", "")
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

# --- INTERFACCIA ---
st.title(f"🚀 TERMINALE DEBUG - {datetime.now().strftime('%H:%M:%S')}")

# SEZIONE DEBUG CHIAVE
with st.expander("🔍 DEBUG: Cosa sta leggendo il codice?", expanded=True):
    st.write("**Chiave rilevata nei Secrets (Grezza):**")
    st.code(f"[{RAW_KEY}]", language="text")
    st.write("**Chiave pulita inviata a Bitpanda:**")
    st.code(BITPANDA_KEY, language="text")
    st.write(f"Lunghezza: {len(BITPANDA_KEY)} caratteri")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("💰 Connessione Bitpanda")
    
    if not BITPANDA_KEY or BITPANDA_KEY == "CHIAVE_NON_TROVATA":
        st.error("Manca la chiave nei Secrets!")
    else:
        # TENTATIVO DI CONNESSIONE
        url = "https://api.bitpanda.com/v1/fiat-wallets"
        headers = {"X-API-KEY": BITPANDA_KEY, "Accept": "application/json"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            st.write(f"**Status Code:** {response.status_code}")
            
            # STAMPA TUTTO QUELLO CHE RICEVIAMO
            st.write("**Risposta Integrale dal Server:**")
            st.json(response.text) # Qui vedrai l'errore esatto se fallisce
            
            if response.status_code == 200:
                st.success("✅ CONNESSIONE RIUSCITA!")
                data = response.json().get('data', [])
                for item in data:
                    attr = item.get('attributes', {})
                    bal = float(attr.get('balance', 0))
                    if bal > 0:
                        st.metric(f"{attr.get('name')}", f"€ {bal:.2f}")
            elif response.status_code == 401:
                st.error("❌ 401: Accesso negato. La chiave non è valida per Bitpanda.")
        except Exception as e:
            st.error(f"Errore di rete: {str(e)}")

with col_right:
    st.header("🎯 Analisi News AI")
    try:
        n_url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
        articles = requests.get(n_url).json().get('articles', [])
        for asset in ["Gold", "Bitcoin"]:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = analyzer.polarity_scores(rel[0]['title'])['compound']
                if score > 0.1: st.success(f"BUY {asset}")
                elif score < -0.1: st.error(f"SELL {asset}")
                else: st.warning(f"WAIT {asset}")
    except:
        st.write("News offline.")
