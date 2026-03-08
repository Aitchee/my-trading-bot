import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE LIVE ---
st.set_page_config(page_title="EDOARDO REAL-TIME TERMINAL", layout="wide")
st_autorefresh(interval=10000, key="datarefresh") # 10 secondi secchi

# Recupero chiavi dai Secrets (OBBLIGATORI)
ETORO_API_KEY = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__", "")
ETORO_ACCOUNT_ID = st.secrets.get("ETORO_ACCOUNT_ID", "EdoardoCegna984")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

# --- COMUNICAZIONE REALE ETORO ---
def fetch_etoro_live():
    if not ETORO_API_KEY or not ETORO_ACCOUNT_ID:
        return "ERRORE: Chiavi API non configurate nei Secrets."
    
    headers = {
        "Authorization": f"Bearer {ETORO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Endpoint eToro per posizioni e saldo
    url_p = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}/positions"
    url_b = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}/balance"
    
    try:
        # Richiesta Saldo
        res_b = requests.get(url_b, headers=headers, timeout=8)
        # Richiesta Posizioni
        res_p = requests.get(url_p, headers=headers, timeout=8)
        
        if res_b.status_code == 200 and res_p.status_code == 200:
            return {
                "balance": res_b.json().get('balance'),
                "positions": res_p.json().get('positions', [])
            }
        else:
            return f"ERRORE API ETORO: Status {res_b.status_code}. Controlla la validità della chiave."
    except Exception as e:
        return f"ERRORE CONNESSIONE: Impossibile raggiungere i server eToro ({str(e)})"

# --- CALCOLO DINAMICO PAPABILI ---
def get_dynamic_signals():
    # Prende le news business dell'ultimo minuto
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}&language=en"
    try:
        r = requests.get(url, timeout=5).json()
        articles = r.get('articles', [])
        
        # Scannerizziamo i titoli per trovare asset citati
        watchlist = ["Bitcoin", "Gold", "NVIDIA", "Tesla", "Oil", "Apple", "Ethereum"]
        found_signals = []
        
        for asset in watchlist:
            relevant = [a['title'] for a in articles if asset.lower() in a['title'].lower()]
            if relevant:
                # Calcolo sentiment matematico
                avg_score = sum([analyzer.polarity_scores(t)['compound'] for t in relevant]) / len(relevant)
                found_signals.append({"name": asset, "score": avg_score, "news": relevant[0]})
        
        return sorted(found_signals, key=lambda x: x['score'], reverse=True), articles
    except:
        return [], []

# --- INTERFACCIA ---
st.title(f"📊 TERMINAL EDOARDO - LIVE {datetime.now().strftime('%H:%M:%S')}")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

# COLONNA 1: I MIEI ASSET (SOLO API)
with col_left:
    st.header("💰 eToro Live Data")
    data = fetch_etoro_live()
    
    if isinstance(data, str):
        st.error(data) # Qui vedrai l'errore se l'API non risponde
    else:
        st.metric("Saldo Attuale (API)", f"${data['balance']}")
        if not data['positions']:
            st.info("Nessuna posizione aperta rilevata dalle API.")
        for p in data['positions']:
            st.metric(f"{p['displaySymbol']}", f"${p['currentValue']}", f"{p['profitPercentage']}%")

# COLONNA 2: CALCOLO PAPABILI (MATEMATICO)
with col_mid:
    st.header("🎯 Segnali AI Dinamici")
    signals, raw_news = get_dynamic_signals()
    
    if not signals:
        st.write("Scansione titoli in corso... Nessun trend forte rilevato.")
    else:
        for s in signals:
            if s['score'] > 0.15:
                st.success(f"**BUY {s['name']}**")
                st.caption(f"Sentiment: {s['score']:.2f}")
            elif s['score'] < -0.15:
                st.error(f"**SELL {s['name']}**")
                st.caption(f"Sentiment: {s['score']:.2f}")
            else:
                st.warning(f"**WAIT {s['name']}**")
            st.write(f"News: {s['news'][:60]}...")
            st.divider()

# COLONNA 3: NEWS REALI
with col_right:
    st.header("📰 News Stream")
    if raw_news:
        for n in raw_news[:10]:
            st.markdown(f"**{n['source']['name']}**")
            st.write(f"[{n['title']}]({n['url']})")
            st.divider()

st.markdown("<style>.stMetric { background-color: #0e1117; border: 1px solid #30363d; padding: 10px; }</style>", unsafe_allow_html=True)
