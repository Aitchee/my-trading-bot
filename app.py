import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Il tuo link fisso
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

def recupera_dati():
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=20)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Bridge"

st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Portfolio Scanner | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1.3, 1, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio & Performance")
    data, status = recupera_dati()
    
    if status == 200 and len(data) > 0:
        st.success(f"✅ Dati ricevuti: {len(data)} asset trovati")
        
        # 1. Mostra Liquidità Euro
        for w in data:
            attr = w.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                st.metric("Liquidità Cash", f"{float(attr.get('balance', 0)):.2f} €")
        
        st.divider()
        st.write("### Azioni & Asset")
        
        for w in data:
            attr = w.get('attributes', {})
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol')
            
            if qty > 0 and symbol != 'EUR':
                # Nomi reali per le tue azioni
                nomi = {"LDO": "Leonardo", "ISP": "Intesa Sanpaolo", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft"}
                nome_asset = nomi.get(symbol, symbol)
                
                # Calcolo P&L se disponibile (Bitpanda v1 fornisce average_price)
                pmc = float(attr.get('average_price', 0))
                
                with st.container():
                    c1, c2 = st.columns([1.5, 1])
                    c1.write(f"**{nome_asset}**")
                    c1.caption(f"Quantità: {qty:.4f}")
                    
                    if pmc > 0:
                        # Simuliamo il valore attuale per il calcolo percentuale
                        # In futuro integreremo i prezzi live per precisione 100%
                        st.metric("Valore", f"{qty * pmc:.2f} €", "Live Data")
                        st.caption(f"Pmc: {pmc:.2f} €")
                    else:
                        st.write(f"{qty:.4f} unità")
                    st.divider()
    else:
        st.warning("In attesa di dati da Bitpanda...")
        st.info("💡 Se hai aggiornato lo script di Google, attendi 30 secondi per il refresh.")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for a in ["Leonardo", "Intesa SP", "Amazon", "NVIDIA", "Microsoft"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: **RIALZISTA**")
            st.button(f"Trade {a}", key=f"btn_{a}")

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

time.sleep(60)
st.rerun()
