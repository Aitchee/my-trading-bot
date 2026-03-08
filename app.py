import streamlit as st
import requests
import datetime

st.set_page_config(page_title="AI Terminal - Debug Mode", layout="wide")

BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

def recupera_raw():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        return r.json(), r.status_code
    except Exception as e:
        return {"errore": str(e)}, 500

st.title("🚀 AI Terminal: Debug Totale")

if st.button("🔍 SCANSIONE PROFONDA"):
    st.rerun()

st.divider()
col_sx, col_dx = st.columns([1.5, 1.2])

with col_sx:
    st.subheader("📦 Analisi Pacchetto Dati")
    raw_json, status = recupera_raw()
    
    if status == 200:
        # Mostriamo il numero di asset trovati
        assets = raw_json.get('data', [])
        st.success(f"Pacchetto ricevuto correttamente. Trovati {len(assets)} asset.")
        
        if len(assets) > 0:
            for a in assets:
                attr = a.get('attributes', {})
                bal = float(attr.get('balance', 0))
                if bal > 0:
                    st.write(f"✅ **Trovato:** {attr.get('name')} ({attr.get('symbol')}) - Q.tà: {bal}")
        else:
            st.warning("⚠️ Il pacchetto 'data' è vuoto. Bitpanda dice che non hai asset.")
            st.info("Questo succede se la Chiave API non ha il permesso 'Assets' attivo.")
        
        # MOSTRACI IL CODICE CRUDO
        with st.expander("🕵️ ISPEZIONA RISPOSTA INTEGRALE (RAW JSON)"):
            st.write(raw_json)
    else:
        st.error(f"Errore Bridge: {status}")
        st.write(raw_json)

with col_dx:
    st.subheader("📊 Analisi Tecnica")
    st.components.v1.html("""
        <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});
        </script>
        </div>
    """, height=460)
