import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Recupero Chiave Pulita
try:
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip().replace('"', '').replace("'", "")
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).strip()
except:
    st.error("Configura i Secrets!")
    st.stop()

# Funzione con Header di sicurezza avanzato
def get_bitpanda_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {
        "X-API-KEY": BP_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0" # Fondamentale per far accettare la chiave confermata
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Timeout"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Command Center")
st.caption(f"Status: Live | {time.strftime('%H:%M:%S')}")

col_port, col_ai, col_chart = st.columns([1, 1.2, 1.2])

with col_port:
    st.subheader("💰 Portafoglio")
    # Fiat Wallets (Saldo Euro)
    fiat, status = get_bitpanda_data("fiat-wallets")
    
    if status == 200:
        st.success("✅ Connessione Riuscita!")
        for w in fiat:
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
    else:
        st.error(f"Bitpanda Status: {status}")
        if status == 401:
            st.info("⚠️ Se la chiave è confermata, prova a fare un 'Reboot' dell'app da Streamlit Cloud.")

    st.divider()
    st.subheader("💼 Asset Reali")
    assets, _ = get_bitpanda_data("asset-wallets")
    for a in assets:
        bal = float(a['attributes']['balance'])
        if bal > 0.0001:
            st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")

with col_ai:
    st.subheader("🎯 Top 10 Segnali AI")
    for m in ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Amazon", "Google", "Meta", "Eni", "Enel"]:
        with st.expander(f"Analisi {m}"):
            st.write("Analisi News in corso...")
            st.button("Trade", key=f"t_{m}")

with col_chart:
    st.subheader("📊 Analisi Tecnica Leonardo")
    st.components.v1.html("""
        <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
        </div>
    """, height=420)

time.sleep(60)
st.rerun()
