import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh ogni 10 secondi per dati reali
st_autorefresh(interval=10 * 1000, key="datarefresh")

st.set_page_config(page_title="Edoardo LIVE Terminal", layout="wide")

# Recupero credenziali dai Secrets
ETORO_API_KEY = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__")
ETORO_ACCOUNT_ID = st.secrets.get("EdoardoCegna984")
NEWS_API_KEY = st.secrets.get("f47b85db22664beba249feed052403c3")

# --- CHIAMATA REALE ETORO ---
def get_etoro_live_data():
    if not ETORO_API_KEY or not ETORO_ACCOUNT_ID:
        return None
    
    headers = {"Authorization": f"Bearer {ETORO_API_KEY}", "Content-Type": "application/json"}
    # Endpoint per saldo e posizioni aperte
    url_balance = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}/balance"
    url_positions = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}/positions"
    
    try:
        # Recupero Saldo
        res_b = requests.get(url_balance, headers=headers, timeout=5).json()
        # Recupero Posizioni (es. il tuo Gold XAU/USD)
        res_p = requests.get(url_positions, headers=headers, timeout=5).json()
        return {"balance": res_b.get('balance'), "positions": res_p.get('positions', [])}
    except:
        return None

# --- ANALISI NEWS ---
def get_market_intelligence(asset):
    url = f"https://newsapi.org/v2/everything?q={asset}&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])[:5]
        analyzer = SentimentIntensityAnalyzer()
        score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in articles]) / len(articles) if articles else 0
        return score, articles
    except: return 0, []

# --- INTERFACCIA A TRE COLONNE ---
col_assets, col_ai, col_news = st.columns([1, 1.2, 1])

# COLONNA 1: I MIEI ASSET (Dati API)
with col_assets:
    st.header("💰 I Miei Asset")
    live_data = get_etoro_live_data()
    
    if live_data:
        st.metric("Saldo Totale LIVE", f"${live_data['balance']}")
        for pos in live_data['positions']:
            st.metric(f"{pos['displaySymbol']}", f"${pos['currentValue']}", f"{pos['profitPercentage']}%")
    else:
        st.error("API eToro non connessa. Controlla i Secrets.")
        # Visualizziamo l'ultimo dato noto solo come riferimento se l'API fallisce
        st.info(f"Ultimo dato registrato: $56.95") 

# COLONNA 2: PAPABILI ACQUISTO
with col_ai:
    st.header("🎯 Segnali Operativi")
    for asset in ["Bitcoin", "Gold", "NVIDIA"]:
        score, _ = get_market_intelligence(asset)
        st.write(f"**{asset}**")
        if score > 0.2: st.success(f"SENTIMENT: POSITIVO ({score:.2f})")
        elif score < -0.2: st.error(f"SENTIMENT: NEGATIVO ({score:.2f})")
        else: st.warning(f"SENTIMENT: NEUTRALE ({score:.2f})")

# COLONNA 3: NEWS FEED
with col_news:
    st.header("📰 News Feed")
    _, news = get_market_intelligence("market")
    for n in news:
        st.markdown(f"**{n['title']}**")
        st.caption(f"[Link alla notizia]({n['url']})")
