import streamlit as st
import requests
import time

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Trading Terminal PRO", layout="wide")

# --- 2. RECUPERO CHIAVI DAI SECRETS ---
# IMPORTANTE: Qui usiamo i NOMI delle etichette, non i codici lunghi!
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    ET_KEY = st.secrets["ETORO_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
except Exception as e:
    st.error(f"❌ Errore Secrets: Assicurati che nel box di Streamlit i nomi siano BITPANDA_API_KEY, ETORO_API_KEY e NEWS_API_KEY.")
    st.stop()

# --- 3. FUNZIONI DI RECUPERO DATI REALI (BITPANDA) ---

def recupera_saldo_fiat():
    """Recupera il saldo EUR reale dai Fiat Wallets"""
    url = "https://api.bitpanda.com/v1/fiat-wallets"
    headers = {"X-API-KEY": BP_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', [])
            for wallet in data:
                if wallet['attributes']['symbol'] == 'EUR':
                    balance = float(wallet['attributes']['balance'])
                    return f"{balance:.2f} €"
            return "0.00 €"
        elif response.status_code == 401:
            return "Chiave Errata"
        elif response.status_code == 403:
            return "Permessi Insufficienti"
        return f"Errore {response.status_code}"
    except:
        return "Errore Sync"

def recupera_asset_portafoglio():
    """Recupera le posizioni reali (BTC, ETH, LDO ecc.)"""
    url = "https://api.bitpanda.com/v1/asset-wallets"
    headers = {"X-API-KEY": BP_KEY}
    asset_trovati = {}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', [])
            for wallet in data:
                balance = float(wallet['attributes']['balance'])
                if balance > 0.0001:
                    simbolo = wallet['attributes']['cryptocoin_symbol']
                    asset_trovati[simbolo] = {"val": f"{balance:.4f}", "perf": "Live"}
            return asset_trovati
        return None
    except:
        return None

# --- 4. LOGICA AI & NEWS ---
def analizza_sentiment(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        art = r.get('articles', [])
        if art:
            titolo = art[0]['title']
            score = 0.90 if any(p in titolo.lower() for p in ["rialzo", "utile", "accordo", "boom", "crescita"]) else 0.45
            motivo = "Segnale Positivo" if score > 0.8 else "Neutro"
            return titolo, score, motivo
    except:
        pass
    return "Nessuna notizia recente", 0.4, "Attesa"

# --- 5. SIDEBAR: COMANDO ---
st.sidebar.title("🎮 Comando Automazione")
st.sidebar.divider()

# Visualizzazione Saldo Reale
saldo_fiat = recupera_saldo_fiat()
with st.sidebar.expander("💰 Saldo Reale LIVE", expanded=True):
    st.write(f"Bitpanda EUR: **{saldo_fiat}**")
    st.write("eToro: **Sync in attesa**")

st.sidebar.divider()

auto_mode = st.sidebar.toggle("ATTIVA PILOTA AUTOMATICO", value=False)
budget_trade = st.sidebar.slider("Budget operazione (€)", 10, 500, 50)

# --- 6. INTERFACCIA PRINCIPALE ---
st.title("🚀 AI Terminal: Trading Operativo")
st.caption(f"Status: {'🤖 AUTOMATICO' if auto_mode else '🔌 MANUALE'} | {time.strftime('%H:%M:%S')}")

col_news, col_top10, col_portafoglio = st.columns([1, 1.4, 1])

with col_news:
    st.header("📰 News Flash")
    for t in ["Borsa Italiana", "Mercati Euro"]:
        news, _, _ = analizza_sentiment(t)
        st.info(f"**{t}**: {news[:80]}...")

with col_top10:
    st.header("🎯 Top 10 Segnali AI")
    monitorati = ["NVIDIA", "Tesla", "Bitcoin", "Ferrari", "Apple", "Amazon", "Microsoft", "Meta", "Google", "Enel"]
    for m in monitorati:
        news, score, motivo = analizza_sentiment(m)
        stato = "🟢 BUY" if score > 0.8 else "⚪ HOLD"
        with st.expander(f"{stato} | {m}"):
            st.write(f"**Analisi:** {motivo}")
            st.caption(f"News: {news}")
            if score > 0.8 and not auto_mode:
                st.button(f"Compra {m}", key=f"btn_{m}")

with col_portafoglio:
    st.header("💼 I Tuoi Asset")
    asset_live = recupera_asset_portafoglio()
    if asset_live:
        for nome, d in asset_live.items():
            st.metric(label=nome, value=d["val"], delta=d["perf"])
    else:
        st.warning("⚠️ Nessun asset trovato o errore API")
        # Fallback dati statici per Leonardo/Intesa se non hai ancora comprato nulla
        st.metric("Leonardo (Esempio)", "520€", "+4.5%")
        st.metric("Intesa SP (Esempio)", "310€", "-1.2%")

st.divider()

# --- 7. GRAFICI ---
st.header("📊 Analisi Tecnica")
g1, g2 = st.columns(2)

def genera_grafico(sym):
    return f"""<div style="height:400px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "D", "theme": "dark", "style": "1", "locale": "it"}});</script></div>"""

with g1:
    st.subheader("Leonardo (LDO)")
    st.components.v1.html(genera_grafico("MIL:LDO"), height=420)
with g2:
    st.subheader("Intesa Sanpaolo (ISP)")
    st.components.v1.html(genera_grafico("MIL:ISP"), height=420)

# --- 8. REFRESH ---
time.sleep(60)
st.rerun()
