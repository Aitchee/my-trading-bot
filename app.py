import streamlit as st
import requests
from datetime import datetime

# Setup minimo
st.set_page_config(page_title="EDOARDO TERMINAL", layout="wide")

# Recupero chiave (Assicurati che sia quella NUOVA e segreta)
BITPANDA_KEY = st.secrets.get("BITPANDA_API_KEY", "ad7c16aa1dce062f454b9c1a58f1972de5d41698d1d119e48aaf63e66b6f402ef3c9a3c7e7e2648211f0b5aa83036a67205df48710b91215b9cd09616c5159b0").strip()

def test_connection():
    if not BITPANDA_KEY:
        return "MANCA_CHIAVE"
    
    # Endpoint più semplice per testare l'autorizzazione
    url = "https://api.bitpanda.com/v1/fiat-wallets"
    headers = {"X-API-KEY": BITPANDA_KEY, "Accept": "application/json"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', [])
        return f"ERRORE_{r.status_code}: {r.text}"
    except Exception as e:
        return f"ERRORE_RETE: {str(e)}"

# --- UI ---
st.title(f"🚀 TERMINALE EDOARDO - {datetime.now().strftime('%H:%M:%S')}")

data = test_connection()

if isinstance(data, list):
    st.success("✅ CONNESSIONE RIUSCITA! Il bot vede i tuoi asset.")
    for item in data:
        attr = item.get('attributes', {})
        if float(attr.get('balance', 0)) > 0:
            st.metric(f"Saldo {attr.get('name')}", f"€ {attr.get('balance')}")
else:
    st.error(f"⚠️ {data}")
    st.info("Se leggi ancora 401, significa che Bitpanda sta ancora rifiutando la tua chiave. Controlla di aver cliccato l'email di conferma per la NUOVA chiave.")
