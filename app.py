import streamlit as st
import requests

st.set_page_config(page_title="AI Terminal PRO", layout="wide")

# URL del tuo ponte Google (deve finire con /exec)
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

st.title("🚀 AI Financial Terminal")
st.write("---")

def recupera_dati():
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        return r.json().get('data', []), "OK"
    except:
        return [], "Errore"

# Layout: Portafoglio a sinistra, Grafico ENORME a destra
col_port, col_chart = st.columns([1, 2.5]) # Aumentato lo spazio per il grafico

with col_port:
    st.subheader("💰 Portafoglio")
    if st.button("🔄 Aggiorna Saldi"):
        st.rerun()
    
    data, status = recupera_dati()
    if status == "OK" and data:
        for item in data:
            attr = item.get('attributes', {})
            qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
            symbol = attr.get('symbol', '')
            
            if qty > 0:
                # Nomi reali per i tuoi titoli legacy
                nomi = {"LDO": "Leonardo", "ISP": "Intesa SP", "AMZN": "Amazon", "NVDA": "NVIDIA", "AAPL": "Apple", "EUR": "Contanti"}
                nome = nomi.get(symbol, symbol)
                pmc = float(attr.get('average_price', 0))
                
                with st.container():
                    st.write(f"**{nome}** ({symbol})")
                    st.metric("Q.tà", f"{qty:.4f}", delta=f"Pmc: {pmc:.2f}€" if pmc > 0 else None)
                    st.write("---")
    else:
        st.info("In attesa di dati... Assicurati di aver fatto 'Nuova Versione' su Google.")

with col_chart:
    st.subheader("📊 Analisi Tecnica Leonardo (LDO)")
    chart_html = """
    <div style="height:600px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "MIL:LDO", "interval": "D",
          "theme": "dark", "style": "1", "locale": "it", "container_id": "tv_chart_main"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=620)
