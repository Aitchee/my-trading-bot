import streamlit as st
import requests
import time

# --- SETUP ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip().replace('"', '').replace("'", "")
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).strip()
except Exception:
    st.error("Configura i Secrets su Streamlit!")
    st.stop()

# --- FUNZIONE API CON USER-AGENT (EVITA BLOCCHI) ---
def get_bitpanda_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    # Aggiungiamo User-Agent per simulare un browser reale
    headers = {
        "X-API-KEY": BP_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), 200
        return [], r.status_code
    except Exception as e:
        return [], f"Errore Connessione: {str(e)[:20]}"

# --- INTERFACCIA ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    # Proviamo a leggere il saldo Fiat
    fiat_wallets, status = get_bitpanda_data("fiat-wallets")
    
    if status == 200:
        st.success("✅ Bitpanda Connesso")
        for w in fiat_wallets:
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
    elif status == 401:
        st.error("❌ Bitpanda dice: Chiave Non Autorizzata (401)")
        st.info("⚠️ Verifica su Bitpanda: 1. IP Whitelist deve essere VUOTO. 2. Permessi Saldo/Trading attivi.")
    else:
        st.error(f"Status API: {status}")

    st.divider()
    st.subheader("💼 Asset Reali")
    if status == 200:
        assets, _ = get_bitpanda_data("asset-wallets")
        for a in assets:
            bal = float(a['attributes']['balance'])
            if bal > 0.0001:
                st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for m in ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari"]:
        with st.expander(f"Analisi {m}"):
            st.write(f"News sentiment per {m}...")
            st.button(f"Trade {m}", key=m)

with col_dx:
    st.subheader("📊 Analisi Tecnica")
    # Simbolo corretto per Borsa Italiana
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

# Refresh
time.sleep(60)
st.rerun()
