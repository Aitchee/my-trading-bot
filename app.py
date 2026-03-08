import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh rapido (10s) per non perdere i movimenti di mercato
st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO AI BOT", layout="wide")

# --- CREDENZIALI ---
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

# --- 1. SCANNER WALLET REALE (IRL) ---
def get_bitpanda_assets():
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        r = requests.get(url, headers=headers, timeout=10).json()
        active_assets = []
        
        # Scansioniamo tutti i wallet (Fiat, Oro, Crypto)
        for item in r.get('data', []):
            attr = item.get('attributes', {})
            balance = float(attr.get('balance', 0))
            
            # Mostriamo solo quello che possiedi davvero
            if balance > 0:
                active_assets.append({
                    "symbol": attr.get('symbol'),
                    "name": attr.get('name'),
                    "balance": balance
                })
        return active_assets
    except Exception as e:
        return f"Errore Connessione: {str(e)}"

# --- 2. LOGICA SEGNALI AI ---
def get_ai_intelligence():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        articles = requests.get(url).json().get('articles', [])
        # Focus su Oro (XAU) e Bitcoin (BTC)
        watchlist = {"Gold": "XAU", "Bitcoin": "BTC"}
        signals = []
        for name, code in watchlist.items():
            rel = [a for a in articles if name.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                signals.append({"name": name, "code": code, "score": score, "headline": rel[0]['title']})
        return signals, articles
    except:
        return [], []

# --- INTERFACCIA DASHBOARD ---
st.title(f"🚀 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")

col_wallet, col_trading, col_news = st.columns([1, 1.2, 1])

with col_wallet:
    st.header("💰 Asset Bitpanda")
    assets = get_bitpanda_assets()
    
    if isinstance(assets, str):
        st.error(assets)
    elif not assets:
        st.info("Saldo 0.00 rilevato su tutti gli asset confermati.")
    else:
        for a in assets:
            st.metric(f"{a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Connessione API Bitpanda: ATTIVA")

with col_trading:
    st.header("🎯 Analisi & Operazioni")
    sigs, news_data = get_ai_intelligence()
    
    if not sigs:
        st.write("Scansione mercati... Attesa segnali forti.")
        
    for s in sigs:
        st.subheader(f"Asset: {s['name']}")
        if s['score'] > 0.15:
            st.success(f"📈 SEGNALE BUY ({s['score']:.2f})")
            # LOGICA ORDINE REALE (Sostituisci la print con la POST per comprare)
            if st.button(f"ESEGUI ORDINE {s['name']}"):
                st.info(f"Ordine di test per {s['code']} inviato ai server Bitpanda.")
        elif s['score'] < -0.15:
            st.error(f"📉 SEGNALE SELL ({s['score']:.2f})")
        else:
            st.warning("⚖️ ATTENDERE (Sentiment Neutro)")
        st.caption(f"News: {s['headline'][:70]}...")

with col_news:
    st.header("📰 News Feed")
    for n in news_data[:8]:
        st.write(f"**{n['source']['name']}**: {n['title']}")
        st.divider()
