import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Refresh ogni 10 secondi per i prezzi e i segnali
st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO PRO-TRADER", layout="wide")

# --- CREDENZIALI ---
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

# --- 1. RECUPERO WALLET REALE ---
def get_balance():
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        r = requests.get(url, headers=headers).json()
        wallets = []
        # Estraiamo Fiat (Euro) e Asset (Oro/BTC)
        for w in r.get('data', []):
            attributes = w.get('attributes', {})
            if float(attributes.get('balance', 0)) > 0:
                wallets.append({
                    "name": attributes.get('name'),
                    "symbol": attributes.get('symbol'),
                    "balance": attributes.get('balance')
                })
        return wallets
    except: return []

# --- 2. LOGICA DI ESECUZIONE ORDINE (IL "TRADING") ---
def execute_trade(asset_code, amount, side="buy"):
    """
    ATTENZIONE: Questa funzione invia un ordine REALE a Bitpanda.
    Asset_code es: 'XAU' (Oro), 'BTC' (Bitcoin)
    """
    url = "https://api.bitpanda.com/v1/trades"
    payload = {
        "asset_code": asset_code,
        "amount": amount,
        "type": side, # 'buy' o 'sell'
        "currency_code": "EUR"
    }
    # Per sicurezza, in questa fase stampiamo solo l'intenzione. 
    # Per attivare l'acquisto reale, scommenta la riga sotto:
    # r = requests.post(url, headers=headers, json=payload)
    return f"SIMULAZIONE: Ordine {side} di {amount}€ su {asset_code} inviato."

# --- 3. ANALISI SENTIMENT NEWS ---
def get_signals():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        articles = requests.get(url).json().get('articles', [])
        watchlist = {"Gold": "XAU", "Bitcoin": "BTC", "NVIDIA": "NVDA"}
        found = []
        for name, code in watchlist.items():
            rel = [a for a in articles if name.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                found.append({"name": name, "code": code, "score": score, "news": rel[0]['title']})
        return found, articles
    except: return [], []

# --- INTERFACCIA DASHBOARD ---
st.title(f"📈 TERMINALE EDOARDO: BITPANDA LIVE")
st.write(f"Ultimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}")

col_w, col_t, col_n = st.columns([1, 1.2, 1])

with col_w:
    st.header("💰 Il Tuo Wallet")
    my_assets = get_balance()
    if my_assets:
        for a in my_assets:
            st.metric(f"{a['name']} ({a['symbol']})", f"{float(a['balance']):.4f}")
    else:
        st.warning("Nessun asset trovato o API limitata.")

with col_t:
    st.header("🎯 Analisi & Trading")
    sigs, news = get_signals()
    for s in sigs:
        st.subheader(f"Mercato: {s['name']}")
        # Visualizzazione Segnale
        if s['score'] > 0.15:
            st.success(f"🚀 BUY SIGNAL ({s['score']:.2f})")
            # Tasto per eseguire l'operazione
            if st.button(f"COMPRA {s['name']} (10€)"):
                msg = execute_trade(s['code'], 10, "buy")
                st.info(msg)
        elif s['score'] < -0.15:
            st.error(f"📉 SELL SIGNAL ({s['score']:.2f})")
            if st.button(f"VENDI {s['name']}"):
                msg = execute_trade(s['code'], 10, "sell")
                st.info(msg)
        else:
            st.warning("⚖️ HOLD (Sentiment Neutro)")
        st.caption(f"Ultima News: {s['news'][:70]}...")

with col_n:
    st.header("📰 News Stream")
    for n in news[:8]:
        st.write(f"**{n['source']['name']}**: {n['title']}")
        st.divider()
