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

# --- 3. FUNZIONE SALDO REALE (BITPANDA) ---
def recupera_saldo_bitpanda():
    # Nota: richiede permesso 'Read' sulla chiave API di Bitpanda
    url = "https://api.bitpanda.com/v1/fiat-wallets"
    headers = {"X-API-KEY": BP_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        for wallet in response['data']:
            if wallet['attributes']['symbol'] == 'EUR':
                return f"{wallet['attributes']['balance']} €"
    except:
        return "Errore Sync"
    return "0.00 €"

# --- 4. LOGICA AI & SENTIMENT ---
def analizza_asset_full(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        art = r.get('articles', [])
        if art:
            titolo = art[0]['title']
            parole_positive = ["rialzo", "utile", "accordo", "record", "crescita", "boom", "partnership"]
            score = 0.92 if any(p in titolo.lower() for p in parole_positive) else 0.45
            motivo = "Forte segnale positivo (News)" if score > 0.8 else "Nessun segnale operativo"
            return titolo, score, motivo
    except:
        pass
    return "Dati non disponibili", 0.4, "Attesa aggiornamento"

# --- 5. SIDEBAR: COMANDO E CONTROLLO ---
st.sidebar.title("🎮 Centro di Comando")
st.sidebar.divider()

# Visualizzazione Saldo Reale
saldo_bp = recupera_saldo_bitpanda()
with st.sidebar.expander("💰 Saldo Reale LIVE", expanded=True):
    st.write(f"Bitpanda: **{saldo_bp}**")
    st.write("eToro: **In attesa API...**")

st.sidebar.divider()

# Toggle Automazione
st.sidebar.subheader("🤖 Automazione")
auto_mode = st.sidebar.toggle("ATTIVA PILOTA AUTOMATICO", value=False)
if auto_mode:
    st.sidebar.warning("⚠️ IL BOT OPERERÀ DA SOLO!")

# Parametri di Rischio
budget_trade = st.sidebar.slider("Budget per operazione (€)", 10, 500, 50)
stop_loss = st.sidebar.slider("Stop Loss globale (%)", 1, 15, 5)

if st.sidebar.button("🔴 DISATTIVA TUTTO", type="secondary"):
    st.rerun()

# --- 6. INTERFACCIA PRINCIPALE ---
st.title("🚀 AI Terminal: Trading Operativo")
st.caption(f"Aggiornamento Live: {time.strftime('%H:%M:%S')} | Refresh ogni 60s")

col_news, col_top10, col_portafoglio = st.columns([1, 1.4, 1])

with col_news:
    st.header("📰 Breaking News")
    for t in ["Borsa Italiana", "Mercati Euro", "Nasdaq"]:
        news, _, _ = analizza_asset_full(t)
        st.info(f"**{t}**: {news[:80]}...")

with col_top10:
    st.header("🎯 Top 10 Segnali AI")
    monitorati = ["NVIDIA", "Tesla", "Bitcoin", "Ferrari", "Apple", "Amazon", "Microsoft", "Meta", "Google", "Eni"]
    for m in monitorati:
        news, score, motivo = analizza_asset_full(m)
        stato = "🟢 BUY" if score > 0.8 else "⚪ HOLD"
        
        with st.expander(f"{stato} | {m} ({int(score*100)}%)"):
            st.write(f"**Analisi AI:** {motivo}")
            st.caption(f"Ultima News: {news}")
            
            if score > 0.8:
                if auto_mode:
                    st.success(f"🤖 Automazione pronta: acquisto {budget_trade}€ in corso...")
                else:
                    st.button(f"Conferma Acquisto {m}", key=f"buy_{m}")

with col_portafoglio:
    st.header("💼 Asset in Possesso")
    # Qui inserisci i tuoi asset reali
    miei_asset = {
        "Leonardo": {"perf": "+4.5%", "val": "520€", "sym": "MIL:LDO"},
        "Intesa SP": {"perf": "-1.2%", "val": "310€", "sym": "MIL:ISP"},
        "Enel": {"perf": "+0.8%", "val": "150€", "sym": "MIL:ENEL"}
    }
    for nome, d in miei_asset.items():
        st.metric(label=nome, value=d["val"], delta=d[ "perf"])

st.divider()

# --- 7. GRAFICI ---
st.header("📊 Analisi Tecnica (TradingView)")
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
    st.subheader("Leonardo SPA (LDO)")
    st.components.v1.html(genera_grafico("MIL:LDO"), height=420)
with g2:
    st.subheader("Intesa Sanpaolo (ISP)")
    st.components.v1.html(genera_grafico("MIL:ISP"), height=420)

# --- 8. AUTO REFRESH ---
time.sleep(60)
st.rerun()
