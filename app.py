import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE DASHBOARD ---
st.set_page_config(page_title="My AI Trading Bot 2026", layout="wide")
st.title("🤖 Dashboard Trading Automatico: eToro & Bitpanda")

# Qui caricheremo le tue chiavi in modo sicuro
# Per ora le simuliamo, poi ti spiego come inserirle nei "Secrets"
BITPANDA_API_KEY = st.sidebar.text_input("Bitpanda API Key", type="password")
ETORO_API_KEY = st.sidebar.text_input("eToro API Key", type="password")
NEWS_API_KEY = st.sidebar.text_input("NewsAPI Key", type="password")

# --- FUNZIONE ANALISI NEWS ---
def get_market_sentiment(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=it&sortBy=publishedAt"
    response = requests.get(url).json()
    articles = response.get('articles', [])
    
    # Logica semplificata: cerchiamo parole chiave "positive"
    positive_words = ['record', 'investimento', 'crescita', 'utile', 'accordo', 'rialzo']
    score = 0
    latest_news = ""
    
    if articles:
        latest_news = articles[0]['title']
        for word in positive_words:
            if word in latest_news.lower():
                score += 1
    return score, latest_news

# --- INTERFACCIA DASHBOARD ---
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Analisi Real-Time")
    asset_da_monitorare = ["Leonardo", "Intesa Sanpaolo", "Elon Musk"]
    
    for asset in asset_da_monitorare:
        score, news = get_market_sentiment(asset)
        st.subheader(f"Sentiment per: {asset}")
        if score > 0:
            st.success(f"POSITIVO (Score: {score})")
            st.write(f"Ultima news: {news}")
        else:
            st.info("Neutro / Nessuna news rilevante")

with col2:
    st.header("💰 Portafoglio Integrato")
    # Qui inseriremo le chiamate API per leggere i tuoi saldi reali
    st.write("Connessione a Bitpanda... Attesa API")
    st.write("Connessione a eToro... Attesa API")
    
    # Esempio di obiettivo rendimento
    st.metric(label="Rendimento Stimato Annuo", value="2.4%", delta="Target 10%")

# --- LOGICA DI TRADING (IL BOT) ---
if st.button("Avvia Bot di Trading"):
    st.warning("Il Bot è attivo e sta scansionando i mercati...")
    # Qui inseriremo la funzione che effettivamente compra/vende