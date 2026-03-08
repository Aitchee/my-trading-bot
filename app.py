import streamlit as st
import requests

st.set_page_config(page_title="PORTFOLIO REAL-TIME", layout="wide")

BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

st.header("💰 Portafoglio Bitpanda")

if st.button("🔄 AGGIORNA"):
    st.rerun()

try:
    r = requests.get(BRIDGE_URL, timeout=15)
    res = r.json()
    assets = res.get('data', [])
    
    if not assets:
        st.error("Bitpanda restituisce ancora ZERO dati. Controlla i permessi della chiave API (Read/Balance/Trading).")
        st.json(res) # Debug crudo
    else:
        for a in assets:
            attr = a.get('attributes', {})
            val = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            if val > 0:
                col1, col2 = st.columns(2)
                col1.subheader(f"{attr.get('name')} ({attr.get('symbol')})")
                col2.header(f"{val:.4f}")
                st.divider()
except Exception as e:
    st.write(f"Errore: {e}")
