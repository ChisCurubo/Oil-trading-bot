import os
import logging
from dotenv import load_dotenv
import sys

# Añadir el directorio raíz al path para importar core
sys.path.append(os.getcwd())

from core.news_client import NewsClient

# Configurar logging para ver las advertencias
logging.basicConfig(level=logging.WARNING)

load_dotenv("config/.env")
api_key = os.getenv("NEWS_API_KEY")

print(f"Testing NewsClient with API Key: {api_key[:10]}...")

client = NewsClient(api_key)
headlines = client.get_headlines()

print(f"\nHeadlines received: {len(headlines)}")
if headlines:
    for i, h in enumerate(headlines[:5]):
        print(f"{i+1}: {h}")
else:
    print("No headlines returned. Check logs above for errors.")
