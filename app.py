import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")
st_autorefresh(interval=10 * 1000, key="datarefresh") # Refresh 10s

# RECUPERO SEGRETI
ETORO_API_KEY = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__")
ETORO_ACCOUNT_ID = st.secrets.get("EdoardoCegna984")
NEWS_API_KEY = st.secrets.get("f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

# --- MODULO 1: ASSET REALI (API eToro) ---
def get_etoro_real_time():
    if not ETORO_API_KEY or not ETORO_ACCOUNT_ID:
        return None
    headers = {"Authorization": f"Bearer {ETORO_API_KEY}"}
    try:
        # Chiamate reali ai server eToro
        b_res = requests.get(f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}/balance", headers=headers, timeout=5).json()
        p_res = requests.get(f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}/positions", headers=headers, timeout=5).json()
        return {"balance": b_res.get('balance'), "positions": p_res.get('positions', [])}
    except:
        return None

# --- MODULO 2: ANALISI DINAMICA MERCATO (AI) ---
def analyze_market_dynamics():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}&language=en"
    try:
        articles = requests.get(url).json().get('articles', [])
        # Identifichiamo asset comuni nei titoli per non essere statici
        potential_assets = ["Gold", "Bitcoin", "Oil", "Tesla", "Apple", "NVIDIA", "Amazon", "Microsoft"]
        dynamic_signals = []
        
        for asset in potential_assets:
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                sentiment_avg = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                dynamic_signals.append({
                    "asset": asset,
                    "sentiment": sentiment_avg,
                    "volume": len(relevant),
                    "latest": relevant[0]['title']
                })
        return sorted(dynamic_signals, key=lambda x: x['sentiment'], reverse=True), articles
    except:
        return [], []

# --- DASHBOARD LAYOUT ---
st.title(f"🚀 EDOARDO AI TERMINAL - {datetime.now().strftime('%H:%M:%S')}")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

# SINISTRA: I TUOI ASSET IRL
with col_left:
    st.header("💰 Portafoglio eToro")
    et_data = get_etoro_real_time()
    if et_data:
        st.metric("Saldo Netto Reale", f"${et_data['balance']}")
        for pos in et_data['positions']:
            st.metric(f"{pos['displaySymbol']}", f"${pos['currentValue']}", f"{pos['profitPercentage']}%")
    else:
        st.error("API eToro non collegata.")
        st.info("Inserisci ETORO_API_KEY nei Secrets.")

# CENTRO: PAPABILI (CALCOLO AI)
with col_mid:
    st.header("🎯 Papabili Acquisto")
    signals, all_news = analyze_market_dynamics()
    if not signals:
        st.write("Nessun trend forte rilevato nelle news dell'ultima ora.")
    else:
        for s in signals:
            score = s['sentiment']
            if score > 0.15:
                st.success(f"**BUY {s['asset']}** (Sentiment: {score:.2f})")
            elif score < -0.15:
                st.error(f"**SELL/AVOID {s['asset']}** (Sentiment: {score:.2f})")
            else:
                st.info(f"**WAIT {s['asset']}** (Sentiment: {score:.2f})")
            st.caption(f"News: {s['latest'][:70]}...")

# DESTRA: NEWS FEED
with col_right:
    st.header("📰 News Live")
    for n in all_news[:10]:
        st.markdown(f"**{n['source']['name']}**")
        st.write(f"[{n['title']}]({n['url']})")
        st.divider()
