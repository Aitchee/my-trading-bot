import streamlit as st
import requests

st.set_page_config(page_title="AI Trading Bot PRO", layout="wide")

# --- RECUPERO CHIAVI ---
BP_KEY = st.secrets["BITPANDA_API_KEY"]
NW_KEY = st.secrets["NEWS_API_KEY"]

st.title("🚀 AI Trading Command Center")

# --- FUNZIONE LOGICA AI ---
def analizza_asset(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it"
    try:
        r = requests.get(url).json()
        news = r['articles'][0]['title'] if r['articles'] else "Nessuna news"
        # Logica simulata: se la news è lunga o contiene parole chiave, il sentiment è alto
        score = 0.85 if any(x in news.lower() for x in ["rialzo", "record", "dividendo", "crescita"]) else 0.40
        return news, score
    except:
        return "Connessione news assente", 0.0

# --- LAYOUT SUPERIORE (3 COLONNE) ---
col_news, col_opportunita, col_portafoglio = st.columns([1, 1.2, 1])

with col_news:
    st.header("📰 Global News")
    for topic in ["Borsa Italiana", "Inflazione", "Mercati"]:
        titolo, _ = analizza_asset(topic)
        st.write(f"🔹 {titolo}")

with col_opportunita:
    st.header("🎯 Consigli AI (Buy)")
    # Lista di asset potenziali da monitorare
    potenziali = ["Bitcoin", "Apple", "Ferrari", "Oro"]
    for p in potenziali:
        news, score = analizza_asset(p)
        if score > 0.8:
            st.success(f"✅ **{p}**: Segnale Forte (Sentiment: {score})")
            if st.button(f"Investi ora in {p}"):
                st.toast(f"Ordine automatico inviato per {p}!")
        else:
            st.info(f"⚪ **{p}**: Monitoraggio (Sentiment: {score})")

with col_portafoglio:
    st.header("💼 I Tuoi Asset")
    miei_asset = {"Leonardo SPA": "+4.5%", "Intesa SP": "-1.2%"}
    for nome, rendimento in miei_asset.items():
        st.metric(label=nome, value=rendimento, delta=rendimento)
        st.caption(f"Ultima news: {analizza_asset(nome)[0][:50]}...")

st.divider()

# --- LAYOUT INFERIORE (GRAFICI) ---
st.header("📊 Analisi Tecnica (TradingView)")
col_g1, col_g2 = st.columns(2)

def genera_grafico(symbol):
    return f"""
        <div style="height:300px">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{symbol}", "interval": "H",
          "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "it", "toolbar
