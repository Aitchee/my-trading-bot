import etoro_module # Il file che abbiamo creato prima
import news_engine

ASSETS_TO_WATCH = ["BTC", "TSLA", "AAPL", "ETH"]

def run_bot_cycle():
    for asset in ASSETS_TO_WATCH:
        sentiment = news_engine.get_latest_sentiment(asset)
        print(f"Sentiment per {asset}: {sentiment}")
        
        if sentiment > 0.4:
            print(f"🚀 Sentiment POSITIVO per {asset}. Invio ordine a eToro...")
            # Qui chiameremo la funzione di acquisto di eToro
            # etoro_module.place_order(asset, amount=100)
            
        elif sentiment < -0.4:
            print(f"⚠️ Sentiment NEGATIVO per {asset}. Valutazione vendita...")
            # etoro_module.close_position(asset)

if __name__ == "__main__":
    run_bot_cycle()
