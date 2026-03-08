import streamlit as st
from trading_bot import TradingBot
import pandas as pd

bot = TradingBot()

st.set_page_config(page_title="Edoardo Trading Bot", layout="wide")
st.title("🤖 Dashboard Trading Bot: eToro & Bitpanda")

# Sidebar con Stato Account
st.sidebar.header("Stato Account eToro")
status = bot.get_etoro_status()
st.sidebar.metric("Saldo Totale", f"{status['balance']} {status['currency']}")
st.sidebar.write(f"Operazione attuale: **{status['active_trade']}**")

# Analisi News in tempo reale
st.subheader("🌍 Analisi Eventi Globali e Sentiment")
assets = ["Gold", "Bitcoin", "Tesla", "S&P 500"]
cols = st.columns(len(assets))

for i, asset in enumerate(assets):
    with cols[i]:
        sentiment = bot.get_sentiment(asset)
        st.metric(label=asset, value=f"{sentiment:.2f}")
        if sentiment > 0.2:
            st.success("Segnale: BUY 🚀")
        elif sentiment < -0.2:
            st.error("Segnale: SELL 📉")
        else:
            st.warning("Segnale: NEUTRAL ⚖️")

# Log delle operazioni
st.divider()
st.subheader("📝 Log Operazioni Recenti")
log_data = {
    "Orario": ["2026-03-08 22:10", "2026-03-08 21:00"],
    "Asset": ["XAU/USD", "BTC"],
    "Azione": ["HOLD", "MONITORING"],
    "Motivazione": ["Sentiment Oro Stabile", "News API: Attesa dati USA"]
}
st.table(pd.DataFrame(log_data))
