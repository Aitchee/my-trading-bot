import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Terminal - Full Scan", layout="wide")

# Link fisso fornito
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

def recupera_tutto():
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=20)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Bridge"

st.title("🚀 AI Terminal: Deep Scan")
st.caption(f"Status Live | Scansione Totale Asset | {time.strftime('%H:%M:%S')}")

col_port, col_ai, col_chart = st.columns([1.3, 1, 1.2])

with col_port:
    st.subheader("💰 Portafoglio Reale")
    raw_data, status = recupera_tutto()
    
    if status == 200:
        st.success(f"✅ Ricevuti {len(raw_data)} pacchetti dati")
        
        found_any = False
        for item in raw_data:
            attr = item.get('attributes', {})
            # Recuperiamo tutti i possibili nomi del saldo (Bitpanda cambia tra Fiat e Asset)
            balance = float(attr.get('balance', 0) or attr.get('amount', 0))
            symbol = attr.get('symbol', '???')
            name = attr.get('name', symbol)
            
            # Se c'è un saldo positivo, lo mostriamo
            if balance > 0:
                found_any = True
                avg_price = float(attr.get('average_price', 0) or 0)
                
                with st.container():
                    c1, c2 = st.columns([2, 1])
                    if symbol == 'EUR':
                        c1.metric("EURO CASH", f"{balance:.2f} €")
                    else:
                        # Calcolo guadagno/perdita basato sul prezzo di carico (Pmc)
                        # Se Bitpanda non ci dà il prezzo live, mostriamo il Pmc e la quantità
                        c1.write(f"**{name}** ({symbol})")
                        c2.metric("Quantità", f"{balance:.4f}")
                        if avg_price > 0:
                            st.caption(f"Prezzo Medio Carico: {avg_price:.2f} €")
                    st.divider()
        
        if not found_any:
            st.warning("⚠️ Bitpanda non restituisce asset con saldo > 0.")
            with st.expander("Vedi Dati Raw (Debug)"):
                st.write(raw_data) # Questo ci dice cosa sta effettivamente arrivando
    else:
        st.error(f"Errore Bridge: {status}")

with col_ai:
    st.subheader("🎯 Segnali AI")
    for a in ["Leonardo", "Intesa SP", "Amazon", "NVIDIA"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: Bullish")
            st.button("Trade", key=a)

with col_chart:
    st.subheader("📊 Grafico Leonardo")
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
