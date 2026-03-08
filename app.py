import streamlit as st
import requests
import time

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Trading Terminal PRO", layout="wide")

# --- 2. CONFIGURAZIONE PONTE GOOGLE ---
# Sostituisci con il tuo URL /exec
GOOGLE_BRIDGE_URL = "INCOLLA_QUI_IL_TUO_URL_DI_GOOGLE"

# --- 3. FUNZIONE DI RECUPERO DATI ---
def recupera_dati_globali():
    if "GOOGLE" in GOOGLE_BRIDGE_URL:
        return [], "URL_MANCANTE"
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=20)
        if r.status_code == 200:
            res_json = r.json()
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
        found_eur = False
        for wallet in data:
            attr = wallet.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                bal = float(attr.get('balance', 0))
                st.metric("Saldo Disponibile (EUR)", f"{bal:.2f} €")
                found_eur = True
        if not found_eur:
            st.info("Nessun saldo EUR rilevato.")
    else:
        st.error(f"⚠️ Errore: {status}")

with col_ai:
    st.subheader("🎯 Segnali AI Top 10")
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Leonardo"]
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write(f"Sentiment {m}: **RIALZISTA**")
            st.button(f"Trade {m}", key=f"btn_{m}")

with col_chart:
    st.subheader("📊 Analisi Tecnica Leonardo")
    # HTML del grafico - Qui è dove c'era l'errore di sintassi
    chart_html = """
    <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "MIL:LDO",
          "interval": "D",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "it",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tv_chart"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=460)

# --- 5. REFRESH ---
time.sleep(60)
st.rerun()
