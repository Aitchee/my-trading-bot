import streamlit as st
import requests

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Link del tuo ponte Google (deve terminare con /exec)
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

st.header("💰 Portafoglio Reale Bitpanda")

if st.button("🔄 SINCRONIZZA ORA"):
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        res = r.json()
        assets = res.get('data', [])
        
        if not assets:
            st.warning("⚠️ Connessione OK, ma Bitpanda restituisce 0 asset. Verifica i permessi 'Trading' della chiave.")
            st.json(res)
        else:
            for a in assets:
                attr = a.get('attributes', {})
                # Legge balance per contanti e amount per titoli/crypto
                val = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
                if val > 0:
                    symbol = attr.get('symbol', 'N/A')
                    name = attr.get('name', symbol)
                    st.metric(label=f"{name} ({symbol})", value=f"{val:.4f}")
                    st.divider()
    except Exception as e:
        st.error(f"Errore: {e}")
