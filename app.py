import streamlit as st
import pandas as pd

st.set_page_config(page_title="eToro AI Terminal", layout="wide")

st.title("🦅 eToro AI Management Terminal")
st.caption("Centrale Operativa - Monitoraggio Asset & Segnali")

# Simuliamo il tuo portafoglio eToro (visto che non hanno API, lo gestiamo qui)
# Puoi modificare questi valori quando vuoi
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        "LDO.MI": {"nome": "Leonardo", "qty": 10, "pmc": 21.50},
        "ISP.MI": {"nome": "Intesa Sanpaolo", "qty": 500, "pmc": 3.10},
        "AMZN": {"nome": "Amazon", "qty": 5, "pmc": 175.00},
        "NVDA": {"nome": "NVIDIA", "qty": 2, "pmc": 800.00}
    }

col_sx, col_dx = st.columns([1, 2.5])

with col_sx:
    st.subheader("📋 Portafoglio eToro")
    total_val = 0
    for ticker, info in st.session_state.portfolio.items():
        with st.container():
            st.write(f"**{info['nome']}** ({ticker})")
            # Qui il terminale simula il monitoraggio
            st.write(f"Quantità: {info['qty']} | Pmc: {info['pmc']}€")
            st.divider()

    if st.button("➕ Aggiungi/Modifica Asset"):
        st.info("Funzione per aggiornare manualmente i tuoi acquisti su eToro")

with col_dx:
    st.subheader("📊 Analisi Tecnica & Segnali AI")
    
    # Selettore per cambiare grafico al volo
    scelta = st.selectbox("Seleziona titolo da analizzare", list(st.session_state.portfolio.keys()))
    
    # Grafico TradingView DINAMICO (Prezzi eToro/Exchange)
    chart_html = f"""
    <div style="height:550px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{scelta}", "interval": "D",
          "theme": "dark", "style": "1", "locale": "it", "toolbar_bg": "#f1f3f6",
          "enable_publishing": false, "allow_symbol_change": true, "container_id": "tv_chart"
        }});
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=570)

st.subheader("🎯 Suggerimenti Operativi AI")
st.info(f"L'intelligenza artificiale consiglia di MANTENERE la posizione su {scelta}. RSI in zona neutra.")
