import streamlit as st
import requests
import time

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Trading Terminal PRO", layout="wide")

# --- 2. RECUPERO CHIAVI DAI SECRETS ---
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    ET_KEY = st.secrets["ETORO_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
except Exception:
    st.error("❌ Errore: Chiavi API mancanti nei Secrets di Streamlit!")
    st.stop()

# --- 3. FUNZIONI DI RECUPERO DATI REALI (BITPANDA) ---

def recupera_saldo_bitpanda():
    """Recupera il saldo EUR reale dal portafoglio Fiat"""
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
        return "Errore Permessi"
    except:
        return "Errore Sync"

def recupera_asset_reali():
    """Recupera le cripto o azioni possedute su Bitpanda"""
    url = "https://api.bitpanda.com/v1/asset-wallets"
    headers = {"X-API-KEY": BP_KEY}
    asset_trovati = {}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', [])
            for wallet in data:
                balance = float(wallet['attributes']['balance'])
                if balance > 0.001: # Filtra i portafogli vuoti
                    nome = wallet['attributes']['cryptocoin_symbol']
                    asset_trovati[nome] = {"val": f"{balance:.4f}", "perf": "Live"}
            return asset_trovati
        return None
    except:
        return None

# --- 4. LOGICA AI & SENTIMENT ---
def analizza_asset_full(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        art = r.get('articles', [])
        if art:
            titolo = art[0]['title']
            parole_positive = ["rialzo", "utile", "accordo", "record", "crescita", "partnership", "buy"]
            score = 0.92 if any(p in titolo.lower() for p in parole_positive) else 0.48
            motivo = "Segnale Positivo Rilevato" if score > 0.8 else "Analisi Neutra"
            return titolo, score, motivo
    except:
        pass
    return "Dati non disponibili", 0.4, "Attesa news"

# --- 5. SIDEBAR: CENTRO DI COMANDO ---
st.sidebar.title("🎮 Comando Automazione")
st.sidebar.divider()

# Visualizzazione Saldo Reale
saldo_bp = recupera_saldo_bitpanda()
with st.sidebar.expander("💰 Saldo Reale LIVE", expanded=True):
    st.write(f"Bitpanda EUR: **{saldo_bp}**")
    st.write("eToro: **Sync in attesa**")

st.sidebar.divider()

# Toggle Automazione
st.sidebar.subheader("🤖 Automazione")
auto_mode = st.sidebar.toggle("ATTIVA PILOTA AUTOMATICO", value=False)
if auto_mode:
    st.sidebar.warning("⚠️ BOT ARMATO: Operazioni automatiche attive")

budget_trade = st.sidebar.slider("Budget per operazione (€)", 10, 500, 50)

# --- 6. INTERFACCIA PRINCIPALE ---
st.title("🚀 AI Terminal: Trading Operativo")
st.caption(f"Status: {'🤖 AUTOMATICO' if auto_mode else '🔌 MANUALE'} | Live: {time.strftime('%H:%M:%S')}")

col_news, col_top10, col_portafoglio = st.columns([1, 1.4, 1])

with col_news:
    st.header("📰 News Flash")
    for t in ["Borsa Italiana", "Mercati"]:
        news, _, _ = analizza_asset_full(t)
        st.info(f"**{t}**: {news[:80]}...")

with col_top10:
    st.header("🎯 Top 10 Segnali AI")
    monitorati = ["NVIDIA", "Tesla", "Bitcoin", "Ferrari", "Apple", "Amazon", "Microsoft", "Meta", "Google", "Eni"]
    for m in monitorati:
        news, score, motivo = analizza_asset_full(m)
        stato = "🟢 BUY" if score > 0.8 else "⚪ HOLD"
        with st.expander(f"{stato} | {m}"):
            st.write(f"**Analisi:** {motivo}")
            st.caption(f"News: {news}")
            if score > 0.8:
                if auto_mode:
                    st.success(f"🤖 Pronto ad acquistare {budget_trade}€")
                else:
                    st.button(f"Compra {m}", key=f"buy_{m}")

with col_portafoglio:
    st.header("💼 I Tuoi Asset")
    asset_live = recupera_asset_reali()
    
    if asset_live:
        for nome, d in asset_live.items():
            st.metric(label=nome, value=d["val"], delta=d["perf"])
    else:
        # Se le API falliscono, mostra i dati di esempio per non lasciare vuoto
        st.warning("⚠️ Usando dati di esempio (Verifica API Key)")
        st.metric("Leonardo", "520€", "+4.5%")
        st.metric("Intesa SP", "310€", "-1.2%")

st.divider()

# --- 7. GRAFICI ---
st.header("📊 Analisi Tecnica")
g1, g2 = st.columns(2)

def genera_grafico(sym):
    return f"""
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{sym}", "interval": "D",
          "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "it"
        }});
        </script>
    </div>
    """

with g1:
    st.subheader("Leonardo (LDO)")
    st.components.v1.html(genera_grafico("MIL:LDO"), height=420)
with g2:
    st.subheader("Intesa Sanpaolo (ISP)")
    st.components.v1.html(genera_grafico("MIL:ISP"), height=420)

# --- 8. AUTO REFRESH (60 secondi) ---
time.sleep(60)
st.rerun()
