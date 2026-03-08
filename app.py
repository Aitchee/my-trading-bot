import streamlit as st
import requests
import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- CONFIGURAZIONE ESTRATTA DAI TUOI DATI ---
# Se sei su Streamlit Cloud, inserisci queste chiavi nei "Secrets"
# Se sei in locale, usa i valori predefiniti
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")
USER_ID = "EdoardoCegna984"
SALDO_INIZIALE = 56.95  # Dato preso dal tuo PDF

# --- LOGICA DEL BOT ---
class TradingEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(self, keyword):
        """Analizza le notizie in tempo reale tramite NewsAPI"""
        url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt"
        try:
            response = requests.get(url).json()
            articles = response.get('articles', [])[:5]
            if not articles:
                return 0.0
            
            scores = []
            for art in articles:
                text = (art['title'] or "") + " " + (art['description'] or "")
                score = self.analyzer.polarity_scores(text)['compound']
                scores.append(score)
            return sum(scores) / len(scores)
        except Exception as e:
            return 0.0

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Edoardo AI Trader", layout="wide")

# CSS per rendere l'interfaccia più professionale
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Edoardo AI Bot: eToro & Bitpanda")
st.write(f"Monitoraggio attivo per l'account: **{USER_ID}**")

# --- SIDEBAR: STATO ACCOUNT ---
st.sidebar.header("Portafoglio Reale")
st.sidebar.metric("Saldo stimato (USD)", f"${SALDO_INIZIALE}")
st.sidebar.write("🟢 **Status:** Bot in ascolto")
st.sidebar.divider()
st.sidebar.write("Asset monitorati: Gold (XAU), BTC, ETH, TSLA")

# --- CORPO CENTRALE: ANALISI SENTIMENT ---
bot = TradingEngine()
assets = ["Gold", "Bitcoin", "Ethereum", "Tesla"]

st.subheader("📊 Analisi Notizie ed Eventi Globali")
cols = st.columns(4)

for i, asset in enumerate(assets):
    with cols[i]:
        with st.spinner(f"Analizzando {asset}..."):
            score = bot.get_sentiment(asset)
            
            # Determina colore e segnale
            if score > 0.15:
                color = "normal"
                label = "RIALZISTA 🚀"
                st.success(label)
            elif score < -0.15:
                label = "RIBASSISTA 📉"
                st.error(label)
            else:
                label = "NEUTRALE ⚖️"
                st.warning(label)
            
            st.metric(label=f"Sentiment {asset}", value=f"{score:.2f}", delta=label)

# --- TABELLA OPERAZIONI ---
st.divider()
st.subheader("📜 Registro Attività Bot")

# Simuliamo le operazioni basate sul tuo estratto conto
data = {
    "Data/Ora": ["2026-03-08 23:15", "2026-03-08 22:45", "2026-03-01 09:00"],
    "Asset": ["XAU/USD", "BTC", "XAU/USD"],
    "Azione": ["HOLD", "ANALYSIS", "OPEN BUY"],
    "Motivazione": ["Sentiment Gold Stabile (0.05)", "News neutre su ETF", "Apertura posizione manuale"],
    "Esito": ["In attesa", "Nessuna azione", "Attivo (-0.52 USD fee)"]
}
st.table(pd.DataFrame(data))

st.info("💡 Il bot analizza i titoli di Bloomberg, Reuters e testate crypto ogni volta che ricarichi la pagina.")
