import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# 1. SETUP UNICO (Niente doppioni)
st.set_page_config(page_title="EDOARDO PRO-BOT", layout="wide")
st_autorefresh(interval=10000, key="terminal_refresh_final")

# 2. RECUPERO SEGRETI
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

# 3. FUNZIONE ASSET CORAZZATA
def get_bitpanda_assets():
    if not BITPANDA_KEY:
        return "CONFIG_MISSING"
        
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se il server risponde male (es. 401, 403, 500)
        if response.status_code != 200:
            return f"Errore {response.status_code}: Verificare API Key e Permessi."
            
        # TENTATIVO DI PARSING SICURO
        try:
            json_data = response.json()
        except ValueError:
            return "Il server Bitpanda ha risposto con testo non valido (Non-JSON)."

        # VERIFICA STRUTTURA (Evita l'errore 'str' object has no attribute 'get')
        if isinstance(json_data, dict) and 'data' in json_data:
            active_assets = []
            for item in json_data['data']:
                if isinstance(item, dict):
                    attr = item.get('attributes', {})
                    balance = float(attr.get('balance', 0))
                    if balance > 0:
                        active_assets.append({
                            "symbol": attr.get('symbol'),
                            "name": attr.get('name'),
                            "balance": balance
                        })
            return active_assets
        else:
            return "Dati ricevuti ma formato non riconosciuto."
            
    except Exception as e:
        return f"Errore di rete/connessione: {str(e)}"

# --- LOGICA NEWS & INTERFACCIA ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")
c_wallet, c_trade, c_news = st.columns([1, 1.2, 1])

with c_wallet:
    st.header("💰 Portafoglio")
    assets = get_bitpanda_assets()
    
    if assets == "CONFIG_MISSING":
        st.error("Inserisci BITPANDA_API_KEY nei Secrets.")
    elif isinstance(assets, str):
        st.error(f"⚠️ {assets}")
    elif not assets:
        st.info("Connesso. Saldo 0.00 rilevato.")
    else:
        for a in assets:
            st.metric(f"{a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Bitpanda Online")

with c_trade:
    st.header("🎯 Analisi AI")
    # Logica semplice per non appesantire
    st.write("Scansione segnali in corso...")
    # Qui andrebbe la funzione get_market_sentiment() se vuoi rimetterla

with c_news:
    st.header("📰 News Feed")
    st.write("In attesa di dati live...")
