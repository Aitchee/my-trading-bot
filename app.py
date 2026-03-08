import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh 10 secondi per dati Live
st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO REAL-TIME TERMINAL", layout="wide")

# Recupero Segreti puliti
CID = st.secrets.get("ETORO_ACCOUNT_ID", "").strip()
TOKEN = st.secrets.get("ETORO_API_KEY", "").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "").strip()

analyzer = SentimentIntensityAnalyzer()

def fetch_etoro_portfolio():
    if not TOKEN or not CID:
        return "CONFIG_MISSING"

    # Headers ufficiali estratti dal tuo JSON
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }
    
    # Usiamo l'endpoint specifico per il Portfolio che abbiamo visto nel tuo JSON
    url = f"https://api.etoro.com/v1/portfolio/{CID}/positions"
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return "TOKEN_EXPIRED"
        elif response.status_code == 404:
            return "ID_NOT_FOUND"
        else:
            return f"ERRORE_{response.status_code}"
    except Exception as e:
        return f"CONNESSIONE_FALLITA: {str(e)}"

def get_market_signals():
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
st.title(f"🚀 EDOARDO TERMINAL LIVE - {datetime.now().strftime('%H:%M:%S')}")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Portafoglio Reale")
    data = fetch_etoro_portfolio()
    
    if isinstance(data, str):
        if data == "TOKEN_EXPIRED":
            st.error("❌ Token Scaduto. Prendi un nuovo 'ey...' dalla console di eToro.")
        elif data == "ID_NOT_FOUND":
            st.error(f"❌ ID {CID} non trovato. Verifica il numero CID.")
        else:
            st.error(f"❌ Errore: {data}")
    else:
        # Parsing delle posizioni reali dal tuo JSON
        positions = data.get('Positions', [])
        if not positions:
            st.info("Nessuna posizione aperta trovata.")
        for p in positions:
            # Sappiamo che InstrumentID 18 è GOLD dal tuo JSON
            asset_name = "GOLD (XAU/USD)" if p['InstrumentID'] == 18 else f"ID {p['InstrumentID']}"
            st.metric(f"{asset_name}", f"${p['Amount']}", f"Leva: {p['Leverage']}x")
            st.caption(f"Aperta il: {p['OpenDateTime'][:10]}")
        st.success(f"Connesso all'ID: {CID}")

with c2:
    st.header("🎯 Papabili Acquisto")
    sigs, news = get_market_signals()
    for s in sigs:
        if s['score'] > 0.1: st.success(f"**BUY {s['asset']}** (Sent: {s['score']:.2f})")
        elif s['score'] < -0.1: st.error(f"**SELL {s['asset']}** (Sent: {s['score']:.2f})")
        else: st.warning(f"**WAIT {s['asset']}**")
    if not sigs: st.write("Scansione mercati...")

with c3:
    st.header("📰 News Feed")
    for n in news[:8]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
        st.divider()
