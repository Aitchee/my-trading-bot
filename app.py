import streamlit as st
import requests
import datetime

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Link Google Bridge aggiornato (il tuo rimane lo stesso)
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

def recupera_dati():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Errore Bridge"

st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Portfolio Scanner | {datetime.datetime.now().strftime('%H:%M:%S')}")

if st.button("🔄 SINCRONIZZA PORTAFOGLIO"):
    st.rerun()

st.divider()
col_sx, col_cx, col_dx = st.columns([1.5, 1, 1.2])

with col_sx:
    st.subheader("💰 Asset & Performance")
    data, status = recupera_dati()
    
    if status == 200:
        found = False
        for item in data:
            attr = item.get('attributes', {})
            # Recuperiamo il saldo indipendentemente dal nome del campo (balance o amount)
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            
            if qty > 0:
                found = True
                nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft"}
                nome_asset = nomi.get(symbol, attr.get('name', symbol))
                
                # Prezzo medio di carico (Pmc)
                pmc = float(attr.get('average_price', 0))
                
                with st.container():
                    c1, c2 = st.columns([1.5, 1])
                    if symbol == "EUR":
                        c1.metric("EURO LIQUIDITÀ", f"{qty:.2f} €")
                    else:
                        c1.write(f"**{nome_asset}** ({symbol})")
                        c1.caption(f"Posizione: {qty:.4f} unità")
                        
                        if pmc > 0:
                            val_attuale = qty * pmc # Stima valore
                            c2.metric("Valore", f"{val_attuale:.2f} €", "Live")
                            st.caption(f"Prezzo medio carico: {pmc:.2f} €")
                    st.divider()
        
        if not found:
            st.warning("⚠️ Nessun asset trovato. Controlla la 'Nuova Versione' su Google Script.")
            with st.expander("Ispeziona Dati Raw"):
                st.write(data)
    else:
        st.error(f"Errore: {status}")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for a in ["Leonardo", "Intesa SP", "NVIDIA", "Amazon"]:
        with st.expander(f"Analisi {a}"):
            st.write(f"Sentiment {a}: **RIALZISTA**")
            st.button(f"Trade {a}", key=f"t_{a}")

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
