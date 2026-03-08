import streamlit as st
import requests
import time

# 1. Impostazioni pagina
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# 2. INCOLLA QUI IL TUO URL DI GOOGLE SCRIPT
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxT8Z-dfwGB9oBTwneveMHAXF9DdWxE-z5GYKlbnStSyX1OGuw_qq2Q4TqTPf-TEfhP/exec"

# 3. Funzione di recupero dati tramite il "Ponte"
def recupera_dati_ponte():
    try:
        # Chiamata a Google Script invece che a Bitpanda direttamente
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except Exception as e:
        return [], f"Errore: {str(e)[:20]}"

# --- INTERFACCIA GRAFICA ---
st.title("🚀 AI Financial Terminal (Google Bridge)")
st.caption(f"Status: Collegato tramite Proxy Google | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    data, status = recupera_dati_ponte()
    
    if status == 200:
        st.success("✅ Dati Ricevuti")
        for w in data:
            # Cerchiamo il saldo EUR
            if w.get('attributes', {}).get('symbol') == 'EUR':
                bal = w['attributes']['balance']
                st.metric("Saldo Bitpanda (EUR)", f"{float(bal):.2f} €")
    else:
        st.error(f"Errore Connessione: {status}")
        st.info("💡 Se vedi 401, controlla di aver messo la Chiave API corretta dentro lo script di Google.")

with col_cx:
    st.subheader("🎯 Segnali AI")
    for m in ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari"]:
        with st.expander(f"Analisi {m}"):
            st.write("Sentiment: **RIALZISTA**")
            st.button(f"Trade {m}", key=m)

with col_dx:
    st.subheader("📊 Grafico Leonardo (Milano)")
    st.components.v1.html("""
        <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
        </div>
    """, height=420)

# Refresh automatico ogni minuto
time.sleep(60)
st.rerun()
