import streamlit as st
import requests
import time

# --- SETUP PAGINA ---
st.set_page_config(page_title="AI Financial Terminal", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    # Pulizia profonda delle chiavi da spazi o virgolette extra
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip().replace('"', '').replace("'", "")
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).strip().replace('"', '').replace("'", "")
except Exception as e:
    st.error("Configura le chiavi nei Secrets di Streamlit")
    st.stop()

# --- FUNZIONE API ---
def get_data(endpoint):
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
st.caption(f"Aggiornamento Live | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    fiat_wallets, status = get_data("fiat-wallets")
    
    if status == 200:
        for w in fiat_wallets:
            if w['attributes']['symbol'] == 'EUR':
                st.metric("Saldo Euro", f"{float(w['attributes']['balance']):.2f} €")
    else:
        st.error(f"Bitpanda API Error: {status}")
        st.info("Se vedi 401: la chiave è errata. Se vedi 403: mancano permessi 'Read' sulla chiave.")

    st.divider()
    st.subheader("💼 Asset Reali")
    # Protezione riga 54: carichiamo asset solo se lo status è OK
    if status == 200:
        assets, _ = get_data("asset-wallets")
        found = False
        for a in assets:
            bal = float(a['attributes']['balance'])
            if bal > 0.0001:
                st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")
                found = True
        if not found: st.write("Nessun asset trovato.")
    else:
        st.warning("In attesa di connessione valida...")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    # Qui usiamo la tua News API
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Ferrari", "Apple"]
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write(f"News sentiment per {m}...")
            st.button(f"Trade {m}", key=m)

with col_dx:
    st.subheader("📊 Grafico Leonardo")
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
