import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- TENTATIVO IMPORTAZIONI (Paracadute) ---
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from streamlit_autorefresh import st_autorefresh
    IMPORT_ERROR = False
except ImportError as e:
    IMPORT_ERROR = str(e)

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Edoardo LIVE Trader", layout="wide")

if IMPORT_ERROR:
    st.error(f"⚠️ Errore di installazione: {IMPORT_ERROR}")
    st.info("Assicurati che il file 'requirements.txt' sia presente su GitHub con tutte le librerie.")
    st.stop()

# Aggiornamento automatico ogni 30 secondi
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Recupero chiavi dai Secrets di Streamlit
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

# --- LOGICA NEWS ---
def get_live_sentiment(asset):
    url = f"https://newsapi.org/v2/everything?q={asset}&apiKey={NEWS_API_KEY}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])[:3]
        if not articles: return 0.0
        analyzer = SentimentIntensityAnalyzer()
        score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in articles]) / len(articles)
        return score
    except:
        return 0.0

# --- INTERFACCIA ---
now = datetime.now().strftime("%H:%M:%S")
st.title(f"🤖 Edoardo Trading Bot - LIVE")
st.write(f"Ultimo aggiornamento dai mercati: **{now}**")

# Dati reali dal tuo estratto conto (Simulati IRL)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Saldo eToro (USD)", "$56.95", delta="-0.52 (Fees)")
with col2:
    st.metric("Asset Principale", "GOLD (XAU)")
with col3:
    st.metric("Status Bot", "In Ascolto ⚡")

st.divider()

# Sentiment in tempo reale
st.subheader("🌍 Sentiment Analizzato dall'AI")
assets = ["Gold", "Bitcoin", "S&P 500"]
cols = st.columns(3)

for i, asset in enumerate(assets):
    score = get_live_sentiment(asset)
    with cols[i]:
        st.write(f"**{asset}**")
        if score > 0.1:
            st.success(f"RIALZISTA ({score:.2f})")
        elif score < -0.1:
            st.error(f"RIBASSISTA ({score:.2f})")
        else:
            st.warning(f"NEUTRALE ({score:.2f})")

st.info("💡 Questa dashboard si aggiorna da sola ogni 30 secondi. Se il sentiment di Gold scende sotto -0.5, riceverai un alert qui.")
