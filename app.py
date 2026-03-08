import streamlit as st
import requests
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# METTI QUI IL LINK CHE HAI APPENA COPIATO DA GOOGLE
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

def recupera_dati():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except Exception as e:
        return [], f"Errore: {str(e)[:20]}"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
with col_h2:
    if st.button("🔄 SINCRONIZZA ORA"):
        st.rerun()

st.divider()
col_sx, col_cx, col_dx = st.columns([1.5, 1, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    data, status = recupera_dati()
    
    if status == 200:
        if len(data) > 0:
            for item in data:
                attr = item.get('attributes', {})
                qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
                symbol = attr.get('symbol', '')
                if qty > 0:
                    nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "EUR": "Euro"}
                    nome = nomi.get(symbol, symbol)
                    st.metric(nome, f"{qty:.4f} {symbol}")
                    st.divider()
        else:
            st.warning("⚠️ Collegato, ma Bitpanda restituisce un portafoglio vuoto.")
            st.info("Controlla di aver creato una 'Nuova Versione' nello script di Google.")
    else:
        st.error(f"Status Errore: {status}")

with col_dx:
    st.subheader("📊 Grafico Leonardo")
    chart_html = '<div style="height:450px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});</script></div>'
    st.components.v1.html(chart_html, height=460)
