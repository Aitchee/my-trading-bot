with col_port:
    st.subheader("💰 Portafoglio")
    data, status = recupera_dati_globali()
    
    if status == 200:
        # 1. Visualizzazione Saldo Cash
        for wallet in data:
            attr = wallet.get('attributes', {})
            if attr.get('symbol') == 'EUR':
                bal = float(attr.get('balance', 0))
                st.metric("Liquidità (EUR)", f"{bal:.2f} €")
        
        st.divider()
        st.subheader("💼 Performance Asset")
        
        # 2. Tabella Asset con Gain/Loss
        for wallet in data:
            attr = wallet.get('attributes', {})
            symbol = attr.get('symbol')
            qty = float(attr.get('balance', 0))
            
            # Filtriamo solo gli asset che possiedi (escludendo l'Euro)
            if qty > 0 and symbol != 'EUR':
                # --- LOGICA CALCOLO P&L ---
                # Nota: Bitpanda API v1 a volte non fornisce il 'buy_price' diretto.
                # Qui usiamo un valore di esempio che potrai mappare con i tuoi dati reali.
                prezzo_carico = float(attr.get('average_price', 0)) 
                
                # Simulo un prezzo attuale (In futuro lo prenderemo via API)
                # Per ora facciamo una variazione fittizia per vedere la grafica
                prezzo_attuale = prezzo_carico * 1.05 if prezzo_carico > 0 else 0
                
                if prezzo_carico > 0:
                    gain_loss = ((prezzo_attuale - prezzo_carico) / prezzo_carico) * 100
                    valore_attuale = qty * prezzo_attuale
                    
                    # Grafica personalizzata per ogni azione
                    with st.container():
                        c1, c2 = st.columns([1, 1])
                        c1.write(f"**{symbol}**")
                        c1.caption(f"Q.tà: {qty:.4f}")
                        
                        # Colore verde se in gain, rosso se in loss
                        color = "normal" if gain_loss >= 0 else "inverse"
                        c2.metric("Valore", f"{valore_attuale:.2f}€", f"{gain_loss:.2f}%", delta_color=color)
                        st.divider()
                else:
                    # Se non abbiamo il prezzo di carico, mostriamo solo la quantità
                    st.write(f"**{symbol}**")
                    st.write(f"Quantità: {qty:.4f}")
                    st.caption("Prezzo di carico non disponibile")
                    st.divider()
    else:
        st.error(f"Errore: {status}")
