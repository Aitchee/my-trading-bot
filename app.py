import streamlit as st

st.set_page_config(page_title="DEBUG CHIAVE EDOARDO", layout="wide")

st.title("🔍 Scanner Segreti Streamlit")

# 1. Recupero grezzo (quello che Streamlit vede)
raw_key = st.secrets.get("BITPANDA_API_KEY", "NON TROVATA")

# 2. Pulizia (quello che il codice usa)
clean_key = raw_key.strip().replace('"', '').replace("'", "")

st.subheader("1. Chiave Rilevata nei Secrets:")
if raw_key == "NON TROVATA":
    st.error("❌ Errore: Non ho trovato nessuna voce 'BITPANDA_API_KEY' nei Secrets.")
else:
    # Stampiamo la chiave in un box di codice per vederla bene
    st.code(raw_key, language="text")
    st.info(f"Lunghezza totale: {len(raw_key)} caratteri")

st.divider()

st.subheader("2. Chiave Pulita (Pronta per il codice):")
st.code(clean_key, language="text")

st.divider()

st.subheader("📝 Check-list per te:")
st.markdown(f"""
1. **Confronto:** La stringa qui sopra è IDENTICA a quella che hai su Bitpanda?
2. **Spazi:** Se selezioni il testo nel box sopra, vedi spazi vuoti all'inizio o alla fine? (La lunghezza corretta per Bitpanda è solitamente **128** caratteri).
3. **Virgolette:** Vedi delle virgolette `"` o `'` dentro il box? Se sì, cancellale dai Secrets, non devono esserci.
""")

if st.button("RIFA SCAN (Dopo che hai salvato i Secrets)"):
    st.rerun()
