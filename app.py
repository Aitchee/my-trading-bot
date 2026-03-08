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

# --- FUNZIONE API ULTRA-PROTETTA ---
def get_bp_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {
        "X-API-KEY": BP_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            res_json = r.json()
            # Verifichiamo che la risposta contenga la lista 'data'
            if isinstance(res_json, dict) and 'data' in res_json:
                return res_json['data'], 200
        return [], r.status_code
    except Exception as e:
        return [], f"Errore: {str(e)[:15]}"

# --- LAYOUT DASHBOARD ---
st.title("🚀 AI Financial Command Center")
st.caption(f"Ultimo aggiornamento: {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    fiat_data, status = get_bp_data("fiat-wallets")
    
    if status == 200 and fiat_data:
        st.success("✅ Connesso")
        for w in fiat_data:
            # Controllo strutturale per evitare il crash alla riga 56
            attr = w.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                bal = attr.get('balance', 0)
                st.metric("Saldo Euro", f"{float(bal):.2f} €")
    else:
        st.error(f"Bitpanda Status: {status}")
        if status == 401:
            st.info("💡 La chiave è attiva ma il server Cloud è bloccato. Prova a rigenerare la chiave senza IP Whitelist.")

    st.divider()
    st.subheader("💼 Asset Reali")
    asset_data, asset_status = get_bp_data("asset-wallets")
    
    found = False
    if asset_status == 200 and asset_data:
        for a in asset_data:
            attr = a.get('attributes', {})
            bal = float(attr.get('balance', 0))
            if bal > 0.0001:
                st.write(f"**{attr.get('cryptocoin_symbol')}**: {bal:.4f}")
                found = True
    
    if not found:
        st.write("Nessun asset rilevato.")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    # News e Segnali (Simulati per ora)
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Amazon", "Microsoft", "Meta", "Eni", "Enel"]
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write("Sentiment rilevato: **POSITIVO**")
            st.caption("Motivo: Volume di scambi in aumento e news favorevoli.")
            st.button("Avvia Trade", key=f"btn_{m}")

with col_dx:
    st.subheader("📊 Analisi Tecnica Leonardo")
    # Grafico TradingView
    chart_html = """
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=420)

# Refresh automatico ogni 60 secondi
time.sleep(60)
st.rerun()
