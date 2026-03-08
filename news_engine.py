import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Usa la tua chiave di NewsAPI.org o simili
NEWS_API_KEY = "f47b85db22664beba249feed052403c3" 

def get_latest_sentiment(keyword):
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt"
    response = requests.get(url).json()
    
    articles = response.get('articles', [])[:5] # Prendiamo le ultime 5 notizie
    if not articles:
        return 0 # Neutrale se non ci sono news
    
    analyzer = SentimentIntensityAnalyzer()
    total_score = 0
    
    for art in articles:
        text = art['title'] + " " + (art['description'] or "")
        score = analyzer.polarity_scores(text)['compound']
        total_score += score
    
    avg_sentiment = total_score / len(articles)
    return avg_sentiment

# Esempio: Il bot controlla il sentiment per Tesla
# sentiment_tsla = get_latest_sentiment("Tesla")
