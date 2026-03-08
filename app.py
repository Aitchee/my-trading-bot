import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Refresh ogni 10 secondi esatti
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10 * 1000, key="datarefresh")

st.set_page_config(page_title="Edoardo LIVE Terminal", layout="wide")

# --- FUNZIONE CONNESSIONE API ETORO ---
def get_etoro_real_data():
    api_key = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__")
    acc_id = st.secrets.get("EdoardoCegna984")
    
    if not api_key:
        # Fallback se la chiave non è ancora nei secrets
        return {"balance": 56.95, "assets": [{"name": "GOLD", "val": 56.43, "p": -0.91}]}
    
    # Tentativo di chiamata reale
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://api.etoro.com/v1/accounts/{acc_id}/positions"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        return r.json()
    except:
        return {"balance": 56.95, "assets": [{"name": "GOLD", "val": 56.43, "p": -0.91}]}

# --- LOGICA AI & NEWS ---
def get_market_intelligence(asset):
    news_key = st.secrets.get("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={asset}&apiKey={news_key}&language=en&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])[:5]
        analyzer = SentimentIntensityAnalyzer()
        score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in articles]) / len(articles) if articles else 0
        return score, articles
    except: return 0, []

# --- INTERFACCIA ---
col_assets, col_ai, col_news = st.columns([1, 1.2, 1])

# SINISTRA: I TUOI ASSET (Dati estratti dal PDF e API )
with col_assets:
    st.header("💰 I Miei Asset")
    data = get_etoro_real_data()
    st.metric("Saldo Totale", f"${data['balance']}")
    for asset in data.get('assets', []):
        st.metric(f"Position: {asset['name']}", f"${asset['val']}", f"{asset['p']}%")
    st.caption(f"Aggiornato alle: {datetime.now().strftime('%H:%M:%S')}")

# CENTRO: PAPABILI ACQUISTI (In base a News + Trend)
with col_ai:
    st.header("🎯 Papabili Acquisto")
    watch_list = ["Bitcoin", "S&P 500", "Gold", "NVIDIA"]
    for item in watch_list:
        score, _ = get_market_intelligence(item)
        with st.container():
            if score > 0.2:
                st.success(f"**{item}** - Segnale: ACQUISTA (Sent: {score:.2f})")
            elif score < -0.2:
                st.error(f"**{item}** - Segnale: VENDI (Sent: {score:.2f})")
            else:
                st.info(f"**{item}** - Segnale: ATTENDI (Sent: {score:.2f})")

# DESTRA: NEWS LIVE
with col_news:
    st.header("📰 News Feed")
    _, news = get_market_intelligence("market")
    for n in news[:6]:
        st.markdown(f"**{n['title']}**")
        st.caption(f"{n['source']['name']} | [Link]({n['url']})")
        st.divider()
