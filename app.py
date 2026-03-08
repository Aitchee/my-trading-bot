import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh automatico 10s
st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO AI BOT", layout="wide")

# --- CONFIGURAZIONE BITPANDA & NEWS ---
# Incolla la tua API KEY di Bitpanda nei Secrets (Profilo -> API)
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1")
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

# --- FUNZIONE BITPANDA (SALDO REALE) ---
def get_bitpanda_balance():
    if "IL_TUO_API_KEY" in BITPANDA_KEY: return None
    headers = {"X-API-KEY": BITPANDA_KEY}
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        r = requests.get(url, headers=headers)
        return r.json()
    except: return None

# --- ANALISI SENTIMENT ---
def get_trading_signals():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        articles = requests.get(url).json().get('articles', [])
        watchlist = ["Gold", "Bitcoin", "NVIDIA"]
        results = []
        for asset in watchlist:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                results.append({"name": asset, "score": score, "headline": rel[0]['title']})
        return results, articles
    except: return [], []

# --- INTERFACCIA ---
st.title(f"🤖 Bot Edoardo: Trading IRL - {datetime.now().strftime('%H:%M:%S')}")

col_wallet, col_logic, col_news = st.columns([1, 1.2, 1])

with col_wallet:
    st.header("🐼 Portafoglio Bitpanda")
    bp_data = get_bitpanda_balance()
    if bp_data:
        # Qui mostriamo i tuoi veri asset su Bitpanda
        st.success("Connessione Bitpanda: LIVE")
        # Logica di parsing del wallet Bitpanda...
    else:
        st.error("API Bitpanda non configurata.")
        st.info("💡 Usa Bitpanda per il trading automatico: eToro non permette l'accesso ai bot.")

with col_logic:
    st.header("🎯 Logica Decisionale")
    signals, news = get_trading_signals()
    for s in signals:
        st.subheader(f"Analisi {s['name']}")
        if s['score'] > 0.15:
            st.success(f"🚀 SEGNALE: BUY (Sent: {s['score']:.2f})")
            if st.button(f"Esegui Acquisto {s['name']} su Bitpanda"):
                st.write(f"Inviando ordine API a Bitpanda...")
        elif s['score'] < -0.15:
            st.error(f"📉 SEGNALE: SELL (Sent: {s['score']:.2f})")
        else:
            st.warning("⚖️ SEGNALE: HOLD / ATTENDI")
        st.caption(f"News: {s['headline'][:60]}...")

with col_news:
    st.header("📰 News Feed")
    for n in news[:8]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
        st.divider()

