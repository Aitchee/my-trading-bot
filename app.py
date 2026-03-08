import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Trading Bot PRO", layout="wide")

# --- RECUPERO CHIAVI ---
BP_KEY = st.secrets["BITPANDA_API_KEY"]
NW_KEY = st.secrets["NEWS_API_KEY"]

# --- FUNZIONE ANALISI SENTIMENT ---
def analizza_opportunita(asset):
    url = f"https://newsapi.org/v2/everything?q={asset}&apiKey={NW_KEY}&language=it"
    try:
        r = requests.get(url).json()
        news = r['articles'][0]['title'] if r['articles'] else "Nessuna news"
        # Simulazione logica AI: se la news contiene parole chiave positive
        score = 0.9 if any(word in news.lower() for word in ["record", "rialzo", "accordo", "utile"]) else 0.5
        return news, score
    except:
        return "Connessione news assente", 0.0

# --- LAYOUT A 3 COLONNE ---
col_news, col_segnali, col_grafici = st.columns([1, 1, 1.5])

with col_news:
    st.header("📰 Breaking News")
    for a in ["Mercati", "Borsa Italiana", "Fed"]:
        titolo, _ = analizza_opportunita(a)
        st.caption(f"🔥 {titolo}")

with col_segnali:
    st.header("🎯 Segnali AI")
    assets = ["Leonardo SPA", "Intesa Sanpaolo", "Bitcoin", "Oro", "Apple"]
    for a in assets:
        txt, score = analizza_opportunita(a)
        if score > 0.8:
            st.success(f"🟢 BUY: {a}")
            # --- QUI SCATTA L'AUTOMAZIONE ---
            # if auto_trade: esegui_ordine(a)
        else:
            st.warning(f"🟡 HOLD: {a}")

with col_grafici:
    st.header("📊 Grafici Real-Time")
    # Inseriamo un grafico interattivo (Widget TradingView)
    st.components.v1.html("""
        <div class="tradingview-widget-container">
            <div id="tradingview_12345"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({
              "width": "100%", "height": 400, "symbol": "BITPANDA:LDO",
              "interval": "D", "timezone": "Etc/UTC", "theme": "light", "style": "1"
            });
            </script>
        </div>
    """, height=450)

# --- SIDEBAR: CONTROLLO PILOTA AUTOMATICO ---
st.sidebar.header("⚙️ Impostazioni Bot")
auto_mode = st.sidebar.toggle("Attiva Pilota Automatico", value=False)
if auto_mode:
    st.sidebar.info("🤖 Bot in modalità operativa: Cercherà opportunità e comprerà da solo.")
