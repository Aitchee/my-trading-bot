import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# CONFIGURAZIONE UNICA (Niente doppioni qui!)
st.set_page_config(page_title="EDOARDO PRO-BOT", layout="wide")

# Timer unico per il refresh automatico (10 secondi)
st_autorefresh(interval=10000, key="terminal_refresh_unique")

# RECUPERO SEGRETI
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1").strip()
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()
headers = {"X-API-KEY": BITPANDA_KEY}

# --- FUNZIONE ASSET (CON CORREZIONE CRASH) ---
def get_bitpanda_assets():
    if not BITPANDA_KEY:
        return "CONFIG_MISSING"
        
    url = "https://api.bitpanda.com/v1/asset-wallets"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Errore {response.status_code}: {response.text[:50]}"
            
        json_data = response.json()
        
        # Verifichiamo che 'data' sia presente e sia una lista
        if isinstance(json_data, dict) and 'data' in json_data:
            active_assets = []
            for item in json_data['data']:
                attr = item.get('attributes', {})
                balance = float(attr.get('balance', 0))
                if balance > 0:
                    active_assets.append({
                        "symbol": attr.get('symbol'),
                        "name": attr.get('name'),
                        "balance": balance
                    })
            return active_assets
        else:
            return "Formato dati Bitpanda non riconosciuto."
            
    except Exception as e:
        return f"Errore di rete: {str(e)}"

# --- LOGICA NEWS ---
def get_market_sentiment():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        watchlist = {"Gold": "XAU", "Bitcoin": "BTC"}
        sigs = []
        for name, code in watchlist.items():
            rel = [a for a in articles if name.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                sigs.append({"name": name, "code": code, "score": score, "news": rel[0]['title']})
        return sigs, articles
    except:
        return [], []

# --- INTERFACCIA DASHBOARD ---
st.title(f"🚀 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")

c_wallet, c_trade, c_news = st.columns([1, 1.2, 1])

with c_wallet:
    st.header("💰 Portafoglio")
    assets = get_bitpanda_assets()
    
    if assets == "CONFIG_MISSING":
        st.error("Inserisci BITPANDA_API_KEY nei Secrets.")
    elif isinstance(assets, str):
        st.error(f"⚠️ {assets}")
    elif not assets:
        st.info("Connesso. Saldo 0.00 su tutti gli asset.")
    else:
        for a in assets:
            st.metric(f"{a['name']} ({a['symbol']})", f"{a['balance']:.4f}")
        st.success("✅ Bitpanda Online")

with c_trade:
    st.header("🎯 Analisi AI")
    signals, raw_news = get_market_sentiment()
    for s in signals:
        st.subheader(f"Asset: {s['name']}")
        if s['score'] > 0.15:
            st.success(f"📈 SEGNALE BUY ({s['score']:.2f})")
            st.button(f"Esegui Ordine {s['name']}", key=f"buy_{s['code']}")
        elif s['score'] < -0.15:
            st.error(f"📉 SEGNALE SELL ({s['score']:.2f})")
        else:
            st.warning("⚖️ Sentiment Neutro")
        st.caption(f"Headline: {s['news'][:70]}...")

with c_news:
    st.header("📰 News Feed")
    for n in raw_news[:8]:
        st.write(f"**{n['source']['name']}**: {n['title']}")
        st.divider()
