import streamlit as st
import requests
import time

# --- SETUP PAGINA ---
st.set_page_config(page_title="AI Financial Terminal", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip().replace('"', '').replace("'", "")
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).strip().replace('"', '').replace("'", "")
except Exception as e:
    st.error("⚠️ Configura le chiavi nei Secrets di Streamlit (BITPANDA_API_KEY e NEWS_API_KEY)")
    st.stop()

# --- FUNZIONE API BITPANDA ---
def get_bitpanda_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {"X-API-KEY": BP_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except:
        return [], "Timeout"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Refresh: {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

# --- COLONNA 1: SALDO E ASSET ---
with col_sx:
    st.subheader("💰 Portafoglio")
    # Fiat Wallets per il saldo in Euro
    fiat_wallets, status = get_bitpanda_data("fiat-wallets")
    
    if status == 200:
        found_eur = False
        for w in fiat_wallets:
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
                found_eur = True
        if not found_eur:
            st.warning("Nessun portafoglio EUR trovato.")
    elif status == 401:
        st.error("❌ Errore 401: Chiave non valida.")
    elif status == 403:
        st.error("❌ Errore 403: Permessi mancanti (Saldo/Transazione).")
    else:
        st.error(f"Errore Bitpanda: {status}")

    st.divider()
    st.subheader("💼 Asset Reali")
    # Asset Wallets per le crypto/azioni possedute
    if status == 200:
        assets, _ = get_bitpanda_data("asset-wallets")
        found_asset = False
        for a in assets:
            bal = float(a['attributes']['balance'])
            if bal > 0.0001:
                st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")
                found_asset = True
        if not found_asset: st.write("Nessun asset in possesso.")

# --- COLONNA 2: NEWS & SEGNALI ---
with col_cx:
    st.subheader("🎯 Top 10 Segnali AI")
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Ferrari", "Apple", "Amazon", "Microsoft", "Meta", "Google", "Enel"]
    
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write(f"Sentiment Analysis per {m}...")
            if st.button(f"Trade {m}", key=f"btn_{m}"):
                st.toast(f"Ordine simulato per {m}")

# --- COLONNA 3: GRAFICO ---
with col_dx:
    st.subheader("📊 Analisi Tecnica")
    chart_html = """
    <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "MIL:LDO", "interval": "D",
          "theme": "dark", "style": "1", "locale": "it", "timezone": "Etc/UTC"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=460)

# --- REFRESH AUTOMATICO ---
st.sidebar.info("Il bot si aggiorna ogni 60s")
time.sleep(60)
st.rerun()
