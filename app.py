import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Trading Bot Debug", layout="wide")

# RECUPERO CHIAVI (Senza manipolazioni, le prendiamo come sono)
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
except:
    st.error("Chiave BITPANDA_API_KEY non trovata nei Secrets!")
    st.stop()

# --- FUNZIONE DI TEST (DIRETTISSIMA) ---
def test_connessione():
    # Proviamo l'endpoint bilancio globale, più stabile del fiat-wallets
    url = "https://api.bitpanda.com/v1/balances"
    headers = {
        "X-API-KEY": BP_KEY,
        "Accept": "application/json" # Fondamentale per Bitpanda
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return str(e), "Errore"

st.title("🤖 Debug Connessione Bitpanda")

# --- ESECUZIONE TEST ---
dati, status = test_connessione()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Stato API")
    if status == 200:
        st.success(f"✅ CONNESSO! (Codice {status})")
        st.write("Il bot ora riesce a leggere i tuoi dati.")
    elif status == 401:
        st.error(f"❌ ERRORE 401: Accesso Negato")
        st.write("Bitpanda non riconosce questa chiave. Controlla che non sia scaduta.")
    else:
        st.warning(f"⚠️ Status: {status}")
        st.write(dati)

with col2:
    st.subheader("Grafico di Controllo (Leonardo)")
    # Se il grafico non appare qui, il problema è il simbolo di TradingView
    st.components.v1.html("""
        <div style="height:350px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "MIL:LDO", "interval": "D",
          "theme": "dark", "style": "1", "locale": "it", "timezone": "Etc/UTC"
        });
        </script>
        </div>
    """, height=360)

# Visualizzazione dei dati grezzi per capire cosa arriva
st.divider()
st.subheader("Dati Grezzi ricevuti dall'API:")
st.json(dati)

# Refresh ogni 30s per il debug
time.sleep(30)
st.rerun()
