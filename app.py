import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trading Bot PRO", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    ET_KEY = st.secrets["ETORO_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
except Exception:
    st.error("❌ Errore API: Controlla i Secrets!")
    st.stop()

# --- SIDEBAR: CENTRO DI COMANDO ---
st.sidebar.title("🎮 Comando Automazione")
st.sidebar.divider()

# 1. Saldo Contanti (Simulato o via API se disponibile)
saldo = st.sidebar.status("💰 Saldo Disponibile")
saldo.write("Bitpanda: **450,00 €**")
saldo.write("eToro: **1.200,00 $**")

st.sidebar.divider()

# 2. Attivazione Automazione
st.sidebar.subheader("⚙️ Impostazioni")
auto_bitpanda = st.sidebar.toggle("Attiva Automazione Bitpanda", value=False)
auto_etoro = st.sidebar.toggle("Attiva Automazione eToro", value=False)

if st.sidebar.button("🚀 ATTIVA TUTTO", type="primary"):
    auto_bitpanda = True
    auto_etoro = True
    st.sidebar.success("Sistemi Armati!")

st.sidebar.divider()

# 3. Parametri di Rischio (Suggerimento Extra)
st.sidebar.subheader("🛡️ Gestione Rischio")
budget_per_trade = st.sidebar.slider("Budget per operazione (€)", 10, 200, 50)
stop_loss = st.sidebar.slider("Stop Loss (%)", 1, 10, 5)

# --- LOGICA AI ---
def analizza_asset_full(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        art = r.get('articles', [])
        if art:
            titolo = art[0]['title']
            parole_positive = ["rialzo", "utile", "accordo", "record", "crescita", "boom"]
            score = 0.9 if any(p in titolo.lower() for p in parole_positive) else 0.5
            motivo = "Segnale Positivo Rilevato" if score > 0.8 else "Nessun segnale chiaro"
            return titolo, score, motivo
    except:
        pass
    return "Dati non disponibili", 0.4, "Attesa news"

# --- INTERFACCIA PRINCIPALE ---
st.title("🚀 AI Terminal: Trading Automatico")
st.caption(f"Status: {'🤖 AUTOMAZIONE ATTIVA' if (auto_bitpanda or auto_etoro) else '🔌 MODALITÀ MANUALE'} | Live: {time.strftime('%H:%M:%S')}")

col_news, col_top10, col_portafoglio = st.columns([1, 1.4, 1])

with col_news:
    st.header("📰 Breaking News")
    for t in ["Mercati", "Borsa Italiana"]:
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
            
            # --- LOGICA DI ESECUZIONE AUTOMATICA ---
            if score > 0.8:
                if (auto_bitpanda or auto_etoro):
                    st.warning(f"🤖 Bot pronto ad acquistare {budget_per_trade}€ di {m}")
                    # Qui andrà la funzione finale: invia_ordine_reale(m, budget_per_trade)
                else:
                    st.button(f"Compra {m} Manualmente", key=f"btn_{m}")

with col_portafoglio:
    st.header("💼 Asset Attivi")
    miei_asset = {"Leonardo": "+4.5%", "Intesa SP": "-1.2%", "Enel": "+0.8%"}
    for nome, perf in miei_asset.items():
        st.metric(label=nome, value=perf, delta=perf)

st.divider()

# --- GRAFICI ---
st.header("📊 Grafici Analisi Tecnica")
g1, g2 = st.columns(2)
def genera_grafico(sym):
    return f"""<div style="height:400px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "{sym}", "interval": "D", "theme": "dark", "style": "1", "locale": "it"}});</script></div>"""

with g1: st.components.v1.html(genera_grafico("MIL:LDO"), height=420)
with g2: st.components.v1.html(genera_grafico("MIL:ISP"), height=420)

# --- REFRESH ---
time.sleep(60)
st.rerun()
