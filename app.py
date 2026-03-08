import streamlit as st
import requests

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Trading Bot PRO", layout="wide")
st.title("🚀 AI Trading Command Center")

# 2. Recupero Chiavi dai Secrets
try:
    BP_KEY = st.secrets["BITPANDA_API_KEY"]
    NW_KEY = st.secrets["NEWS_API_KEY"]
    st.sidebar.success("✅ Connessione API Stabilita")
except Exception:
    st.error("❌ Errore: Controlla i Secrets su Streamlit!")
    st.stop()

# 3. Funzione Logica AI
def analizza_asset(nome):
    url = f"https://newsapi.org/v2/everything?q={nome}&apiKey={NW_KEY}&language=it"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
        news = articles[0]['title'] if articles else "Nessuna news rilevante"
        # Logica simulata sentiment
        score = 0.85 if any(x in news.lower() for x in ["rialzo", "record", "utile", "crescita"]) else 0.45
        return news, score
    except:
        return "Errore connessione news", 0.0

# 4. Layout Superiore (3 Colonne)
col_news, col_opportunita, col_portafoglio = st.columns([1, 1.2, 1])

with col_news:
    st.header("📰 Global News")
    for topic in ["Borsa Italiana", "Inflazione", "Mercati"]:
        titolo, _ = analizza_asset(topic)
        st.write(f"🔹 {titolo}")

with col_opportunita:
    st.header("🎯 Consigli AI (Buy)")
    potenziali = ["Bitcoin", "Apple", "Ferrari", "Oro"]
    for p in potenziali:
        news, score = analizza_asset(p)
        if score > 0.8:
            st.success(f"✅ **{p}**: Segnale Forte")
            st.caption(f"News: {news[:60]}...")
            if st.button(f"Investi in {p}", key=f"btn_{p}"):
                st.toast(f"Ordine simulato per {p}!")
        else:
            st.info(f"⚪ **{p}**: Monitoraggio")

with col_portafoglio:
    st.header("💼 I Tuoi Asset")
    miei_asset = {"Leonardo SPA": "+4.5%", "Intesa SP": "-1.2%"}
    for nome, rendimento in miei_asset.items():
        st.metric(label=nome, value=rendimento, delta=rendimento)
        st.caption(f"News: {analizza_asset(nome)[0][:50]}...")

st.divider()

# 5. Layout Inferiore (Grafici) - Correzione SyntaxError
st.header("📊 Analisi Tecnica (TradingView)")
col_g1, col_g2 = st.columns(2)

def genera_grafico(symbol):
    html_code = f"""
    <div style="height:350px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "{symbol}",
          "interval": "H",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "it",
          "toolbar_bg": "#f1f3f6"
        }});
        </script>
    </div>
    """
    return html_code

with col_g1:
    st.components.v1.html(genera_grafico("BITPANDA:LDO"), height=380)
with col_g2:
    st.components.v1.html(genera_grafico("BITPANDA:ISP"), height=380)

# 6. Sidebar Automazione
st.sidebar.header("🤖 Robot Settings")
auto_trade = st.sidebar.toggle("Pilota Automatico Totale")
if auto_trade:
    st.sidebar.warning("MODALITÀ ATTIVA: Il bot opererà basandosi sul sentiment.")
