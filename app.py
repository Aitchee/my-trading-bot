import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="EDOARDO TERMINAL", layout="wide")

# Recupero chiave (Assicurati che sia quella NUOVA e segreta)
RAW_KEY = st.secrets.get("BITPANDA_API_KEY", "881aefd79878522f1b565cd8003b25df0cf1455654f73240edfc50ccae1ca8d4b4d4f218af699a84ce08b8c4b03019edf361986d3023f877673bff3e28610518")
BITPANDA_KEY = RAW_KEY.strip().replace('"', '').replace("'", "")

def check_bitpanda():
    if not BITPANDA_KEY:
        return "MANCA_CHIAVE_NEI_SECRETS"
    
    # Usiamo l'endpoint più leggero in assoluto
    url = "https://api.bitpanda.com/v1/fiat-wallets"
    headers = {
        "X-API-KEY": BITPANDA_KEY,
        "Accept": "application/json"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', [])
        return f"ERRORE_{r.status_code}: {r.text}"
    except Exception as e:
        return f"ERRORE_RETE: {str(e)}"

# --- INTERFACCIA ---
st.title(f"🚀 TERMINALE EDOARDO - {datetime.now().strftime('%H:%M:%S')}")

res = check_bitpanda()

if isinstance(res, list):
    st.success("✅ SEI DENTRO! Connessione stabilita con Bitpanda.")
    if not res:
        st.info("Connesso, ma non ci sono Euro nel Fiat Wallet.")
    for item in res:
        attr = item.get('attributes', {})
        bal = float(attr.get('balance', 0))
        if bal > 0:
            st.metric(f"Saldo {attr.get('name')}", f"€ {bal:.2f}")
else:
    st.error(f"⚠️ {res}")
    st.markdown("""
    ### Se vedi ancora 401:
    1. Hai cliccato **'Confirm'** nell'email di Bitpanda per la **nuova** chiave?
    2. Hai messo la spunta su **'Balance'** e **'Trading'**?
    3. Hai salvato i **Secrets** su Streamlit dopo aver incollato la chiave?
    """)

