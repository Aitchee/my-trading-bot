import streamlit as st
import json
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="EDOARDO AI TERMINAL", layout="wide")
analyzer = SentimentIntensityAnalyzer()

# --- SIDEBAR: INPUT DATI REALI ---
st.sidebar.header("🔌 Collegamento Live")
raw_json = st.sidebar.text_area("Incolla qui il JSON della Console eToro:", height=150, help="Copia tutto il blocco 'AggregatedResult' e incollalo qui.")

# --- LOGICA DI PARSING ---
def parse_etoro_json(data_str):
    try:
        data = json.loads(data_str)
        # Navighiamo nella struttura che hai postato
        portfolio = data['AggregatedResult']['ApiResponses']['PrivatePortfolio']['Content']['ClientPortfolio']
        rates = data['AggregatedResult']['ApiResponses']['Rates']['Content']
        
        pos_list = []
        for pos in portfolio['Positions']:
            instr_id = str(pos['InstrumentID'])
            # Troviamo il prezzo corrente nei Rates
            current_rate = rates.get(instr_id, {}).get('Bid', pos['OpenRate'])
            
            # Calcolo profitto con Leva (estratta dal JSON)
            pnl = (current_rate - pos['OpenRate']) if pos['IsBuy'] else (pos['OpenRate'] - current_rate)
            pnl_perc = (pnl / pos['OpenRate']) * 100 * pos['Leverage']
            
            pos_list.append({
                "Asset": "GOLD" if instr_id == "18" else f"ID {instr_id}",
                "Investito": pos['Amount'],
                "Profitto": round(pnl_perc, 2),
                "Prezzo_Ora": current_rate,
                "ID": pos['PositionID']
            })
        return pos_list
    except Exception as e:
        return None

# --- LOGICA NEWS ---
def get_ai_signals():
    news_key = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={news_key}&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        watchlist = ["Gold", "Bitcoin", "NVIDIA", "Tesla"]
        found = []
        for asset in watchlist:
            rel = [a for a in articles if asset.lower() in (a['title'] or "").lower()]
            if rel:
                score = analyzer.polarity_scores(rel[0]['title'])['compound']
                found.append({"name": asset, "score": score, "news": rel[0]['title']})
        return found, articles
    except: return [], []

# --- DASHBOARD ---
st.title(f"🤖 EDOARDO AI TERMINAL - {datetime.now().strftime('%H:%M:%S')}")

col1, col2, col3 = st.columns([1, 1.2, 1])

with col1:
    st.header("💰 Portafoglio IRL")
    if raw_json:
        user_data = parse_etoro_json(raw_json)
        if user_data:
            for p in user_data:
                st.metric(f"{p['Asset']} (Prezzo: {p['Prezzo_Ora']})", f"${p['Investito']}", f"{p['Profitto']}%")
                st.caption(f"ID Posizione: {p['ID']}")
            st.success("Dati sincronizzati con successo.")
        else:
            st.error("Formato JSON non valido. Assicurati di copiare tutto.")
    else:
        st.info("Incolla il JSON nella barra laterale per visualizzare i tuoi asset reali.")

with col2:
    st.header("🎯 Papabili Acquisto")
    signals, news_list = get_ai_signals()
    for s in signals:
        if s['score'] > 0.1: st.success(f"**BUY {s['name']}** (Sentiment: {s['score']:.2f})")
        elif s['score'] < -0.1: st.error(f"**SELL {s['name']}** (Sentiment: {s['score']:.2f})")
        else: st.warning(f"**WAIT {s['name']}**")
        st.caption(f"News: {s['news'][:60]}...")

with col3:
    st.header("📰 News Feed Live")
    for n in news_list[:10]:
        st.write(f"**{n['source']['name']}**: [{n['title']}]({n['url']})")
        st.divider()
