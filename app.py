import streamlit as st
import requests

st.title("🔍 Bitpanda API Scanner")

# Recupero chiave
key = st.secrets["BITPANDA_API_KEY"].strip().replace('"', '')

def test_endpoint(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {
        "X-API-KEY": key,
        "Accept": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return "Errore", str(e)

# --- SCANSIONE ENDPOINT DOCUMENTAZIONE ---
endpoints = ["fiat-wallets", "balances", "asset-wallets", "currencies"]

st.write("Sto testando gli endpoint della documentazione con la tua chiave...")

for ep in endpoints:
    status, result = test_endpoint(ep)
    if status == 200:
        st.success(f"✅ {ep}: FUNZIONA! (200)")
        st.json(result)
    else:
        st.error(f"❌ {ep}: FALLITO ({status})")
        if status == 401:
            st.warning(f"Il server dice: Credenziali errate per {ep}. Controlla i permessi Fiat/Balance.")

st.divider()
st.subheader("📊 Analisi Tecnica Leonardo (Sempre attiva)")
st.components.v1.html("""
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
    </div>
""", height=420)
