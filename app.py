import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh 10 secondi
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")

# --- DIAGNOSTICA SECRETS ---
st.sidebar.header("🛠 Diagnostica Sistema")
check_news = "✅ Caricata" if "NEWS_API_KEY" in st.secrets else "❌ MANCANTE"
check_etoro = "✅ Caricata" if "ETORO_API_KEY" in st.secrets else "❌ MANCANTE"
check_id = "✅ Caricato" if "ETORO_ACCOUNT_ID" in st.secrets else "❌ MANCANTE"

st.sidebar.write(f"News API: {check_news}")
st.sidebar.write(f"eToro Key: {check_etoro}")
st.sidebar.write(f"Account ID: {check_id}")

# --- RECUPERO DATI (SOLO API) ---
def fetch_etoro_data():
    # Recupero diretto dai segreti
    key = st.secrets.get("ETORO_API_KEY")
    acc_id = st.secrets.get("ETORO_ACCOUNT_ID")
    
    if not key or not acc_id:
        return "ERROR_CONFIG"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }
    
    try:
        # Tentativo saldo
        url = f"https://api.etoro.com/v1/accounts/{acc_id}/balance"
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            return r.json()
        else:
            return f"ERRORE API: {r.status_code} - {r.text[:100]}"
    except Exception as e:
        return f"ERRORE RETE: {str(e)}"

# --- ANALISI NEWS DINAMICA ---
def analyze_market():
    news_key = st.secrets.get("NEWS_API_KEY")
    if not news_key: return [], []
    
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={news_key}&language=en"
    try:
        res = requests.get(url).json()
        articles = res.get('articles', [])
        analyzer = SentimentIntensityAnalyzer()
        
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla", "Oil"]
        signals = []
        for asset in watchlist:
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                signals.append({"asset": asset, "score": score, "news": relevant[0]['title']})
        return signals, articles
    except:
        return [], []

# --- LAYOUT DASHBOARD ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")

col1, col2, col3 = st.columns([1, 1.2, 1])

# COLONNA 1: ASSET REALI
with col1:
    st.header("💰 eToro IRL")
    res = fetch_etoro_data()
    
    if res == "ERROR_CONFIG":
        st.error("I Secrets non sono stati letti correttamente da Streamlit.")
    elif isinstance(res, str):
        st.error(f"Dati non ricevuti: {res}")
    else:
        st.metric("Saldo Reale (USD)", f"${res.get('balance', 'N/D')}")
        st.success("Connessione eToro Stabilita!")

# COLONNA 2: SEGNALI AI (CALCOLO DINAMICO)
with col2:
    st.header("🎯 Papabili Acquisto")
    signals, news_list = analyze_market()
    if not signals:
        st.info("Nessun trend rilevato nelle news recenti.")
    for s in signals:
        if s['score'] > 0.15:
            st.success(f"**BUY {s['asset']}** ({s['score']:.2f})")
        elif s['score'] < -0.15:
            st.error(f"**SELL {s['asset']}** ({s['score']:.2f})")
        else:
            st.warning(f"**WAIT {s['asset']}** ({s['score']:.2f})")
        st.caption(f"Headline: {s['news'][:60]}...")

# COLONNA 3: NEWS FEED
with col3:
    st.header("📰 News Stream")
    for n in news_list[:8]:
        st.markdown(f"**{n['source']['name']}**")
        st.write(f"[{n['title']}]({n['url']})")
        st.divider()
