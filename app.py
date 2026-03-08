import streamlit as st
import requests
import datetime

# 1. Configurazione Pagina
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
        return [], "Errore Bridge"

# 2. Interfaccia
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
            # Leggiamo saldo per azioni legacy e contanti
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            
            if qty > 0:
                found = True
                nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "EUR": "Euro"}
                nome_asset = nomi.get(symbol, symbol)
                pmc = float(attr.get('average_price', 0))
                
                with st.container():
                    c1, c2 = st.columns([2, 1])
                    if symbol == "EUR":
                        c1.metric("Liquidità Cash", f"{qty:.2f} €")
                    else:
                        c1.write(f"**{nome_asset}**")
                        c2.metric("Q.tà", f"{qty:.4f}")
                        if pmc > 0:
                            st.caption(f"Pmc: {pmc:.2f} € | Valore: {qty*pmc:.2f} €")
                    st.divider()
        if not found:
            st.warning("Nessun saldo positivo trovato.")
    else:
        st.error(f"Status Bridge: {status}")
        st.info("💡 Se vedi 200 ma non vedi dati, assicurati di aver fatto 'Nuova Versione' su Google Script.")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for a in ["Leonardo", "Intesa SP", "Amazon", "NVIDIA"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment AI: **RIALZISTA**")
            st.button(f"Trade {a}", key=f"t_{a}")

with col_dx:
    st.subheader("📊 Analisi Tecnica Leonardo")
    st.components.v1.html("""
        <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});
        </script>
        </div>
    """, height=460)
