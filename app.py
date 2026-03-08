import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE LIVE ---
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")
st_autorefresh(interval=10000, key="datarefresh") # Refresh 10 secondi

# Recupero variabili dai Secrets
# Usiamo nomi consistenti per evitare NameError
NEWS_TOKEN = st.secrets.get("NEWS_API_KEY", "").strip()
ETORO_TOKEN = st.secrets.get("ETORO_API_KEY", "").strip()

analyzer = SentimentIntensityAnalyzer()

# --- FUNZIONE SCOPERTA ACCOUNT & SALDO ---
def fetch_live_etoro():
    if not ETORO_TOKEN:
        return "CHIAVE_MANCANTE"

    headers = {
        "Authorization": f"Bearer {ETORO_TOKEN}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }

    try:
        # 1. Identifichiamo l'ID dell'utente dal Token (Auto-discovery)
        user_res = requests.get("https://api.etoro.com/v1/users/me", headers=headers, timeout=10)
        
        if user_res.status_code != 200:
            return f"Errore Auth: {user_res.status_code}"
        
        user_info = user_res.json()
        # Estraiamo l'ID numerico reale (cid)
        internal_id = user_info.get('cid') or user_info.get('accountID')
        
        # 2. Recuperiamo il saldo usando l'ID trovato
        balance_url = f"https://api.etoro.com/v1/accounts/{internal_id}/balance"
        bal_res = requests.get(balance_url, headers=headers, timeout=10)
        
        if bal_res.status_code == 200:
            return {
                "balance": bal_res.json().get('balance'),
                "id": internal_id,
                "user": user_info.get('username', 'Edoardo')
            }
        else:
            return f"Errore Saldo: {bal_res.status_code}"
            
    except Exception as e:
        return f"Errore Connessione: {str(e)}"

# --- ANALISI NEWS DINAMICA ---
def get_market_signals():
    if not NEWS_TOKEN:
        return [], []
    
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_TOKEN}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        
        # Asset da monitorare
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla", "Oil", "Apple"]
        signals = []
        
        for asset in watchlist:
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                signals.append({"asset": asset, "score": score, "news": relevant[0]['title']})
        
        return sorted(signals, key=lambda x: x['score'], reverse=True), articles
    except:
        return [], []

# --- INTERFACCIA DASHBOARD ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

# COLONNA 1: ASSET REALI (API ETORO)
with col_left:
    st.header("💰 Portafoglio eToro")
    result = fetch_live_etoro()
    
    if result == "CHIAVE_MANCANTE":
        st.error("Inserisci 'ETORO_API_KEY' nei Secrets di Streamlit.")
    elif isinstance(result, str):
        st.error(f"⚠️ {result}")
        st.info("Il bot sta tentando l'accesso IRL...")
    else:
        st.metric("Saldo Reale (USD)", f"${result['balance']}")
        st.caption(f"Account: {result['user']} | ID: {result['id']}")
        st.success("Connessione IRL: ATTIVA")

# COLONNA 2: SEGNALI AI (DINAMICI)
with col_mid:
    st.header("🎯 Papabili Acquisto")
    signals, raw_news = get_market_signals()
    
    if not signals:
        st.write("Scansione mercati in corso...")
    
    for s in signals:
        with st.container():
            if s['score'] > 0.15:
                st.success(f"**BUY {s['asset']}** (Sent: {s['score']:.2f})")
            elif s['score'] < -0.15:
                st.error(f"**SELL {s['asset']}** (Sent: {s['score']:.2f})")
            else:
                st.warning(f"**WAIT {s['asset']}** (Sent: {s['score']:.2f})")
            st.caption(f"News: {s['news'][:70]}...")
            st.divider()

# COLONNA 3: NEWS REALI
with col_right:
    st.header("📰 News Feed")
    if raw_news:
        for n in raw_news[:10]:
            st.markdown(f"**{n['source']['name']}**")
            st.write(f"[{n['title']}]({n['url']})")
            st.divider()
