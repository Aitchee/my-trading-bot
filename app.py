import streamlit as st
import requests
import time

# --- 1. CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(
    page_title="AI Financial Terminal PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CONFIGURAZIONE PONTE GOOGLE ---
# Incolla qui l'URL della distribuzione (che finisce con /exec)
GOOGLE_BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxO6mmU9uVUqTKtlmR9cIhJRB7B8jn9dPXwXnvRWVV4xPB2a_jAB0y9r_j61Nji1xTXHQ/exec"

# --- 3. FUNZIONE RECUPERO DATI ---
def recupera_dati_ponte():
    """Recupera i dati da Bitpanda passando per il ponte Google Apps Script"""
    if "GOOGLE_BRIDGE_URL" in GOOGLE_BRIDGE_URL: # Controllo se l'URL è stato inserito
        return [], "URL Mancante"
        
    try:
        # Chiamata al proxy Google per evitare il blocco 401 di Streamlit
        r = requests.get(GOOGLE_BRIDGE_URL, timeout=15)
        
        # Verifica se la risposta è effettivamente un JSON
        content_type = r.headers.get("Content-Type", "").lower()
        if "application/json" not in content_type:
            return [], "Errore: Google non ha restituito JSON (Controlla permessi 'Chiunque')"
            
        if r.status_code == 200:
            data = r.json().get('data', [])
            return data if isinstance(data, list) else [], 200
        else:
            return [], r.status_code
    except Exception as e:
        return [], f"Errore Connessione: {str(e)[:20]}"

# --- 4. INTERFACCIA GRAFICA (LAYOUT) ---
st.title("🚀 AI Financial Terminal")
st.caption(f"Status Live | Proxy: Google Apps Script | {time.strftime('%H:%M:%S')}")

# Definizione delle tre colonne
col_port, col_ai, col_chart = st.columns([1, 1.2, 1.2])

# --- COLONNA 1: PORTAFOGLIO & SALDO ---
with col_port:
    st.subheader("💰 Portafoglio")
    data, status = recupera_dati_ponte()
    
    if status == 200:
        st.success("✅ Connesso")
        found_eur = False
        for wallet in data:
            # Accesso sicuro agli attributi per evitare crash
            attr = wallet.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                bal = attr.get('balance', 0)
                st.metric("Saldo Bitpanda (EUR)", f"{float(bal):.2f} €")
                found_eur = True
        
        if not found_eur:
            st.info("Saldo EUR non trovato o pari a 0.")
            
        st.divider()
        st.subheader("💼 Asset Reali")
        # Qui potresti chiamare un secondo endpoint o filtrare i dati
        st.caption("Visualizzazione asset in tempo reale...")
        
    elif status == "URL Mancante":
        st.warning("⚠️ Configura l'URL di Google Script nel codice.")
    else:
        st.error(f"Errore: {status}")
        st.info("Assicurati di aver impostato 'Chiunque' nella distribuzione di Google Script.")

# --- COLONNA 2: SEGNALI AI (TOP 10) ---
with col_ai:
    st.subheader("🎯 Top 10 Segnali AI")
    # Lista di asset monitorati
    monitorati = [
        "Bitcoin", "NVIDIA", "Tesla", "Apple", "Ferrari", 
        "Amazon", "Microsoft", "Meta", "Eni", "Leonardo"
    ]
    
    for asset in monitorati:
        with st.expander(f"Analisi {asset}"):
            st.write(f"Sentiment per {asset}: **RIALZISTA**")
            st.progress(0.82) # Esempio di score AI
            if st.button(f"Avvia Operazione {asset}", key=f"btn_{asset}"):
                st.toast(f"Analisi approfondita inviata per {asset}!")

# --- COLONNA 3: GRAFICI ANALISI TECNICA ---
with col_chart:
    st.subheader("📊 Grafico Leonardo (Milano)")
    # Widget TradingView caricato via HTML
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
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "container_id": "tv_chart_ldo"
        });
        </script>
    </div>
    """
    st.components.v1.html(chart_html, height=460)

# --- 5. SIDEBAR & CONTROLLI ---
st.sidebar.header("⚙️ Impostazioni Bot")
st.sidebar.toggle("Pilota Automatico", value=False)
st.sidebar.divider()
st.sidebar.write("### Istruzioni Ponte:")
st.sidebar.caption("1. Vai su Google Apps Script")
st.sidebar.caption("2. Distribuisci come App Web")
st.sidebar.caption("3. Imposta accesso a 'Chiunque'")
st.sidebar.caption("4. Incolla l'URL /exec nel codice")

# --- 6. AGGIORNAMENTO AUTOMATICO ---
# Refresh della pagina ogni 60 secondi
time.sleep(60)
st.rerun()

