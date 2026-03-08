import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# 1. SETUP INTERFACCIA
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")
st_autorefresh(interval=10000, key="terminal_refresh_final")

# 2. RECUPERO SEGRETI
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

# 3. MOTORE DI ESTRAZIONE ASSET (FIAT + CRYPTO/GOLD)
def get_all_my_assets():
    if not BITPANDA_KEY: return "CONFIG_MISSING"
    
    # Endpoint per Asset (Oro, BTC, ecc.) e Fiat (Euro)
    urls = {
        "Assets": "https://api.bitpanda.com/v1/asset-wallets",
        "Fiat": "https://api.bitpanda.com/v1/fiat-wallets"
    }
    
    my_portfolio = []
    
    try:
        for category, url in urls.items():
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                if isinstance(json_data, dict) and 'data' in json_data:
                    for item in json_data['data']:
                        attr = item.get('attributes', {})
                        balance = float(attr.get('balance', 0))
                        # Mostriamo solo quello che ha valore > 0
                        if balance > 0:
                            my_portfolio.append({
                                "symbol": attr.get('symbol'),
                                "name": attr.get('name'),
                                "balance": balance,
                                "type": category
                            })
            else:
                return f"Errore {response.status_code} su {category}"
        
        return my_portfolio
    except Exception as e:
        return f"Errore Connessione: {str(e)}"

# --- INTERFACCIA DASHBOARD ---
st.title(f"🚀 EDOARDO TERMINAL LIVE - {datetime.now().strftime('%H:%M:%S')}")

col_assets, col_ai, col_news = st.columns([1, 1.2, 1])

with col_assets:
    st.header("💰 I Miei Asset (IRL)")
    portfolio = get_all_my_assets()
    
    if isinstance(portfolio, str):
        st.error(f"⚠️ {portfolio}")
    elif not portfolio:
        st.info("Connesso, ma il portafoglio risulta vuoto (Saldo 0.00).")
    else:
        for a in portfolio:
            icon = "💶" if a['type'] == "Fiat" else "🪙"
            st.metric(f"{icon} {a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Dati Bitpanda Sincronizzati")

with col_ai:
    st.header("🎯 Segnali AI")
    # Qui il bot analizza se comprare/vendere in base alle news
    st.write("Analisi flussi di mercato in corso...")
    # Recupero news semplificato
    try:
        n_url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
        articles = requests.get(n_url).json().get('articles', [])
        for asset_name in ["Gold", "Bitcoin", "NVIDIA"]:
            rel = [a for a in articles if asset_name.lower() in (a['title'] or "").lower()]
            if rel:
                score = analyzer.polarity_scores(rel[0]['title'])['compound']
                if score > 0.1: st.success(f"**BUY {asset_name}**")
                elif score < -0.1: st.error(f"**SELL {asset_name}**")
                else: st.warning(f"**WAIT {asset_name}**")
    except: st.caption("In attesa di news...")

with col_news:
    st.header("📰 News Stream")
    # Mostra le ultime news reali
    st.write("Connessione NewsAPI attiva.")
