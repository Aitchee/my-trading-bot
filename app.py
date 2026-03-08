import streamlit as st
import requests
import time

# 1. Configurazione Pagina
st.set_page_config(page_title="Trading Terminal PRO", layout="wide")

# 2. Recupero Chiavi con Pulizia Automatica
try:
    # Usiamo strip() per togliere spazi invisibili che spesso causano il "Chiave Errata"
    BP_KEY = str(st.secrets["BITPANDA_API_KEY"]).strip()
    NW_KEY = str(st.secrets["NEWS_API_KEY"]).strip()
    st.sidebar.success("✅ Sistema Collegato")
except Exception as e:
    st.error(f"❌ Errore nei Secrets: {e}")
    st.stop()

# 3. Funzione Saldo Fiat (Bitpanda)
def prendi_saldo():
    url = "https://api.bitpanda.com/v1/fiat-wallets"
    headers = {"X-API-KEY": BP_KEY}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json().get('data', [])
            for wallet in data:
                if wallet['attributes']['symbol'] == 'EUR':
                    return f"{float(wallet['attributes']['balance']):.2f} €"
            return "0.00 €"
        else:
            # Questo ti dirà nei log se il problema è 401 (chiave) o 403 (permessi)
            return f"Errore API {r.status_code}"
    except:
        return "Errore Sync"

# 4. Funzione Asset (Bitpanda)
def prendi_asset():
    url = "https://api.bitpanda.com/v1/asset-wallets"
    headers = {"X-API-KEY": BP_KEY}
    assets = {}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json().get('data', [])
            for w in data:
                bal = float(w['attributes']['balance'])
                if bal > 0.001:
                    simbolo = w['attributes']['cryptocoin_symbol']
                    assets[simbolo] = bal
            return assets
    except:
        pass
    return None

# --- INTERFACCIA ---
st.title("🤖 AI Trading Terminal")

col_left, col_mid, col_right = st.columns([1, 1.5, 1])

with col_left:
    st.header("💰 Il Tuo Saldo")
    saldo_reale = prendi_saldo()
    st.metric("Saldo Bitpanda (EUR)", saldo_reale)
    
    st.header("💼 Asset Reali")
    miei_asset = prendi_asset()
    if miei_asset:
        for s, v in miei_asset.items():
            st.write(f"**{s}**: {v}")
    else:
        st.write("Nessun asset rilevato.")

with col_mid:
    st.header("🎯 Segnali AI Top 10")
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Ferrari", "Apple", "Amazon", "Microsoft", "Meta", "Enel", "Leonardo"]
    for m in monitorati:
        st.button(f"Analizza {m}", key=m)

with col_right:
    st.header("📊 Grafico Live")
    # Grafico Leonardo fisso
    st.components.v1.html(f"""
        <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{"autosize": true, "symbol": "MIL:LDO", "interval": "D", "theme": "dark", "style": "1", "locale": "it"}});
        </script>
        </div>
    """, height=420)

# Refresh automatico ogni 60 secondi
time.sleep(60)
st.rerun()
