import streamlit as st
import requests

st.set_page_config(page_title="BITPANDA RECOVERY", layout="wide")

BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

st.header("🔍 Verifica Dati Bitpanda")

if st.button("ESEGUI SCANSIONE FORZATA"):
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        data_json = r.json()
        
        st.subheader("1. Risposta Grezza (Se è [], la chiave API è limitata)")
        st.json(data_json)
        
        st.subheader("2. Analisi Portafoglio")
        assets = data_json.get('data', [])
        if not assets:
            st.error("Nessun dato trovato. Bitpanda risponde con una lista vuota.")
        else:
            for item in assets:
                attr = item.get('attributes', {})
                qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
                if qty > 0:
                    st.write(f"🏷️ **{attr.get('symbol')}** ({attr.get('name')}): **{qty}**")
                    
    except Exception as e:
        st.error(f"Errore tecnico: {e}")

# Il grafico è in fondo, piccolo, così non rompe i coglioni.
st.divider()
st.caption("Grafico di servizio")
st.components.v1.html('<div style="height:200px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","theme":"dark","container_id":"tv"});</script></div>', height=200)
