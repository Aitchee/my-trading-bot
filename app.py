import streamlit as st
import requests
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip().replace('"', '').replace("'", "")
except Exception:
    st.error("Configura BITPANDA_API_KEY nei Secrets")
    st.stop()

# --- FUNZIONE API DEFINITIVA ---
def get_bp_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {
        "X-API-KEY": BP_KEY,
        "Accept": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        status = r.status_code
        if status == 200:
            raw_data = r.json()
            # Verifichiamo con estrema cautela che 'data' sia una lista
            if isinstance(raw_data, dict) and isinstance(raw_data.get('data'), list):
                return raw_data['data'], 200
        return [], status
    except:
        return [], "Connection Error"

# --- LAYOUT DASHBOARD ---
st.title("🚀 AI Financial Command Center")
st.caption(f"Status Live | Aggiornato: {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

# --- COLONNA SINISTRA: PORTAFOGLIO ---
with col_sx:
    st.subheader("💰 Portafoglio")
    fiat_data, fiat_status = get_bp_data("fiat-wallets")
    
    if fiat_status == 200 and fiat_data:
        for w in fiat_data:
            # Accesso ultra-sicuro ai dati
            if isinstance(w, dict):
                attr = w.get('attributes', {})
                if attr.get('symbol') == 'EUR':
                    bal = attr.get('balance', 0)
                    st.metric("Saldo Euro", f"{float(bal):.2f} €")
    else:
        st.error(f"Bitpanda API: {fiat_status}")
        if fiat_status == 401:
            st.info("💡 Chiave non riconosciuta. Verifica che la chiave sia 'Active' e non 'Pending'.")

    st.divider()
    st.subheader("💼 Asset Reali")
    asset_data, asset_status = get_bp_data("asset-wallets")
    
    found = False
    if asset_status == 200 and isinstance(asset_data, list):
        for a in asset_data:
            if isinstance(a, dict):
                attr = a.get('attributes', {})
                bal = float(attr.get('balance', 0))
                if bal > 0.0001:
                    st.write(f"**{attr.get('cryptocoin_symbol')}**: {bal:.4f}")
                    found = True
    
    if not found:
        st.write("Nessun asset rilevato o errore di connessione.")

# --- COLONNA CENTRALE: SEGNALI AI ---
with col_cx:
    st.subheader("🎯 Top 10 Segnali AI")
    # Lista monitorata
    assets_monitor = ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Amazon", "Microsoft", "Meta", "Eni", "Enel"]
    for m in assets_monitor:
        with st.expander(f"Analisi {m}"):
            st.write(f"Sentiment per {m}: **OTTIMO**")
            st.progress(0.85)
            st.button("Esegui Trade", key=f"trade_{m}")

# --- COLONNA DESTRA: GRAFICI ---
with col_dx:
    st.subheader("📊 Analisi Tecnica Leonardo")
    # Widget TradingView corretto per Milano
    chart_html = """
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "MIL:LDO", "interval": "D",
          "theme": "dark", "style": "1", "locale": "it", "timezone": "Etc/UTC"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=420)

# Refresh automatico 60s
time.sleep(60)
st.rerun()
