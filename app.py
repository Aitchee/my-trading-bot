import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & REFRESH (10s)
st.set_page_config(page_title="EDOARDO AI TRADER", layout="wide")
st_autorefresh(interval=10000, key="auto_trade_refresh_v1")

# 2. RECUPERO CHIAVI
RAW_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1")
BITPANDA_KEY = "".join(RAW_KEY.split()).replace('"', '').replace("'", "")
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {
    "X-API-KEY": BITPANDA_KEY,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# --- FUNZIONE ESECUZIONE ORDINE REALE ---
def execute_trade(asset_code, amount_eur):
    url = "https://api.bitpanda.com/v1/trades"
    payload = {
        "asset_code": asset_code,
        "amount": amount_eur,
        "type": "buy",
        "currency_code": "EUR"
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 201 or r.status_code == 200:
            return f"✅ ORDINE ESEGUITO: {amount_eur}€ su {asset_code}"
        else:
            return f"❌ ERRORE ORDINE: {r.status_code} - {r.text[:100]}"
    except Exception as e:
        return f"❌ ERRORE RETE: {str(e)}"

# --- FUNZIONE RECUPERO ASSET ---
def fetch_wallets():
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', [])
        return f"Status {r.status_code}"
    except: return "Error"

# --- DASHBOARD ---
st.title(f"🤖 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")

c_wallet, c_trade, c_news = st.columns([1, 1.2, 1])

with c_wallet:
    st.header("💰 Portafoglio")
    data = fetch_wallets()
    if isinstance(data, list):
        for item in data:
            attr = item.get('attributes', {})
            val = float(attr.get('balance', 0))
            if val > 0:
                st.metric(f"{attr.get('name')}", f"{val:.4f} {attr.get('symbol')}")
        st.success("Bitpanda Online")
    else:
        st.error(f"Connessione: {data}")

with c_trade:
    st.header("🎯 Trading Logic")
    # Analisi Sentiment per Gold
    try:
        n_url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
        articles = requests.get(n_url).json().get('articles', [])
        
        # Focus Gold (XAU)
        gold_news = [a for a in articles if "gold" in (a['title'] or "").lower()]
        if gold_news:
            score = analyzer.polarity_scores(gold_news[0]['title'])['compound']
            st.write(f"**Sentiment Gold:** {score:.2f}")
            
            # --- LOGICA AUTOMATICA ---
            if score >= 0.40:
                st.success("🚀 SEGNALE FORTE RILEVATO: BUY")
                # Evita acquisti multipli infiniti nella stessa sessione
                if 'last_trade' not in st.session_state or st.session_state.last_trade != gold_news[0]['title']:
                    with st.spinner("Eseguendo acquisto automatico..."):
                        result = execute_trade("XAU", 25.0) # Compra 25€ di Oro
                        st.balloons()
                        st.warning(result)
                        st.session_state.last_trade = gold_news[0]['title']
                else:
                    st.info("Ordine già eseguito per questa notizia.")
            elif score <= -0.40:
                st.error("📉 SEGNALE VENDITA RILEVATO")
            else:
                st.warning("⚖️ Sentiment Neutro. Nessuna azione.")
    except: st.write("Analisi flussi...")

with c_news:
    st.header("📰 News")
    # (News feed solito qui...)
