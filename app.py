import streamlit as st
import requests
import time

# --- SETUP PAGINA ---
st.set_page_config(page_title="AI Financial Terminal", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    # Pulizia totale della chiave da ogni carattere strano
    raw_bp_key = str(st.secrets["BITPANDA_API_KEY"])
    BP_KEY = raw_bp_key.strip().replace('"', '').replace("'", "")
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).strip()
except Exception:
    st.error("⚠️ Chiavi non trovate nei Secrets.")
    st.stop()

# --- FUNZIONE API ---
def get_bp_data(endpoint):
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
st.caption(f"Status Live | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    # Proviamo a leggere il saldo Fiat
    fiat_wallets, status = get_bp_data("fiat-wallets")
    
    if status == 200:
        st.success("✅ Connessione Bitpanda riuscita!")
        for w in fiat_wallets:
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
    elif status == 401:
        st.error("❌ Errore 401: Chiave non valida.")
        st.info("Consiglio: Ricrea la chiave su Bitpanda e incollala senza spazi.")
    else:
        st.error(f"Bitpanda API Status: {status}")

    st.divider()
    st.subheader("💼 Asset Reali")
    if status == 200:
        assets, _ = get_bp_data("asset-wallets")
        found = False
        for a in assets:
            bal = float(a['attributes']['balance'])
            if bal > 0.0001:
                st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")
                found = True
        if not found: st.write("Nessun asset trovato.")
    else:
        st.warning("In attesa di chiave valida...")

with col_cx:
    st.subheader("🎯 Top 10 Segnali AI")
    # Visualizzazione semplificata per evitare crash
    for m in ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari"]:
        with st.expander(f"Analisi {m}"):
            st.write("Segnale basato su News API...")
            st.button(f"Trade {m}", key=m)

with col_dx:
    st.subheader("📊 Analisi Tecnica")
    # Grafico con simbolo corretto per Milano
    chart_html = """
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=420)

# Refresh automatico 60s
time.sleep(60)
st.rerun()
