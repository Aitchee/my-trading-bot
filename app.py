import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10000, key="datarefresh")
st.set_page_config(page_title="EDOARDO LIVE TERMINAL", layout="wide")

# Recupero chiavi
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "").strip()
ETORO_KEY = st.secrets.get("ETORO_API_KEY", "").strip()

analyzer = SentimentIntensityAnalyzer()

def get_etoro_data():
    if not ETORO_KEY:
        return "MISSING_KEY"

    headers = {
        "Authorization": f"Bearer {ETORO_API_KEY}",
        "Content-Type": "application/json",
        "X-Accept-Version": "v1"
    }

    try:
        # STEP 1: Chiediamo all'API chi siamo (User Discovery)
        # Questo endpoint serve a trovare l'ID numerico partendo dal Token
        user_info_res = requests.get("https://api.etoro.com/v1/users/me", headers=headers, timeout=10)
        
        if user_info_res.status_code != 200:
            return f"Errore Autenticazione: {user_info_res.status_code}"
        
        user_data = user_info_res.json()
        # Estraiamo l'ID numerico che eToro ti nasconde
        real_id = user_data.get('cid') or user_data.get('accountID')
        
        # STEP 2: Usiamo l'ID trovato per prendere il saldo
        url_balance = f"https://api.etoro.com/v1/accounts/{real_id}/balance"
        balance_res = requests.get(url_balance, headers=headers, timeout=10)
        
        if balance_res.status_code == 200:
            return {"balance": balance_res.json().get('balance'), "id": real_id}
        else:
            return f"Errore Saldo: {balance_res.status_code}"
            
    except Exception as e:
        return f"Errore Connessione: {str(e)}"

# --- LOGICA NEWS ---
def get_signals():
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_KEY}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla", "Oil"]
        signals = []
        for asset in watchlist:
            relevant = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if relevant:
                score = sum([analyzer.polarity_scores(a['title'])['compound'] for a in relevant]) / len(relevant)
                signals.append({"asset": asset, "score": score, "news": relevant[0]['title']})
        return signals, articles
    except: return [], []

# --- INTERFACCIA ---
st.title(f"🚀 TERMINALE LIVE - {datetime.now().strftime('%H:%M:%S')}")
c1, c2, c3 = st.columns([1, 1.2, 1])

with c1:
    st.header("💰 Asset eToro")
    res = get_etoro_data()
    if isinstance(res, str):
        st.error(f"Dati non ricevuti: {res}")
        st.info("💡 Il bot sta cercando di estrarre il tuo ID numerico dal Token...")
    else:
        st.metric("Saldo Reale (API)", f"${res['balance']}")
        st.caption(f"ID Account Rilevato: {res['id']}")
        st.success("Connessione IRL Stabilita!")

with c2:
    st.header("🎯 Papabili Acquisto")
    signals, news = get_signals()
    for s in signals:
        if s['score'] > 0.15: st.success(f"**BUY {s['asset']}** ({s['score']:.2f})")
        elif s['score'] < -0.15: st.error(f"**SELL {s['asset']}** ({s['score']:.2f})")
        else: st.warning(f"**WAIT {s['asset']}** ({s['score']:.2f})")

with c3:
    st.header("📰 News Feed")
    for n in news[:10]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
        st.divider()
