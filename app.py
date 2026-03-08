import streamlit as st
import requests

st.set_page_config(page_title="Terminal Operativo", layout="wide")

# URL del tuo deployment di Google Script
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

st.header("💰 Saldi Real-Time Bitpanda")

if st.button("🔄 SINCRONIZZA ORA"):
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        res = r.json()
        assets = res.get('data', [])
        
        if not assets:
            st.error("Il ponte è attivo ma Bitpanda non invia asset. Controlla i permessi della chiave API.")
            st.json(res)
        else:
            for a in assets:
                attr = a.get('attributes', {})
                # Legge balance per fiat e amount per asset
                val = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
                if val > 0:
                    symbol = attr.get('symbol', 'N/D')
                    name = attr.get('name', symbol)
                    st.write(f"🏷️ **{name}** ({symbol}): **{val:.4f}**")
                    st.divider()
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
