import os
import requests
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv("config/.env")

class CryptoNewsClient:
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsdata.io/api/1/latest"

    def get_headlines(self, limit=15):
        if not self.api_key:
            return []
            
        params = {
            'apikey': self.api_key,
            'q': 'bitcoin OR crypto OR BTC OR cryptocurrency',
            'language': 'en'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                return [article.get('title', '') for article in results]
            else:
                print(f"Error fetching news: {response.text}")
                return []
        except Exception as e:
            print(f"Exception fetching news: {e}")
            return []

    def analyze_sentiment(self):
        """
        Analiza las noticias diarias y devuelve un sentimiento ponderado:
        ALCISTA, BAJISTA, o NEUTRAL.
        """
        headlines = self.get_headlines()
        if not headlines:
            return "NEUTRAL"
            
        total_polarity = 0
        for text in headlines:
            blob = TextBlob(text)
            total_polarity += blob.sentiment.polarity
            
        avg_score = total_polarity / len(headlines)
        
        if avg_score > 0.1:
            return "ALCISTA"
        elif avg_score < -0.1:
            return "BAJISTA"
        else:
            return "NEUTRAL"
