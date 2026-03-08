import streamlit as st
import requests
import datetime

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Link Google Bridge Fisso
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

# --- 2. FUNZIONE RECUPERO DATI ---
def recupera_dati():
    try:
        # Timeout ridotto per non bloccare l'app
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except Exception as e:
        return [], "Timeout/Errore"

# --- 3. INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
col_header_1, col_header_2 = st.columns([3, 1])

with col_header_1:
    st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
with col_header_2:
    if st.button("🔄 AGGIORNA DATI"):
        st.rerun()

st.divider()

col_sx, col_cx, col_dx = st.columns([1.3, 1, 1.2])

# --- COLONNA 1: PORTAFOGLIO ---
with col_sx:
    st.subheader("💰 Portafoglio")
    with st.spinner('Caricamento asset...'):
        data, status = recupera_dati()
    
    if status == 200 and len(data) > 0:
        # Liquidità Euro
        for w in data:
            attr = w.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                bal = float(attr.get('balance', 0))
                st.metric("Liquidità Cash", f"{bal:.2f} €")
        
        st.divider()
        st.write("### I Tuoi Titoli")
        
        found = False
        for w in data:
            attr = w.get('attributes', {})
            qty = float(attr.get('balance', 0) or 0)
            symbol = attr.get('symbol')
            
            if qty > 0 and symbol != 'EUR':
                found = True
                nomi = {"LDO": "Leonardo", "ISP": "Intesa Sanpaolo", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple"}
                nome_asset = nomi.get(symbol, symbol)
                pmc = float(attr.get('average_price', 0))
                
                with st.container():
                    st.write(f"**{nome_asset}** ({symbol})")
                    valore = qty * pmc if pmc > 0 else 0
                    st.metric(label="Dettaglio", value=f"{qty:.4f} Q.tà", delta=f"{valore:.2f} €" if valore > 0 else None)
                    if pmc > 0: st.caption(f"Prezzo Medio Carico: {pmc:.2f} €")
                    st.divider()
        if not found:
            st.info("Nessun titolo azionario rilevato.")
    else:
        st.error(f"⚠️ Status: {status}")
        st.info("Se non vedi dati, assicurati di aver fatto 'Nuova Versione' su Google Script.")

# --- COLONNA 2: SEGNALI AI ---
with col_cx:
    st.subheader("🎯 Segnali AI")
    for a in ["Leonardo", "Intesa SP", "Amazon", "NVIDIA"]:
        with st.expander(f"Analisi {a}"):
            st.write("Sentiment: **RIALZISTA**")
            st.button(f"Analisi {a}", key=f"btn_{a}")

# --- COLONNA 3: GRAFICO ---
with col_dx:
    st.subheader("📊 Analisi Tecnica")
    st.components.v1.html("""
        <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize":true,"symbol":"MIL:LDO","interval":"D","theme":"dark","style":"1","locale":"it"});
        </script>
        </div>
    """, height=460)
