import streamlit as st
import requests
import json
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# 1. SETUP INTERFACCIA
st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")
st_autorefresh(interval=10000, key="terminal_refresh_final_v3")

# 2. RECUPERO SEGRETI
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {
    "X-API-KEY": BITPANDA_KEY,
    "Accept": "application/json"
}

# 3. MOTORE DI ESTRAZIONE ASSET (CORAZZATO)
def get_all_my_assets():
    if not BITPANDA_KEY: return "CONFIG_MISSING"
    
    urls = {
        "Assets": "https://api.bitpanda.com/v1/asset-wallets",
        "Fiat": "https://api.bitpanda.com/v1/fiat-wallets"
    }
    
    my_portfolio = []
    
    try:
        for category, url in urls.items():
            response = requests.get(url, headers=headers, timeout=10)
            
            # Se la risposta non è un successo (200), fermati e mostra l'errore
            if response.status_code != 200:
                return f"Errore {response.status_code} su {category}: {response.text[:100]}"
            
            # Prova a trasformare in JSON in modo sicuro
            try:
                json_data = response.json()
            except Exception:
                return f"Bitpanda ha risposto con testo non valido su {category}"

            # CONTROLLO TIPO: Se json_data è una stringa, scatta l'errore che avevi
            if not isinstance(json_data, dict):
                return f"Risposta inattesa da Bitpanda su {category}"

            # Estrazione sicura
            data_list = json_data.get('data', [])
            for item in data_list:
                if isinstance(item, dict):
                    attr = item.get('attributes', {})
                    balance = float(attr.get('balance', 0))
                    if balance > 0:
                        my_portfolio.append({
                            "symbol": attr.get('symbol', '???'),
                            "name": attr.get('name', 'Sconosciuto'),
                            "balance": balance,
                            "type": category
                        })
        
        return my_portfolio
    except Exception as e:
        return f"Errore di rete: {str(e)}"

# --- INTERFACCIA DASHBOARD ---
st.title(f"🚀 EDOARDO TERMINAL LIVE - {datetime.now().strftime('%H:%M:%S')}")

col_assets, col_ai, col_news = st.columns([1, 1.2, 1])

with col_assets:
    st.header("💰 I Miei Asset (IRL)")
    portfolio = get_all_my_assets()
    
    if isinstance(portfolio, str):
        st.error(f"⚠️ {portfolio}")
        if "401" in portfolio:
            st.info("💡 Consiglio: Il codice 401 significa che la tua API KEY non è autorizzata. Controlla di averla confermata via email.")
    elif not portfolio:
        st.info("Connesso, ma il portafoglio risulta vuoto (Saldo 0.00).")
    else:
        for a in portfolio:
            icon = "💶" if a['type'] == "Fiat" else "🪙"
            st.metric(f"{icon} {a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Dati Bitpanda Sincronizzati")

with col_ai:
    st.header("🎯 Analisi AI")
    # News logic
    try:
        n_url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
        n_res = requests.get(n_url).json()
        articles = n_res.get('articles', [])
        for asset_name in ["Gold", "Bitcoin", "NVIDIA"]:
            rel = [a for a in articles if asset_name.lower() in (a['title'] or "").lower()]
            if rel:
                score = analyzer.polarity_scores(rel[0]['title'])['compound']
                if score > 0.1: st.success(f"**BUY {asset_name}**")
                elif score < -0.1: st.error(f"**SELL {asset_name}**")
                else: st.warning(f"**WAIT {asset_name}**")
    except: st.caption("Caricamento news...")

with col_news:
    st.header("📰 News Stream")
    st.write("Aggiornamento dinamico attivo.")
