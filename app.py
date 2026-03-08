import streamlit as st
import requests
import time

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Financial Terminal PRO", layout="wide")

# --- 2. CONFIGURAZIONE PONTE GOOGLE ---
# Incolla qui il tuo URL di Google Script (quello che finisce con /exec)
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

# --- 3. FUNZIONE RECUPERO DATI ---
def recupera_dati():
    if "GOOGLE" in GOOGLE_BRIDGE_URL:
        return [], "URL_MANCANTE"
    try:
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=20)
        if r.status_code == 200:
            res_json = r.json()
            return res_json.get('data', []), 200
        return [], r.status_code
    except Exception as e:
        return [], f"Errore: {str(e)[:20]}"

# --- 4. LAYOUT DASHBOARD ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Proxy: Google Apps Script | {time.strftime('%H:%M:%S')}")

col_port, col_ai, col_chart = st.columns([1, 1.2, 1.2])

# --- COLONNA 1: PORTAFOGLIO & PERFORMANCE ---
with col_port:
    st.subheader("💰 Portafoglio & Performance")
    data, status = recupera_dati()
    
    if status == 200:
        st.success("✅ Connesso")
        
        # Separazione Euro vs Asset
        for wallet in data:
            attr = wallet.get('attributes', {})
            symbol = attr.get('symbol')
            if symbol == 'EUR':
                bal = float(attr.get('balance', 0))
                st.metric("Liquidità Disponibile", f"{bal:.2f} €")
        
        st.divider()
        st.write("### I tuoi Asset")
        
        asset_found = False
        for wallet in data:
            attr = wallet.get('attributes', {})
            symbol = attr.get('symbol')
            qty = float(attr.get('balance', 0))
            
            # Mostriamo solo asset diversi da Euro con saldo > 0
            if qty > 0 and symbol != 'EUR':
                asset_found = True
                
                # Calcolo P&L (Bitpanda v1 fornisce average_price se disponibile)
                prezzo_carico = float(attr.get('average_price', 0))
                
                # NOTA: Per avere il gain reale al 100%, qui simulo un prezzo attuale.
                # In una versione avanzata, qui integreremo il prezzo live di mercato.
                cambiamento_fittizio = 1.05 # Simuliamo un +5% per testare la grafica
                prezzo_attuale_simulato = prezzo_carico * cambiamento_fittizio
                
                if prezzo_carico > 0:
                    valore_totale = qty * prezzo_attuale_simulato
                    percentuale = ((prezzo_attuale_simulato - prezzo_carico) / prezzo_carico) * 100
                    
                    # Widget con freccetta verde/rossa
                    st.metric(
                        label=f"Asset: {symbol}",
                        value=f"{valore_totale:.2f} €",
                        delta=f"{percentuale:.2f}% (G/L)",
                        delta_color="normal" if percentuale >= 0 else "inverse"
                    )
                    st.caption(f"Quantità: {qty:.4f} | Prezzo Carico: {prezzo_carico:.2f}€")
                else:
                    st.write(f"**{symbol}**")
                    st.write(f"Quantità: {qty:.4f}")
                    st.caption("Dati di carico non disponibili")
                st.divider()
        
        if not asset_found:
            st.info("Nessun asset (Azioni/Crypto) trovato nel portafoglio.")
    else:
        st.error(f"⚠️ Errore Connessione: {status}")

# --- COLONNA 2: SEGNALI AI ---
with col_ai:
    st.subheader("🎯 Segnali AI Top 10")
    monitorati = ["Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", "Leonardo"]
    for m in monitorati:
        with st.expander(f"Analisi {m}"):
            st.write(f"Sentiment {m}: **RIALZISTA**")
            st.progress(0.85)
            st.button(f"Esegui Trade {m}", key=f"trade_{m}")

# --- COLONNA 3: GRAFICI ---
with col_chart:
    st.subheader("📊 Analisi Tecnica Leonardo")
    chart_html = """
    <div style="height:450px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "MIL:LDO",
          "interval": "D",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "it",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tv_chart_ldo"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=460)

# --- REFRESH ---
time.sleep(60)
st.rerun()

