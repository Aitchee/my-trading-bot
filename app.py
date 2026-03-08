import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# Recupero Chiave con pulizia estrema
try:
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip().replace('"', '').replace("'", "")
except Exception:
    st.error("Configura BITPANDA_API_KEY nei Secrets")
    st.stop()

# --- FUNZIONE API PROTETTA ---
def get_bp_data(endpoint):
    url = f"https://api.bitpanda.com/v1/{endpoint}"
    headers = {
        "X-API-KEY": BP_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json().get('data', [])
            # Verifichiamo che data sia effettivamente una lista per evitare il TypeError
            return data if isinstance(data, list) else [], 200
        return [], r.status_code
    except:
        return [], "Timeout"

# --- LAYOUT DASHBOARD ---
st.title("🚀 AI Financial Command Center")
st.caption(f"Status Live | {time.strftime('%H:%M:%S')}")

col_sx, col_cx, col_dx = st.columns([1, 1.2, 1.2])

with col_sx:
    st.subheader("💰 Portafoglio")
    fiat, status = get_bp_data("fiat-wallets")
    
    if status == 200:
        st.success("✅ Connesso a Bitpanda")
        for w in fiat:
            if w.get('attributes', {}).get('symbol') == 'EUR':
                bal = w['attributes']['balance']
                st.metric("Saldo Euro", f"{float(bal):.2f} €")
    else:
        st.error(f"Bitpanda Status: {status}")
        st.info("Se la chiave è confermata ma vedi 401, Bitpanda sta rifiutando la connessione dal server Cloud.")

    st.divider()
    st.subheader("💼 Asset Reali")
    # Protezione anti-crash: eseguiamo solo se lo status è OK
    if status == 200:
        assets, _ = get_bitpanda_data("asset-wallets")
        found = False
        for a in assets:
            # Controllo di sicurezza sulla struttura dei dati
            if isinstance(a, dict) and 'attributes' in a:
                bal = float(a['attributes']['balance'])
                if bal > 0.0001:
                    st.write(f"**{a['attributes']['cryptocoin_symbol']}**: {bal:.4f}")
                    found = True
        if not found: st.write("Nessun asset rilevato.")
    else:
        st.warning("Dati asset non disponibili (Errore API)")

with col_cx:
    st.subheader("🎯 Segnali AI Top 10")
    for m in ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Amazon", "Microsoft", "Meta", "Eni", "Enel"]:
        with st.expander(f"Analisi {m}"):
            st.write("Sentiment Analysis: In attesa di dati...")
            st.button("Trade", key=f"btn_{m}")

with col_dx:
    st.subheader("📊 Analisi Tecnica Leonardo")
    # Grafico fisso su Borsa Italiana
    st.components.v1.html("""
        <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"});
        </script>
        </div>
    """, height=420)

# Auto-refresh ogni 60 secondi
time.sleep(60)
st.rerun()
