import streamlit as st
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & REFRESH
st.set_page_config(page_title="EDOARDO AI TRADER", layout="wide")
st_autorefresh(interval=10000, key="terminal_final_fix")

# 2. RECUPERO CHIAVI (PULIZIA TOTALE)
RAW_KEY = st.secrets.get("BITPANDA_API_KEY", "5d54c4f3e64db9af79be657b80036696f435feecc9f45c9422fd98964336c821158daf5123376f5175f6a7b8b27dc070126d647ef6c2518946eacaa06ca84ad1")
# Rimuove tutto ciò che non è alfanumerico (spazi, invii, virgolette)
BITPANDA_KEY = "".join(c for c in RAW_KEY if c.isalnum())
NEWS_KEY = st.secrets.get("NEWS_API_KEY", "f47b85db22664beba249feed052403c3")

analyzer = SentimentIntensityAnalyzer()

def fetch_wallets_bruteforce():
    if not BITPANDA_KEY: return "CHIAVE_MANCANTE"
    
    # Proviamo i due endpoint principali di Bitpanda
    endpoints = [
        "https://api.bitpanda.com/v1/asset-wallets",
        "https://api.bitpanda.com/v1/fiat-wallets"
    ]
    
    # Proviamo diverse varianti di Header (alcuni account vogliono Bearer, altri X-API-KEY)
    auth_variants = [
        {"X-API-KEY": BITPANDA_KEY, "Accept": "application/json"},
        {"Authorization": f"Bearer {BITPANDA_KEY}", "Accept": "application/json"}
    ]
    
    all_data = []
    
    for url in endpoints:
        for headers in auth_variants:
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json().get('data', [])
                    all_data.extend(data)
                    break # Se funziona con questo header, passa al prossimo URL
                elif r.status_code == 401:
                    last_error = "401_UNAUTHORIZED"
            except:
                continue
                
    if all_data:
        return all_data
    return "401_STILL_LOCKED"

# --- DASHBOARD ---
st.title(f"🚀 TERMINALE EDOARDO LIVE - {datetime.now().strftime('%H:%M:%S')}")

c1, c2 = st.columns([1, 2])

with c1:
    st.header("💰 Portafoglio")
    res = fetch_wallets_bruteforce()
    
    if res == "401_STILL_LOCKED":
        st.error("❌ Bitpanda rifiuta ancora la chiave (401).")
        st.write("Dettaglio Tecnico: Il server ha ricevuto la chiave ma la considera non valida per questa API.")
        st.info("💡 Prova a creare una chiave API con TUTTI i permessi (anche se pensi di non usarli) e riprova.")
    elif isinstance(res, list):
        st.success("✅ BITPANDA CONNESSO!")
        for item in res:
            attr = item.get('attributes', {})
            val = float(attr.get('balance', 0))
            if val > 0:
                st.metric(f"{attr.get('name')}", f"{val:.4f} {attr.get('symbol')}")
    else:
        st.warning(f"Stato: {res}")

with c2:
    st.header("🎯 AI Trading & News")
    # Logica di trading...
    st.write("In attesa di sblocco API per attivare l'automazione.")
