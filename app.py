import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# Setup Interfaccia
st.set_page_config(page_title="EDOARDO PRO-TRADER", layout="wide")
st_autorefresh(interval=10000, key="terminal_refresh_final")

# Recupero Chiavi Pulite
RAW_KEY = st.secrets.get("BITPANDA_API_KEY", "ad7c16aa1dce062f454b9c1a58f1972de5d41698d1d119e48aaf63e66b6f402ef3c9a3c7e7e2648211f0b5aa83036a67205df48710b91215b9cd09616c5159b0")
BITPANDA_KEY = RAW_KEY.strip().replace('"', '').replace("'", "")
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY, "Accept": "application/json"}

def fetch_all_wallets():
    if not BITPANDA_KEY: return "CHIAVE_MANCANTE"
    
    # Doppio controllo: Asset (Oro/Crypto) e Fiat (Euro)
    endpoints = {
        "Assets": "https://api.bitpanda.com/v1/asset-wallets",
        "Fiat": "https://api.bitpanda.com/v1/fiat-wallets"
    }
    
    total_portfolio = []
    
    for label, url in endpoints.items():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json().get('data', [])
                for item in data:
                    attr = item.get('attributes', {})
                    balance = float(attr.get('balance', 0))
                    if balance > 0:
                        total_portfolio.append({
                            "name": attr.get('name'),
                            "symbol": attr.get('symbol'),
                            "balance": balance,
                            "type": label
                        })
            elif r.status_code == 401:
                return "ERRORE_401_NON_AUTORIZZATO"
        except:
            continue
            
    return total_portfolio

# --- DASHBOARD ---
st.title(f"🚀 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Saldo Reale")
    portfolio = fetch_all_wallets()
    
    if portfolio == "ERRORE_401_NON_AUTORIZZATO":
        st.error("❌ Chiave Rifiutata. Hai cliccato 'Conferma' nell'email di Bitpanda?")
    elif isinstance(portfolio, list):
        if not portfolio:
            st.info("Connesso. Saldo attuale: 0.00")
        for a in portfolio:
            icon = "💶" if a['type'] == "Fiat" else "🪙"
            st.metric(f"{icon} {a['name']}", f"{a['balance']:.4f} {a['symbol']}")
        st.success("✅ Connessione Bitpanda: LIVE")
    else:
        st.warning("In attesa di dati...")

with c2:
    st.header("🎯 Segnali Trading")
    # Logica AI rapida
    try:
        n_url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
        articles = requests.get(n_url).json().get('articles', [])
        for asset in ["Gold", "Bitcoin", "NVIDIA"]:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = analyzer.polarity_scores(rel[0]['title'])['compound']
                if score > 0.15: st.success(f"🚀 BUY {asset} ({score:.2f})")
                elif score < -0.15: st.error(f"📉 SELL {asset} ({score:.2f})")
                else: st.warning(f"⚖️ WAIT {asset}")
    except: st.write("Analisi news...")

with c3:
    st.header("📰 News Stream")
    st.write("Connesso ai mercati globali.")
