import streamlit as st
import requests
import datetime

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# INCOLLA QUI IL NUOVO URL CHE HAI COPIATO DA GOOGLE
BRIDGE_URL = "INCOLLA_QUI_IL_NUOVO_LINK_EXEC"

def recupera_dati():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Bridge"

st.title("🚀 AI Financial Terminal")
if st.button("🔄 AGGIORNA TUTTO"):
    st.rerun()

st.divider()
col_sx, col_cx, col_dx = st.columns([1.5, 1, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    data, status = recupera_dati()
    
    if status == 200 and len(data) > 0:
        for item in data:
            attr = item.get('attributes', {})
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            if qty > 0:
                nome = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "EUR": "Euro"}.get(symbol, symbol)
                st.metric(nome, f"{qty:.4f} {symbol}")
                st.divider()
    else:
        st.error(f"Status: {status}")
        st.info("Se vedi ancora questo, l'URL nel codice Python è diverso da quello dell'ultima versione di Google.")

with col_dx:
    st.subheader("📊 Grafico")
    st.components.v1.html('<div style="height:450px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});</script></div>', height=460)
