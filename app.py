import streamlit as st
import requests
import time

# 1. Setup Pagina
st.set_page_config(page_title="Trading Terminal AI", layout="wide")

# 2. Recupero Chiavi Pulito
try:
    # Pulizia forzata di ogni possibile carattere sporco nelle chiavi
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).replace('"', '').replace("'", "").strip()
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).replace('"', '').replace("'", "").strip()
except Exception as e:
    st.error(f"Errore critico Secrets: {e}")
    st.stop()

# 3. Funzioni Dati (con gestione errori per non rompere la grafica)
def get_bitpanda_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {"X-API-KEY": BP_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Timeout"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Ultimo Refresh: {time.strftime('%H:%M:%S')}")

# Creazione Colonne Fisse
col_saldo, col_signals, col_graph = st.columns([1, 1.2, 1.2])

with col_saldo:
    st.subheader("💰 Portafoglio")
    
    # Recupero Saldo
    fiat_data, status = get_bitpanda_data("fiat-wallets")
    if status == 200:
        for w in fiat_data:
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
    else:
        st.error(f"Errore API Bitpanda: {status}")
        st.info("💡 Verifica che la chiave nei Secrets sia identica a quella su Bitpanda (senza spazi).")

    st.divider()
    st.subheader("💼 Asset Reali")
    asset_data, _ = get_bitpanda_data("asset-wallets")
    found = False
    for a in asset_data:
        bal = float(a['attributes']['balance'])
        if bal > 0.0001:
            st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")
            found = True
    if not found and status == 200: st.write("Nessun asset nel portafoglio.")

with col_signals:
    st.subheader("🎯 Top 10 Segnali AI")
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Ferrari", "Apple", "Amazon", "Microsoft", "Meta", "Google", "Enel"]
    
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write(f"Ricerca news in corso per {m}...")
            st.button("Forza Acquisto", key=f"buy_{m}")

with col_graph:
    st.subheader("📊 Grafico Real-Time")
    # Widget TradingView con protezione altezza
    chart_html = """
    <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "MIL:LDO", "interval": "D",
          "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "it",
          "enable_publishing": false, "hide_top_toolbar": false, "save_image": false
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=460)

# Sidebar di controllo
st.sidebar.header("⚙️ Bot Settings")
auto = st.sidebar.toggle("Pilota Automatico")
st.sidebar.info("Il bot si aggiorna ogni 60s")

# Refresh automatico
time.sleep(60)
st.rerun()
