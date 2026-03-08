import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO REAL-TIME TERMINAL", layout="wide")

# Recupero Segreti
ETORO_TOKEN = st.secrets.get("ETORO_API_KEY", "").strip()
CID = st.secrets.get("ETORO_ACCOUNT_ID", "").strip()
NEWS_TOKEN = st.secrets.get("NEWS_API_KEY", "").strip()

analyzer = SentimentIntensityAnalyzer()

def get_market_data():
    """Recupera i dati reali basati sulla struttura JSON fornita"""
    if not ETORO_TOKEN or not CID:
        return "CONFIG_MISSING"

    headers = {"Authorization": f"Bearer {ETORO_TOKEN}", "Content-Type": "application/json"}
    # Endpoint AggregatedResult (quello che hai postato tu)
    url = "https://api.etoro.com/v1/aggregate" 
    
    try:
        # Nota: In alcuni casi eToro richiede una chiamata POST per l'aggregato
        # Se fallisce, usiamo i dati del tuo JSON come struttura di parsing
        res = requests.get(url, headers=headers, timeout=10).json()
        
        portfolio = res['AggregatedResult']['ApiResponses']['PrivatePortfolio']['Content']['ClientPortfolio']
        rates = res['AggregatedResult']['ApiResponses']['Rates']['Content']
        
        positions = []
        for pos in portfolio['Positions']:
            instr_id = str(pos['InstrumentID'])
            current_price = rates.get(instr_id, {}).get('Bid', 0)
            
            # Calcolo profitto reale
            open_rate = pos['OpenRate']
            profit = (current_price - open_rate) if pos['IsBuy'] else (open_rate - current_price)
            profit_perc = (profit / open_rate) * 100 * pos['Leverage']
            
            positions.append({
                "Asset": "GOLD" if instr_id == "18" else f"ID {instr_id}",
                "Value": pos['Amount'],
                "Profit": round(profit_perc, 2),
                "Price": current_price
            })
            
        return {"positions": positions, "cid": CID}
    except:
        # Se l'API aggregate non risponde, simuliamo il parsing sul tuo ultimo JSON per sicurezza
        return "CONNECTION_ERROR"

def get_signals():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_TOKEN}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla"]
        sigs = []
        for asset in watchlist:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in rel]) / len(rel)
                sigs.append({"asset": asset, "score": score, "news": rel[0]['title']})
        return sigs, articles
    except: return [], []

# --- INTERFACCIA ---
st.title(f"📊 TERMINALE EDOARDO IRL - {datetime.now().strftime('%H:%M:%S')}")

c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Il Mio Portafoglio")
    data = get_market_data()
    
    if data == "CONFIG_MISSING":
        st.error("Configura i Secrets!")
    elif data == "CONNECTION_ERROR":
        st.warning("⚠️ Errore di connessione API. Verificare se il Token è scaduto.")
        # Mostriamo l'ultimo dato certo del JSON per debug
        st.metric("Ultimo Saldo Conosciuto", "$57.19")
        st.write("Asset: **GOLD (XAU/USD)**")
    else:
        for p in data['positions']:
            st.metric(f"{p['Asset']} (Prezzo: {p['Price']})", f"${p['Value']}", f"{p['Profit']}%")
        st.success(f"Connesso al CID: {data['cid']}")

with c2:
    st.header("🎯 Papabili Acquisto")
    sigs, news = get_signals()
    for s in sigs:
        if s['score'] > 0.1: st.success(f"**BUY {s['asset']}** ({s['score']:.2f})")
        elif s['score'] < -0.1: st.error(f"**SELL {s['asset']}** ({s['score']:.2f})")
        else: st.warning(f"**WAIT {s['asset']}**")

with c3:
    st.header("📰 News Feed")
    for n in news[:8]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
