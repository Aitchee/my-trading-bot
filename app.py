import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")

# Refresh grafico ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="datarefresh")

# Recupero credenziali dai Secrets
ETORO_API_KEY = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__", "")
ETORO_ACCOUNT_ID = st.secrets.get("ETORO_ACCOUNT_ID", "EdoardoCegna984")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

# --- FUNZIONI CON CACHE (Per evitare l'errore 1ST) ---
@st.cache_data(ttl=60) # Aggiorna i dati reali ogni 60 secondi, non ogni 10
def get_etoro_data():
    if not ETORO_API_KEY: return None
    headers = {"Authorization": f"Bearer {ETORO_API_KEY}", "Content-Type": "application/json"}
    try:
        # Endpoint simulati per la struttura, sostituisci con quelli forniti dalla tua documentazione eToro
        base_url = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}"
        b_res = requests.get(f"{base_url}/balance", headers=headers, timeout=5).json()
        p_res = requests.get(f"{base_url}/positions", headers=headers, timeout=5).json()
        return {"balance": b_res.get('balance', 56.95), "positions": p_res.get('positions', [])}
    except:
        return None

@st.cache_data(ttl=300) # Le news cambiano meno spesso, aggiorna ogni 5 minuti
def get_dynamic_analysis():
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=5).json()
        articles = r.get('articles', [])
        assets = ["Gold", "Bitcoin", "NVIDIA", "Tesla", "Ethereum", "Apple", "Amazon"]
        results = []
        for asset in assets:
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                results.append({"name": asset, "score": score, "headline": relevant[0]['title']})
        return sorted(results, key=lambda x: x['score'], reverse=True), articles
    except:
        return [], []

# --- LAYOUT DASHBOARD ---
st.title(f"🚀 EDOARDO AI TERMINAL - {datetime.now().strftime('%H:%M:%S')}")

c_left, c_mid, c_right = st.columns([1, 1.2, 1])

# COLONNA 1: I MIEI ASSET (IRL)
with c_left:
    st.subheader("💰 Asset eToro")
    data = get_etoro_data()
    if data:
        st.metric("Saldo Netto", f"${data['balance']}")
        for pos in data['positions']:
            st.metric(f"{pos.get('displaySymbol')}", f"${pos.get('currentValue')}", f"{pos.get('profitPercentage')}%")
    else:
        st.error("Connessione API eToro assente")
        st.info("Utilizzo dati ultimo estratto conto:")
        st.metric("Saldo Finale (PDF)", "$56.95", "-0.52 Fees")
        st.write("**Posizione attiva:** Gold (XAU/USD)")

# COLONNA 2: ANALISI DINAMICA (PAPABILI)
with c_mid:
    st.subheader("🎯 Papabili Acquisto")
    papabili, all_news = get_dynamic_analysis()
    if not papabili:
        st.write("Analisi flussi di mercato in corso...")
    else:
        for p in papabili:
            with st.container():
                if p['score'] > 0.15:
                    st.success(f"**BUY {p['name']}** (Score: {p['score']:.2f})")
                elif p['score'] < -0.15:
                    st.error(f"**AVOID {p['name']}** (Score: {p['score']:.2f})")
                else:
                    st.info(f"**WAIT {p['name']}** (Score: {p['score']:.2f})")
                st.caption(f"News: {p['headline'][:60]}...")
                st.write("---")

# COLONNA 3: NEWS REALI
with c_right:
    st.subheader("📰 News IRL")
    if all_news:
        for n in all_news[:8]:
            st.markdown(f"**{n['source']['name']}**")
            st.write(f"[{n['title']}]({n['url']})")
            st.write("---")
    else:
        st.write("In attesa di dati da NewsAPI...")

# --- CSS ---
st.markdown("<style>.stMetric { background-color: #1a1c23; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)
