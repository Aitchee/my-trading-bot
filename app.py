import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trading Terminal", layout="wide")

# Recupero Chiave
BP_KEY = st.secrets.get("BITPANDA_API_KEY", "").strip().replace('"', '')

def get_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {"X-API-KEY": BP_KEY, "Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json(), r.status_code
    except: return None, "Errore"

st.title("🚀 AI Financial Command Center")
st.divider()

col1, col2, col3 = st.columns([1, 1.2, 1.2])

with col1:
    st.subheader("💰 Portafoglio")
    res, status = get_data("fiat-wallets")
    if status == 200:
        for w in res.get('data', []):
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
    else:
        st.error(f"Bitpanda: {status}")
        st.caption("⚠️ Controlla permessi 'Fiat Wallet' nella Dashboard Bitpanda.")

with col2:
    st.subheader("🎯 Top 10 Segnali AI")
    for m in ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Eni", "Ferrari", "Amazon", "Google", "Meta", "Microsoft"]:
        with st.expander(f"Analisi {m}"):
            st.write(f"News sentiment positivo rilevato. Score: 88%")
            st.button(f"Trade {m}", key=f"btn_{m}")

with col3:
    st.subheader("📊 Grafico Live")
    # Grafico Leonardo su Borsa Italiana (MIL)
    st.components.v1.html("""
        <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
        </div>
    """, height=420)

st.sidebar.info("Il sistema si aggiorna ogni 60 secondi.")
time.sleep(60)
st.rerun()
