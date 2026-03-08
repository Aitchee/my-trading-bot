import streamlit as st
import requests
import datetime

# 1. Configurazione Interfaccia
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Link Google Bridge Fisso
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

def recupera_dati():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Connessione"

# 2. Header Dashboard
st.title("🚀 AI Financial Terminal")
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.caption(f"Ultimo aggiornamento live: {datetime.datetime.now().strftime('%H:%M:%S')}")
with col_h2:
    if st.button("🔄 SINCRONIZZA ORA"):
        st.rerun()

st.divider()

# 3. Layout a tre colonne
col_sx, col_cx, col_dx = st.columns([1.5, 1, 1.2])

with col_sx:
    st.subheader("💰 Asset & Performance")
    data, status = recupera_dati()
    
    if status == 200 and len(data) > 0:
        found = False
        for item in data:
            attr = item.get('attributes', {})
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            
            if qty > 0:
                found = True
                nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "EUR": "Liquidità Euro"}
                nome_asset = nomi.get(symbol, attr.get('name', symbol))
                
                with st.container():
                    c1, c2 = st.columns([2, 1])
                    if symbol == "EUR":
                        c1.metric(nome_asset, f"{qty:.2f} €")
                    else:
                        pmc = float(attr.get('average_price', 0))
                        c1.write(f"**{nome_asset}**")
                        c2.metric("Q.tà", f"{qty:.4f}")
                        if pmc > 0: st.caption(f"Pmc: {pmc:.2f} €")
                    st.divider()
        if not found:
            st.warning("Nessun asset con saldo positivo rilevato.")
    else:
        st.error(f"Status Bridge: {status}")
        st.info("💡 Assicurati di aver creato una 'Nuova Versione' su Google Script.")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for a in ["Leonardo", "Intesa SP", "Amazon", "NVIDIA"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: **RIALZISTA (88%)**")
            st.button(f"Trade {a}", key=f"btn_{a}")

with col_dx:
    st.subheader("📊 Grafico Leonardo (MIL)")
    st.components.v1.html("""
        <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});
        </script>
        </div>
    """, height=460)
