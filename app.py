import streamlit as st
import requests
import time

# 1. Configurazione Pagina e Auto-Refresh (60 secondi)
st.set_page_config(page_title="AI Trading Bot PRO", layout="wide")

# Questo comando forza l'aggiornamento della pagina ogni 60 secondi
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# Script per il refresh automatico
st.empty() 

# 2. Recupero Chiavi
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
except Exception:
    st.error("❌ Controlla i Secrets su Streamlit!")
    st.stop()

st.title("🚀 AI Trading Command Center (Live)")
st.caption(f"Ultimo aggiornamento automatico: {time.strftime('%H:%M:%S')}")

# 3. Funzione Logica AI Avanzata
def analizza_asset_pro(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        if articles:
            titolo = articles[0]['title']
            desc = articles[0].get('description', '')
            # Logica di analisi motivo
            score = 0.85 if any(x in titolo.lower() or x in desc.lower() for x in ["rialzo", "record", "accordo", "positivo", "buy", "target"]) else 0.45
            motivo = "Sentiment positivo dai media" if score > 0.8 else "Mercato stabile / Attesa news"
            return titolo, score, motivo
    except:
        pass
    return "Nessuna news", 0.0, "Dati non disponibili"

# 4. LAYOUT SUPERIORE (3 COLONNE)
col_news, col_opportunita, col_portafoglio = st.columns([1, 1.3, 1])

with col_news:
    st.header("📰 Breaking News")
    temi_caldi = ["Borsa Italiana", "Bitcoin News", "Wall Street", "Economia UE"]
    for t in temi_caldi:
        titolo, _, _ = analizza_asset_pro(t)
        st.info(f"**{t}**: {titolo[:80]}...")

with col_opportunita:
    st.header("🎯 Top 10 Segnali AI")
    # Top 10 monitorate
    monitorati = ["Bitcoin", "Ethereum", "Apple", "NVIDIA", "Tesla", "Ferrari", "Oro", "Amazon", "Microsoft", "Eni"]
    for m in monitorati:
        news, score, motivo = analizza_asset_pro(m)
        with st.expander(f"{'🟢' if score > 0.8 else '⚪'} {m}"):
            st.write(f"**Motivazione AI:** {motivo}")
            st.caption(f"**News:** {news}")
            if score > 0.8:
                st.button(f"Auto-Buy {m}", key=f"buy_{m}")

with col_portafoglio:
    st.header("💼 Il Tuo Portafoglio")
    # Qui aggiungi tutte le azioni che possiedi
    miei_asset = {
        "Leonardo SPA": {"perf": "+4.5%", "val": "520€"},
        "Intesa SP": {"perf": "-1.2%", "val": "310€"},
        "Enel": {"perf": "+0.8%", "val": "150€"},
        "UniCredit": {"perf": "+2.1%", "val": "400€"}
    }
    for nome, dati in miei_asset.items():
        st.metric(label=nome, value=dati["val"], delta=dati["perf"])

st.divider()

# 5. LAYOUT INFERIORE (GRAFICI)
st.header("📊 Grafici Analisi Tecnica")
col_g1, col_g2 = st.columns(2)

def genera_grafico(symbol):
    return f"""
    <div style="height:350px;"><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">new TradingView.widget({{"autosize": true,"symbol": "{symbol}","interval": "H","timezone": "Etc/UTC","theme": "dark","style": "1","locale": "it"}});</script></div>
    """

with col_g1:
    st.components.v1.html(genera_grafico("BITPANDA:LDO"), height=380)
with col_g2:
    st.components.v1.html(genera_grafico("BITPANDA:ISP"), height=380)

# 6. Sidebar e Refresh Automatico (Trick per il refresh)
st.sidebar.header("🤖 Impostazioni")
if st.sidebar.button("🔄 Forza Aggiornamento Manuale"):
    st.rerun()

st.sidebar.write("Il bot si aggiorna da solo ogni minuto.")

# Piccolo trucco per il refresh automatico senza plugin esterni complessi
time.sleep(60)
st.rerun()
