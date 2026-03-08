import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO AI BOT", layout="wide")

BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

def get_bitpanda_assets():
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se il server risponde con errore (es. 401, 403)
        if response.status_code != 200:
            return f"Errore Server Bitpanda: {response.status_code} - {response.text}"
            
        r = response.json()
        
        # Controllo se la struttura dati è quella attesa
        if not isinstance(r, dict) or 'data' not in r:
            return "Formato dati non riconosciuto."
            
        active_assets = []
        for item in r.get('data', []):
            attr = item.get('attributes', {})
            balance = float(attr.get('balance', 0))
            if balance > 0:
                active_assets.append({
                    "symbol": attr.get('symbol'),
                    "name": attr.get('name'),
                    "balance": balance
                })
        return active_assets
    except Exception as e:
        return f"Errore di Connessione: {str(e)}"

# --- RESTO DEL CODICE (Trading & News) ---
st.title(f"🚀 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")
col_wallet, col_trading, col_news = st.columns([1, 1.2, 1])

with col_wallet:
    st.header("💰 Asset Bitpanda")
    assets = get_bitpanda_assets()
    
    if isinstance(assets, str):
        st.error(assets)
        if "401" in assets:
            st.info("💡 Il codice 401 significa che la chiave API non è valida o non è stata confermata via email.")
    elif not assets:
        st.info("Saldo 0.00 rilevato. Il bot è connesso ma il portafoglio è vuoto.")
    else:
        for a in assets:
            st.metric(f"{a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Connessione Bitpanda: ATTIVA")

# (Il resto delle colonne col_trading e col_news rimane uguale a prima)import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO AI BOT", layout="wide")

BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

def get_bitpanda_assets():
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se il server risponde con errore (es. 401, 403)
        if response.status_code != 200:
            return f"Errore Server Bitpanda: {response.status_code} - {response.text}"
            
        r = response.json()
        
        # Controllo se la struttura dati è quella attesa
        if not isinstance(r, dict) or 'data' not in r:
            return "Formato dati non riconosciuto."
            
        active_assets = []
        for item in r.get('data', []):
            attr = item.get('attributes', {})
            balance = float(attr.get('balance', 0))
            if balance > 0:
                active_assets.append({
                    "symbol": attr.get('symbol'),
                    "name": attr.get('name'),
                    "balance": balance
                })
        return active_assets
    except Exception as e:
        return f"Errore di Connessione: {str(e)}"

# --- RESTO DEL CODICE (Trading & News) ---
st.title(f"🚀 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")
col_wallet, col_trading, col_news = st.columns([1, 1.2, 1])

with col_wallet:
    st.header("💰 Asset Bitpanda")
    assets = get_bitpanda_assets()
    
    if isinstance(assets, str):
        st.error(assets)
        if "401" in assets:
            st.info("💡 Il codice 401 significa che la chiave API non è valida o non è stata confermata via email.")
    elif not assets:
        st.info("Saldo 0.00 rilevato. Il bot è connesso ma il portafoglio è vuoto.")
    else:
        for a in assets:
            st.metric(f"{a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Connessione Bitpanda: ATTIVA")

# (Il resto delle colonne col_trading e col_news rimane uguale a prima)
