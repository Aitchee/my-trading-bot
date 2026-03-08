import streamlit as st
import requests
import datetime

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

def recupera_dati():
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Connessione"

st.title("🚀 AI Financial Terminal")
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
with col_h2:
    if st.button("🔄 AGGIORNA"):
        st.rerun()

st.divider()
col_sx, col_cx, col_dx = st.columns([1.5, 1, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio Reale")
    data, status = recupera_dati()
    
    if status == 200 and len(data) > 0:
        found_any = False
        for item in data:
            attr = item.get('attributes', {})
            # Bitpanda usa 'balance' per i contanti e spesso nulla o campi diversi per le azioni legacy
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            
            if qty > 0:
                found_any = True
                nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "EUR": "CONTANTI"}
                nome = nomi.get(symbol, symbol)
                
                with st.container():
                    c1, c2 = st.columns([1.5, 1])
                    if symbol == "EUR":
                        c1.metric("EURO CASH", f"{qty:.2f} €")
                    else:
                        pmc = float(attr.get('average_price', 0))
                        c1.write(f"**{nome}**")
                        c1.caption(f"Simbolo: {symbol}")
                        c2.metric("Q.tà", f"{qty:.4f}")
                        if pmc > 0: st.caption(f"Prezzo medio carico: {pmc:.2f} €")
                    st.divider()
        if not found_any:
            st.warning("⚠️ Nessun saldo positivo trovato nei dati ricevuti.")
    else:
        st.error(f"Status: {status}")
        st.info("💡 Fai 'Nuova Versione' su Google Script per attivare la scansione azioni.")

with col_cx:
    st.subheader("🎯 Segnali AI")
    for a in ["Leonardo", "Intesa SP", "NVIDIA"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: **RIALZISTA**")
            st.button(f"Trade {a}", key=a)

with col_dx:
    st.subheader("📊 Grafico Leonardo")
    st.components.v1.html("""
        <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});
        </script>
        </div>
    """, height=460)
