import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE LIVE ---
# Aggiornamento automatico ogni 10 secondi
st_autorefresh(interval=10 * 1000, key="datarefresh")

st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# Recupero chiavi dai Secrets (Devi averle inserite su Streamlit Cloud)
ETORO_API_KEY = st.secrets.get("ETORO_API_KEY")
ETORO_ACCOUNT_ID = st.secrets.get("ETORO_ACCOUNT_ID", "EdoardoCegna984")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

# Inizializza analizzatore sentiment
analyzer = SentimentIntensityAnalyzer()

# --- FUNZIONI DI CALCOLO E API ---

def get_etoro_data():
    """Recupera saldo e posizioni reali da eToro"""
    if not ETORO_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {ETORO_API_KEY}", "Content-Type": "application/json"}
    try:
        # Nota: Questi sono gli endpoint standard eToro. Verifica se il tuo account usa v1 o v2
        base_url = f"https://api.etoro.com/v1/accounts/{ETORO_ACCOUNT_ID}"
        balance_res = requests.get(f"{base_url}/balance", headers=headers, timeout=5).json()
        pos_res = requests.get(f"{base_url}/positions", headers=headers, timeout=5).json()
        return {"balance": balance_res.get('balance'), "positions": pos_res.get('positions', [])}
    except:
        return None

def get_market_analysis():
    """Scansiona il mercato e calcola i 'Papabili' basandosi sulle news reali"""
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        
        # Lista di asset da monitorare dinamicamente
        assets_to_scan = ["Gold", "Bitcoin", "NVIDIA", "Tesla", "Ethereum", "Apple", "Amazon", "S&P 500"]
        results = []

        for asset in assets_to_scan:
            # Filtra le news che parlano dell'asset
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                # Calcolo matematico del sentiment
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                results.append({
                    "name": asset,
                    "score": score,
                    "news_count": len(relevant),
                    "headline": relevant[0]['title']
                })
        
        # Ordina per punteggio di sentiment (dal più positivo al più negativo)
        return sorted(results, key=lambda x: x['score'], reverse=True), articles
    except:
        return [], []

# --- INTERFACCIA DASHBOARD ---

st.title(f"🚀 EDOARDO AI TRADING TERMINAL - {datetime.now().strftime('%H:%M:%S')}")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

# --- COLONNA 1: I MIEI ASSET (LIVE API) ---
with col_left:
    st.subheader("💰 Portafoglio eToro")
    data = get_etoro_data()
    
    if data:
        st.metric("Saldo Netto", f"${data['balance']}")
        st.write("---")
        for pos in data['positions']:
            val = pos.get('currentValue', 0)
            perc = pos.get('profitPercentage', 0)
            st.metric(f"{pos.get('displaySymbol', 'Asset')}", f"${val}", f"{perc}%")
    else:
        st.warning("⚠️ Collegamento API eToro non rilevato.")
        st.info("Configura 'ETORO_API_KEY' nei Secrets per vedere i tuoi dati qui.")
        # Placeholder basato sull'ultimo PDF per non lasciare vuoto
        st.write("Ultimo dato PDF: **$56.95**")

# --- COLONNA 2: CALCOLO PAPABILI (NEWS VS TREND) ---
with col_mid:
    st.subheader("🎯 Analisi Papabili Acquisto")
    st.caption("Calcolo basato su Sentiment Analysis delle ultime 24h")
    
    papabili, all_news = get_market_intelligence = get_market_analysis()
    
    if not papabili:
        st.write("Ricerca trend in corso...")
    else:
        for p in papabili:
            with st.container():
                # Colore dinamico basato sul calcolo sentiment
                if p['score'] > 0.15:
                    st.success(f"**COMPRA {p['name']}** (Score: {p['score']:.2f})")
                elif p['score'] < -0.15:
                    st.error(f"**VENDI/EVITA {p['name']}** (Score: {p['score']:.2f})")
                else:
                    st.info(f"**ATTENDI {p['name']}** (Score: {p['score']:.2f})")
                st.caption(f"News rilevante: {p['headline'][:80]}...")
                st.write("---")

# --- COLONNA 3: NEWS REALI ---
with col_right:
    st.subheader("📰 Market News IRL")
    if all_news:
        for n in all_news[:8]:
            st.markdown(f"**{n['source']['name']}**")
            st.write(f"[{n['title']}]({n['url']})")
            st.caption(f"Pubblicato: {n['publishedAt']}")
            st.write("---")
    else:
        st.write("Nessuna news disponibile al momento.")

# --- STYLE ---
st.markdown("""
    <style>
    .stMetric { background-color: #1a1c23; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
