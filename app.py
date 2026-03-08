import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="REAL AI TERMINAL", layout="wide")

# --- CONFIGURAZIONE ASSET REALI (Inserisci i tuoi ticker eToro qui) ---
# Esempio: LDO.MI (Leonardo), ISP.MI (Intesa), AMZN (Amazon)
MY_TICKERS = ["LDO.MI", "ISP.MI", "AMZN", "NVDA"]

def get_real_data(tickers):
    data = []
    for t in tickers:
        stock = yf.Ticker(t)
        hist = stock.history(period="1d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            change = hist['Close'].iloc[-1] - hist['Open'].iloc[-1]
            data.append({"Ticker": t, "Prezzo": price, "Change": change})
    return pd.DataFrame(data)

st.title("🚀 REAL-TIME AI TRADING TERMINAL")
st.write("---")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.3])

# 1. SINISTRA: MONITORAGGIO MERCATI REALI (yFinance)
with col_sx:
    st.subheader("📈 Mercati Live")
    df_market = get_real_data(MY_TICKERS)
    for index, row in df_market.iterrows():
        st.metric(row['Ticker'], f"{row['Prezzo']:.2f} €", f"{row['Change']:.2f}")

# 2. CENTRO: NEWS VERE (RSS Feed)
with col_cx:
    st.subheader("📰 News Vere (Borsa)")
    # Usiamo un trucco per mostrare news reali senza API Key complicate
    for t in MY_TICKERS:
        st.write(f"**Ultim'ora {t}:**")
        st.caption(f"Verifica news su: [Finanza Online](https://www.finanzaonline.com/ricerca?q={t})")
    # Nota: Qui integreremo una libreria di scraping per titoli specifici

# 3. DESTRA: IL TUO PORTAFOGLIO (Manuale/Google Sheet)
with col_dx:
    st.subheader("💰 Portafoglio eToro Reale")
    st.warning("Per leggere i tuoi dati eToro, dobbiamo collegare un Google Sheet.")
    st.info("eToro non permette l'accesso API diretto ai privati.")
    
    # Esempio di calcolo reale se inserisci i tuoi dati
    pmc_esempio = st.number_input("Inserisci il tuo prezzo di carico Leonardo:", value=21.0)
    prezzo_attuale = df_market[df_market['Ticker'] == "LDO.MI"]['Prezzo'].values[0]
    st.write(f"**Leonardo (LDO.MI)**")
    st.metric("P&L Attuale", f"{prezzo_attuale:.2f} €", f"{(prezzo_attuale-pmc_esempio):.2f} €")

# --- GRAFICI REALI ---
st.write("---")
ticker_chart = st.selectbox("Seleziona grafico reale:", MY_TICKERS)
df_chart = yf.download(ticker_chart, period="1mo", interval="1d")
if not df_chart.empty:
    fig = px.line(df_chart, y="Close", title=f"Andamento Reale 30gg: {ticker_chart}", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
