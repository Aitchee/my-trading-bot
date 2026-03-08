from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analizza_notizia(titolo_news):
    # Esempio: "Fed cuts interest rates, markets surge"
    vs = analyzer.polarity_scores(titolo_news)
    return vs['compound'] # Restituisce un valore tra -1 (pessimo) e +1 (ottimo)

# Test veloce
print(analizza_notizia("Apple reports record profits and iPhone sales")) 
# Output probabile: 0.7 (Segnale di acquisto)
