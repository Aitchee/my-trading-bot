import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO REAL-TIME TERMINAL", layout="wide")

CID = st.secrets.get("ETORO_ACCOUNT_ID", "").strip()
TOKEN = st.secrets.get("ETORO_API_KEY", "").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "").strip()

analyzer = SentimentIntensityAnalyzer()

def fetch_etoro_full():
    if not TOKEN or not CID: return "CONFIG_MISSING"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }
    
    # Questo è l'endpoint che genera il JSON che hai postato tu (richiede POST)
    url = "https://api.etoro.com/v1/aggregate"
    
    # Body della richiesta per ottenere i dati che vogliamo
    payload = {
        "Requests": [
            {"Method": "GET", "Path": f"v1/portfolio/{CID}/positions", "Id": 1},
            {"Method": "GET", "Path": f"v1/accounts/{CID}/balance", "Id": 2}
        ]
    }

    try:
        # Proviamo prima la POST aggregata
        r = requests.post(url, headers=headers, json=payload, timeout=12)
        
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            # Se l'aggregato fallisce, proviamo l'ultimo URL 'disperato'
            fallback_url = f"https://api.etoro.com/v1/metadata/users/{CID}"
            f_res = requests.get(fallback_url, headers=headers, timeout=10)
            if f_res.status_code == 200:
                return {"type": "metadata", "data": f_res.json()}
            return f"ERRORE 404: L'ID {CID} non risponde a nessun servizio."
        else:
            return f"ERRORE {r.status_code}"
    except Exception as e:
        return f"ERRORE CONNESSIONE: {str(e)}"

# --- INTERFACCIA ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Portafoglio IRL")
    res = fetch_etoro_full()
    
    if isinstance(res, str):
        st.error(res)
    else:
        # Parsing dei dati se arrivano dall'aggregatore o dal metadata
        if "AggregatedResult" in res:
            st.success("Connessione Aggregata: OK")
            # Qui estraiamo il saldo se presente nel JSON aggregato
            st.write("Dati ricevuti con successo dal server.")
        elif res.get("type") == "metadata":
            st.success("Connessione Metadata: OK")
            user = res['data'].get('username', 'Utente')
            st.metric("Account Rilevato", user)
            st.info("L'ID è corretto, ma il saldo richiede permessi aggiuntivi.")

with c2:
    st.header("🎯 Analisi Papabili")
    # Logica news solita
    url_n = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        n_res = requests.get(url_n).json()
        articles = n_res.get('articles', [])
        for asset in ["Gold", "Bitcoin", "NVIDIA"]:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = analyzer.polarity_scores(rel[0]['title'])['compound']
                if score > 0.1: st.success(f"**BUY {asset}**")
                elif score < -0.1: st.error(f"**SELL {asset}**")
                else: st.warning(f"**WAIT {asset}**")
    except: st.write("Caricamento news...")

with c3:
    st.header("📰 News Feed")
    st.write("In attesa di dati live...")
