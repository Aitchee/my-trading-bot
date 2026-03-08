import streamlit as st
import requests
import time

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Trading Terminal PRO", layout="wide")

# --- 2. CONFIGURAZIONE PONTE GOOGLE ---
# Incolla qui il tuo URL di Google Script (quello che finisce con /exec)
GOOGLE_BRIDGE_URL = "IL_TUO_URL_DI_GOOGLE_QUI"

# --- 3. FUNZIONE DI RECUPERO DATI ---
def recupera_dati_globali():
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=20)
        if r.status_code == 200:
            res_json = r.json()
            # Restituisce la lista 'data' se presente, altrimenti una lista vuota
            return res_json.get('data', []), 200
        return [], r.status_code
    except Exception as e:
        return [], f"Errore: {str(e)[:20]}"

# --- 4. INTERFACCIA UTENTE ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Proxy: Google Apps Script | {time.strftime('%H:%M:%S')}")

col_port, col_ai, col_chart = st.columns([1, 1.2, 1.2])

with col_port:
    st.subheader("💰 Portafoglio")
    data, status = recupera_dati_globali()
    
    if status == 200:
        st.success("✅ Connesso")
        
        eur_balance = 0.0
        found_eur = False
        
        # Scansione accurata di tutti i wallet ricevuti
        for wallet in data:
            attr = wallet.get('attributes', {})
            symbol = attr.get('symbol')
            
            # Controllo Saldo Euro
            if symbol == 'EUR':
                eur_balance = float(attr.get('balance', 0))
                st.metric("Saldo Disponibile (EUR)", f"{eur_balance:.2f} €")
                found_eur = True
        
        if not found_eur:
            st.info("Nessun saldo EUR rilevato nel wallet.")

        st.divider()
        st.subheader("💼 Asset Digitali")
        # Visualizziamo altri asset con saldo positivo
        asset_found = False
        for wallet in data:
            attr = wallet.get('attributes', {})
            bal = float(attr.get('balance', 0))
            sym = attr.get('symbol')
            if bal > 0 and sym != 'EUR':
                st.write(f"**{sym}**: {bal:.4f}")
                asset_found = True
        
        if not asset_found:
            st.caption("Nessuna crypto o azione rilevata.")

    else:
        st.error(f"⚠️ Errore Connessione: {status}")
        st.info("Verifica che la chiave Bitpanda sia corretta dentro Google Script.")

with col_ai:
    st.subheader("🎯 Segnali AI Top 10")
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Amazon", "Microsoft", "Meta", "Eni", "Leonardo"]
    
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write(f"Sentiment attuale per {m}: **RIALZISTA**")
            st.progress(0.85)
            st.button(f"Trade {m}", key=f"btn_{m}")

with col_chart:
    st.subheader("📊 Analisi Leonardo (Milano)")
    # Widget TradingView stabile
    chart_html = """
    <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "MIL:LDO", "interval": "D",
          "theme": "dark", "style":
