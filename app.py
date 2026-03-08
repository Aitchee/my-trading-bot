import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh 10 secondi
st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO LIVE TERMINAL", layout="wide")

# Recupero Segreti
CID = st.secrets.get("ETORO_ACCOUNT_ID", "").strip()
TOKEN = st.secrets.get("ETORO_API_KEY", "").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "").strip()

analyzer = SentimentIntensityAnalyzer()

def fetch_etoro_data():
    if not TOKEN or not CID:
        return "CONFIG_MISSING"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }
    
    # Lista di possibili percorsi per stanare il 404
    endpoints = [
        f"https://api.etoro.com/v1/accounts/{CID}/positions", # Percorso standard
        f"https://api.etoro.com/v1/portfolio/{CID}/summary",   # Percorso portfolio
        "https://api.etoro.com/v1/metadata/users/me"           # Percorso auto-discovery
    ]
    
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return {"data": r.json(), "url_used": url.split('/')[-1]}
            elif r.status_code == 401:
                return "TOKEN_EXPIRED"
        except:
            continue
            
    return "NOT_FOUND_404"

def get_market_intelligence():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla"]
        sigs = []
        for asset in watchlist:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                sigs.append({"asset": asset, "score": score, "news": rel[0]['title']})
        return sigs, articles
    except:
        return [], []

# --- INTERFACCIA ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Portafoglio IRL")
    res = fetch_etoro_data()
    
    if res == "TOKEN_EXPIRED":
        st.error("❌ Token Scaduto (401). Rigeneralo.")
    elif res == "NOT_FOUND_404":
        st.error(f"❌ ID {CID} respinto (404).")
        st.info("Suggerimento: eToro potrebbe richiedere il tuo ID globale. Prova a cercare 'gcid' nel JSON e usa quello.")
    elif isinstance(res, dict):
        # Se abbiamo successo
        st.success(f"Connesso via {res['url_used']}!")
        # Parsing flessibile
        data = res['data']
        # Se è un bilancio
        if 'balance' in data:
            st.metric("Saldo Reale", f"${data['balance']}")
        # Se sono posizioni
        if 'Positions' in data:
            for p in data['Positions']:
                st.write(f"📦 Asset ID {p['InstrumentID']}: ${p['Amount']}")
    else:
        st.error("Errore generico di connessione.")

with c2:
    st.header("🎯 Analisi Papabili")
    sigs, news = get_market_intelligence()
    for s in sigs:
        if s['score'] > 0.1: st.success(f"**BUY {s['asset']}**")
        elif s['score'] < -0.1: st.error(f"**SELL {s['asset']}**")
        else: st.warning(f"**WAIT {s['asset']}**")

with c3:
    st.header("📰 News Feed")
    for n in news[:8]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
        st.divider()
