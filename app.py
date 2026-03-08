import streamlit as st
import requests
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Il tuo nuovo link aggiornato
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

def recupera_dati():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Connessione"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
with col_h2:
    if st.button("🔄 AGGIORNA ORA"):
        st.rerun()

st.divider()
col_sx, col_cx, col_dx = st.columns([1.5, 1, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio Reale")
    with st.spinner('Scansione asset in corso...'):
        data, status = recupera_dati()
    
    if status == 200:
        found_any = False
        # Scansione di ogni pacchetto dati ricevuto
        for item in data:
            attr = item.get('attributes', {})
            # Bitpanda usa balance per cash e spesso amount o balance per asset legacy
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            
            if qty > 0:
                found_any = True
                nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft"}
                nome = nomi.get(symbol, attr.get('name', symbol))
                
                with st.container():
                    c1, c2 = st.columns([1.5, 1])
                    if symbol == "EUR":
                        c1.metric("EURO LIQUIDITÀ", f"{qty:.2f} €")
                    else:
                        pmc = float(attr.get('average_price', 0))
                        c1.write(f"**{nome}**")
                        c1.caption(f"Asset: {symbol}")
                        c2.metric("Quantità", f"{qty:.4f}")
                        if pmc > 0: st.caption(f"Pmc: {pmc:.2f} €")
                    st.divider()
        
        if not found_any:
            st.warning("Nessun titolo trovato con saldo positivo.")
            with st.expander("Debug Dati Raw"):
                st.write(data)
    else:
        st.error(f"Status Bridge: {status}")

with col_cx:
    st.subheader("🎯 Segnali AI")
    for a in ["Leonardo", "Intesa SP", "Amazon"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: **RIALZISTA**")
            st.button(f"Trade {a}", key=a)

with col_dx:
    st.subheader("📊 Analisi Tecnica")
    st.components.v1.html(f"""
        <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"}});
        </script>
        </div>
    """, height=460)
