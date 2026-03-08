import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trading Terminal", layout="wide")

# --- RECUPERO CHIAVI ---
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
except Exception:
    st.error("❌ Errore API: Controlla i Secrets!")
    st.stop()

# --- LOGICA AI AVANZATA ---
def analizza_asset_full(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it&sortBy=publishedAt"
    try:
        r = requests.get(url).json()
        art = r.get('articles', [])
        if art:
            titolo = art[0]['title']
            # Analisi semplice del perché
            parole_chiave = {"rialzo": "Trend positivo", "utile": "Bilancio solido", "accordo": "Nuova partnership", "record": "Performance storica", "bitcoin": "Adozione crypto"}
            motivo = next((v for k, v in parole_chiave.items() if k in titolo.lower()), "Stabilità di mercato")
            score = 0.85 if motivo != "Stabilità di mercato" else 0.50
            return titolo, score, motivo
    except:
        pass
    return "Nessuna news fresca", 0.4, "Attesa dati"

# --- TITOLO E TIMER ---
st.title("🚀 AI Terminal: Portafoglio & Strategia")
st.caption(f"Ultimo aggiornamento live: {time.strftime('%H:%M:%S')} (Auto-refresh ogni 60s)")

# --- COLONNE SUPERIORI ---
col_news, col_top10, col_portafoglio = st.columns([1, 1.4, 1])

with col_news:
    st.header("📰 Notizie Flash")
    for t in ["Borsa Italiana", "Fed", "Economia"]:
        news, _, _ = analizza_asset_full(t)
        st.info(f"**{t}**: {news[:70]}...")

with col_top10:
    st.header("🎯 Top 10 Segnali AI")
    monitorati = ["NVIDIA", "Tesla", "Bitcoin", "Apple", "Ferrari", "Oro", "Amazon", "Microsoft", "Eni", "Meta"]
    for m in monitorati:
        news, score, motivo = analizza_asset_full(m)
        with st.expander(f"{'🟢' if score > 0.8 else '⚪'} {m} - {motivo}"):
            st.write(f"**Analisi:** {motivo}. Il sentiment rilevato è del {int(score*100)}%")
            st.caption(f"Ultima News: {news}")
            if score > 0.8: st.button(f"Acquisto Automatico {m}", key=f"top_{m}")

with col_portafoglio:
    st.header("💼 I Tuoi Asset")
    # Aggiungi qui tutte le tue azioni
    miei_asset = {
        "Leonardo": {"perf": "+4.5%", "val": "520€", "sym": "MIL:LDO"},
        "Intesa SP": {"perf": "-1.2%", "val": "310€", "sym": "MIL:ISP"},
        "Enel": {"perf": "+0.8%", "val": "150€", "sym": "MIL:ENEL"},
        "UniCredit": {"perf": "+2.1%", "val": "400€", "sym": "MIL:UCG"}
    }
    for nome, dati in miei_asset.items():
        st.metric(label=nome, value=dati["val"], delta=dati["perf"])

st.divider()

# --- GRAFICI CORRETTI ---
st.header("📊 Grafici Analisi Tecnica (Borsa Italiana)")
col_g1, col_g2 = st.columns(2)

def genera_grafico_fix(symbol):
    return f"""
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{symbol}", "interval": "D",
          "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "it",
          "enable_publishing": false, "hide_top_toolbar": false, "save_image": false
        }});
        </script>
    </div>
    """

with col_g1:
    st.subheader("Leonardo (LDO)")
    st.components.v1.html(genera_grafico_fix("MIL:LDO"), height=420)
with col_g2:
    st.subheader("Intesa Sanpaolo (ISP)")
    st.components.v1.html(genera_grafico_fix("MIL:ISP"), height=420)

# --- AUTO REFRESH SCRIPT ---
time.sleep(60)
st.rerun()
