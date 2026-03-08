import streamlit as st
import requests

# Configurazione base per evitare che la pagina appaia vuota
st.set_page_config(page_title="AI Terminal", layout="wide")

# --- 1. CONFIGURAZIONE URL ---
# Incolla qui il link che hai appena copiato da Google (deve finire con /exec)
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbygLJWSdT0GSTw8qm_1uLOJswsB8J2EHjZ7SjZGpqesnKiTuCW_hx8CZKQF8Z-KkntsjQ/exec"

st.title("🚀 AI Financial Terminal")
st.write("---")

# --- 2. RECUPERO DATI ---
def recupera_dati():
    if "INCOLLA" in BRIDGE_URL:
        return None, "Manca l'URL di Google nel codice Python"
    try:
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            return r.json().get('data', []), "OK"
        else:
            return None, f"Errore Google: {r.status_code}"
    except Exception as e:
        return None, f"Errore Connessione: {str(e)}"

# --- 3. LAYOUT ---
col_port, col_chart = st.columns([1, 1.5])

with col_port:
    st.subheader("💰 Portafoglio")
    
    # Se premo il tasto, forzo il ricaricamento
    if st.button("Aggiorna Saldi"):
        st.rerun()
    
    data, status = recupera_dati()
    
    if status == "OK":
        if data and len(data) > 0:
            for item in data:
                attr = item.get('attributes', {})
                # Cerca il saldo in diversi campi possibili
                qty = float(attr.get('balance', 0) or attr.get('amount', 0) or 0)
                symbol = attr.get('symbol', '')
                
                if qty > 0:
                    st.metric(label=symbol, value=f"{qty:.4f}")
                    st.write("---")
        else:
            st.warning("⚠️ Connesso a Bitpanda, ma il portafoglio risulta vuoto.")
            st.info("Verifica di aver creato una 'Nuova Versione' su Google Script.")
    else:
        st.error(f"❌ Errore: {status}")

with col_chart:
    st.subheader("📊 Grafico Leonardo (LDO)")
    # Grafico TradingView forzato
    chart_html = """
    <div style="height:500px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "MIL:LDO",
          "interval": "D",
          "theme": "dark",
          "style": "1",
          "locale": "it",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tv_chart_1"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=520)
