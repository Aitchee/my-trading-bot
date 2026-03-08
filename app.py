import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh 10 secondi
st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")

# Recupero variabili
NEWS_TOKEN = st.secrets.get("NEWS_API_KEY", "").strip()
ETORO_TOKEN = st.secrets.get("ETORO_API_KEY", "").strip()
# Se hai trovato un numero ID nel tuo profilo eToro, mettilo nei Secrets come ETORO_ACCOUNT_ID
# Altrimenti il bot userà il tuo username "EdoardoCegna984"
USER_ID = st.secrets.get("ETORO_ACCOUNT_ID", "EdoardoCegna984").strip()

analyzer = SentimentIntensityAnalyzer()

def fetch_etoro_direct():
    if not ETORO_TOKEN: return "CHIAVE_MANCANTE"

    headers = {
        "Authorization": f"Bearer {ETORO_TOKEN}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }

    # Proviamo i due unici URL che possono funzionare senza /users/me
    urls = [
        f"https://api.etoro.com/v1/accounts/{USER_ID}/balance",
        f"https://api.etoro.com/v1/portfolio/{USER_ID}/summary"
    ]
    
    last_res = ""
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.json()
            last_res = f"Errore {r.status_code} su {url.split('/')[-2]}"
        except Exception as e:
            last_res = str(e)
    return last_res

def get_signals():
    if not NEWS_TOKEN: return [], []
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_TOKEN}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla"]
        signals = []
        for asset in watchlist:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                signals.append({"asset": asset, "score": score, "news": rel[0]['title']})
        return signals, articles
    except: return [], []

# --- INTERFACCIA ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")
c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Portafoglio IRL")
    res = fetch_etoro_direct()
    if isinstance(res, str):
        st.error(f"⚠️ {res}")
        st.info(f"Tentativo su ID: {USER_ID}")
    else:
        # Se l'API risponde (cerchiamo il campo balance o equity)
        saldo = res.get('balance') or res.get('totalEquity') or "N/D"
        st.metric("Saldo Reale", f"${saldo}")
        st.success("Connessione Stabilita!")

with c2:
    st.header("🎯 Papabili Acquisto")
    sigs, news = get_signals()
    for s in sigs:
        if s['score'] > 0.1: st.success(f"**BUY {s['asset']}**")
        elif s['score'] < -0.1: st.error(f"**SELL {s['asset']}**")
        else: st.warning(f"**WAIT {s['asset']}**")

with c3:
    st.header("📰 News Feed")
    for n in news[:8]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
