import streamlit as st
import requests

st.set_page_config(page_title="BITPANDA TERMINAL", layout="wide")

BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

st.header("💰 Portafoglio Reale Bitpanda")

if st.button("🔄 SINCRONIZZA ORA"):
    st.rerun()

try:
    r = requests.get(BRIDGE_URL, timeout=15)
    data = r.json().get('data', [])
    
    if not data:
        st.error("Dati non ricevuti. Controlla che la Chiave API abbia i permessi 'Trading' e 'Read All'.")
        st.json(r.json()) # Visualizza la risposta grezza per debug
    else:
        for item in data:
            attr = item.get('attributes', {})
            # Legge sia balance (fiat) che amount (stocks/crypto)
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            if qty > 0:
                nome = attr.get('name', 'N/A')
                symbol = attr.get('symbol', '???')
                st.subheader(f"{nome} ({symbol})")
                st.title(f"{qty:.4f}")
                st.write("---")
except Exception as e:
    st.error(f"Errore di rete: {e}")
