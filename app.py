import streamlit as st
import requests
import time

st.set_page_config(page_title="Debug Bitpanda V2", layout="wide")

# Recupero chiave
BP_KEY = st.secrets.get("BITPANDA_API_KEY", "").strip()

def test_v2():
    # Proviamo l'endpoint della v2 che a volte scavalca i blocchi della v1
    url = "https://api.bitpanda.com/v2/balances"
    headers = {
        "X-Api-Key": BP_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0" # Simula un accesso umano
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return str(e), "Errore"

st.title("🤖 Test Connessione V2")

dati, status = test_v2()

if status == 200:
    st.success("✅ CLAMOROSO: Connesso con V2!")
    st.json(dati)
elif status == 401:
    st.error("❌ Ancora 401: Accesso Negato")
    st.write("Dettaglio errore:", dati)
    
    st.divider()
    st.warning("⚠️ **Diagnosi Finale:**")
    st.write("""
    Se anche questo fallisce, il problema non è il codice, ma una di queste due cose nelle impostazioni di Bitpanda:
    1. **E-mail di conferma:** Controlla la tua mail. Bitpanda spesso invia una mail per 'autorizzare l'uso della chiave API' dopo che l'hai creata. Finché non clicchi, la chiave dà 401.
    2. **Restrizioni geografiche/IP:** Streamlit usa server americani o europei random. Se Bitpanda vede un accesso sospetto da un server cloud, lo sega istantaneamente.
    """)
else:
    st.info(f"Status: {status}")

# Il grafico deve funzionare a prescindere dall'API
st.subheader("📊 Analisi Tecnica Leonardo (Sempre Attivo)")
st.components.v1.html("""
    <div style="height:400px;">
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "autosize": true, "symbol": "MIL:LDO", "interval": "D",
      "theme": "dark", "style": "1", "locale": "it"
    });
    </script>
    </div>
""", height=420)
