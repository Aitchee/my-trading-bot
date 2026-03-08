import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Il tuo link Google Bridge
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

def recupera_dati():
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=20)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Bridge"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Portfolio Scanner | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1.3, 1, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio & Performance")
    data, status = recupera_dati()
    
    if status == 200 and len(data) > 0:
        st.success(f"✅ Dati ricevuti: {len(data)} asset trovati")
        
        # 1. Liquidità Euro
        for w in data:
            attr = w.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                st.metric("Liquidità Cash", f"{float(attr.get('balance', 0)):.2f} €")
        
        st.divider()
        st.write("### Azioni & Asset Legacy")
        
        for w in data:
            attr = w.get('attributes', {})
            qty = float(attr.get('balance', 0) or 0)
            symbol = attr.get('symbol')
            
            if qty > 0 and symbol != 'EUR':
                # Nomi reali dai tuoi screenshot
                nomi = {"LDO": "Leonardo", "ISP": "Intesa Sanpaolo", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft"}
                nome_asset = nomi.get(symbol, symbol)
                pmc = float(attr.get('average_price', 0)) # Prezzo Medio Carico
                
                with st.container():
                    st.write(f"**{nome_asset}** ({symbol})")
                    # Calcolo indicativo valore (Qty * Pmc)
                    valore = qty * pmc if pmc > 0 else 0
                    st.metric(label="Valore Stimato", value=f"{valore:.2f} €" if valore > 0 else "N/D", delta=f"Quantità: {qty:.4f}")
                    if pmc > 0: st.caption(f"Prezzo Medio Carico: {pmc:.2f} €")
                    st.divider()
    else:
        st.warning("In attesa di dati reali...")
        st.info("💡 Se hai fatto 'Nuova Versione' su Google, attendi il prossimo refresh.")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for a in ["Leonardo", "Intesa SP", "Amazon", "NVIDIA", "Apple"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: **RIALZISTA**")
            st.button(f"Analisi {a}", key=f"btn_{a}")

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
