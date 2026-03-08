import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE E REFRESH IRL ---
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")
# Refresh automatico dell'interfaccia ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="datarefresh")

# Recupero Credenziali dai Secrets di Streamlit
ETORO_API_KEY = st.secrets.get("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__", "")
ETORO_ACCOUNT_ID = st.secrets.get("ETORO_ACCOUNT_ID", "EdoardoCegna984")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

# --- FUNZIONI API CON CACHE (Per evitare errori di timeout) ---

@st.cache_data(ttl=60) # Aggiorna i dati finanziari ogni minuto
def get_etoro_live():
    if not ETORO_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {ETORO_API_KEY}"}
    try:
        # Nota: Questi URL sono esemplificativi della struttura API eToro
        base_url = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}"
        balance = requests.get(f"{base_url}/balance", headers=headers, timeout=5).json()
        positions = requests.get(f"{base_url}/positions", headers=headers, timeout=5).json()
        return {"saldo": balance.get('balance'), "posizioni": positions.get('positions', [])}
    except:
        return None

@st.cache_data(ttl=300) # Analisi News ogni 5 minuti
def get_market_sentiment():
    # Analisi dinamica basata su news reali
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url, timeout=5).json().get('articles', [])
        assets = ["Gold", "Bitcoin", "NVIDIA", "Tesla", "S&P 500"]
        scored_assets = []
        for asset in assets:
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                scored_assets.append({"name": asset, "score": score, "news": relevant[0]['title']})
        return scored_assets, articles
    except:
        return [], []

# --- LAYOUT DASHBOARD A TRE COLONNE ---
st.title(f"🚀 EDOARDO AI TERMINAL - {datetime.now().strftime('%H:%M:%S')}")

col_assets, col_ai, col_news = st.columns([1, 1.2, 1])

# SINISTRA: I MIEI ASSET (Dati estratti dal tuo account)
with col_assets:
    st.header("💰 I Miei Asset")
    live_data = get_etoro_live()
    
    if live_data:
        st.metric("Saldo Netto LIVE", f"${live_data['saldo']}")
        for p in live_data['posizioni']:
            st.metric(f"{p['displaySymbol']}", f"${p['currentValue']}", f"{p['profitPercentage']}%")
    else:
        st.error("Connessione API eToro assente")
        st.info("Visualizzazione ultimi dati estratti:")
        # Dati reali dal tuo estratto conto 
        st.metric("Patrimonio Realizzato Finale", "$56.95", "-0.52 Fees") 
        st.write("**Posizione Attiva:** Gold (XAU/USD)")
        st.caption("ID Posizione: 3348402212")

# CENTRO: PAPABILI ACQUISTO (Calcolo dinamico News)
with col_ai:
    st.header("🎯 Papabili Acquisto")
    papabili, all_news = get_market_sentiment()
    
    if not papabili:
        st.write("Analisi flussi di mercato in corso...")
    else:
        for p in papabili:
            with st.container():
                # Logica di colore basata sul sentiment reale
                if p['score'] > 0.15:
                    st.success(f"**COMPRA {p['name']}** (Sentiment: {p['score']:.2f})")
                elif p['score'] < -0.15:
                    st.error(f"**EVITA {p['name']}** (Sentiment: {p['score']:.2f})")
                else:
                    st.warning(f"**ATTENDI {p['name']}** (Sentiment: {p['score']:.2f})")
                st.caption(f"News: {p['news'][:70]}...")
                st.write("---")

# DESTRA: NEWS FEED LIVE
with col_news:
    st.header("📰 News Feed IRL")
    if all_news:
        for n in all_news[:8]:
            st.markdown(f"**{n['source']['name']}**")
            st.write(f"[{n['title']}]({n['url']})")
            st.divider()
