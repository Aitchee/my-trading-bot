import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="eToro AI Management", layout="wide")

# --- DATABASE ASSET REALI (Modifica questi dati con i tuoi veri di eToro) ---
if 'my_assets' not in st.session_state:
    st.session_state.my_assets = [
        {"ticker": "LDO.MI", "nome": "Leonardo", "qty": 15, "investito": 300.50, "valore_attuale": 345.20},
        {"ticker": "ISP.MI", "nome": "Intesa SP", "qty": 400, "investito": 1200.00, "valore_attuale": 1180.40},
        {"ticker": "AMZN", "nome": "Amazon", "qty": 2, "investito": 350.00, "valore_attuale": 382.10},
        {"ticker": "NVDA", "nome": "NVIDIA", "qty": 1, "investito": 750.00, "valore_attuale": 890.00},
    ]

# --- LAYOUT SUPERIORE: TRIPLA COLONNA ---
col_monitor, col_news, col_portfolio = st.columns([1, 1.2, 1.3])

# 1. SINISTRA: Monitoraggio e Analisi (Cosa fare ora)
with col_monitor:
    st.subheader("🎯 Stock Monitor")
    for asset in st.session_state.my_assets:
        pnl = asset['valore_attuale'] - asset['investito']
        colore = "green" if pnl >= 0 else "red"
        st.markdown(f"**{asset['nome']}**")
        st.caption(f"Trend: {'🚀 Bullish' if pnl > 0 else '📉 Bearish'}")
        st.button(f"Analisi AI {asset['ticker']}", key=f"btn_{asset['ticker']}")
        st.divider()

# 2. CENTRO: News & Watchlist (In base ai mercati)
with col_news:
    st.subheader("📰 Market Watch (News)")
    st.info("**NVIDIA**: Attesi utili trimestrali. Volatilità alta.")
    st.warning("**Leonardo**: Nuovi contratti Difesa UE. Monitorare breakout.")
    st.error("**Intesa SP**: Taglio tassi BCE potrebbe influire sui margini.")
    
    st.write("---")
    st.write("**Hot Picks del giorno:**")
    st.success("1. TESLA (Oversold)")
    st.success("2. APPLE (New Product Launch)")

# 3. DESTRA: Asset Effettivi e P&L Reale
with col_portfolio:
    st.subheader("💰 Mio Portafoglio eToro")
    tot_investito = sum(a['investito'] for a in st.session_state.my_assets)
    tot_attuale = sum(a['valore_attuale'] for a in st.session_state.my_assets)
    tot_pnl = tot_attuale - tot_investito
    
    st.metric("Valore Totale", f"{tot_attuale:,.2f} €", f"{tot_pnl:,.2f} €")
    st.write("---")
    
    for a in st.session_state.my_assets:
        pnl_singolo = a['valore_attuale'] - a['investito']
        perc = (pnl_singolo / a['investito']) * 100
        
        c1, c2 = st.columns([2,1])
        c1.write(f"**{a['nome']}** ({a['qty']} pezzi)")
        c1.caption(f"Investiti: {a['investito']} €")
        c2.metric("P&L", f"{a['valore_attuale']}€", f"{perc:.2f}%")
        st.divider()

# --- LAYOUT INFERIORE: GRAFICI A CASCATA ---
st.write("---")
st.header("📊 Performance & Charts")

# A. Grafico a Linea del Portafoglio nel tempo (Simulato)
st.subheader("📈 Andamento Equity Line")
# Creiamo dati storici fake per il grafico a linea
date_rng = pd.date_range(start='2024-01-01', periods=10, freq='M')
df_history = pd.DataFrame({'Data': date_rng, 'Valore (€)': [2000, 2100, 2050, 2300, 2450, 2400, 2600, 2750, 2800, tot_attuale]})
fig_line = px.line(df_history, x='Data', y='Valore (€)', template="plotly_dark", line_shape="spline")
st.plotly_chart(fig_line, use_container_width=True)

# B. Grafici Asset Specifici (TradingView)
st.subheader("📉 Analisi Grafica Asset in Portafoglio")
asset_selezionato = st.selectbox("Cambia asset visualizzato sotto:", [a['ticker'] for a in st.session_state.my_assets])

chart_html = f"""
    <div style="height:500px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{asset_selezionato}", "interval": "D",
          "theme": "dark", "style": "1", "locale": "it", "enable_publishing": false, 
          "allow_symbol_change": true, "container_id": "tv_chart_main"
        }});
        </script>
    </div>
"""
st.components.v1.html(chart_html, height=520)
