import aiohttp
import time
import json
import os
from dotenv import load_dotenv

load_dotenv("config/.env")

class BinanceRestClient:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.api_key = os.getenv("BINANCE_API_KEY")

    async def _get(self, endpoint, params=None):
        headers = {}
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}{endpoint}", params=params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"❌ Error Binance REST {endpoint}: {response.status}")
                        return None
            except Exception as e:
                print(f"❌ Exception Binance REST: {e}")
                return None

    async def get_historical_klines(self, symbol="BTCUSDT", interval="1m", limit=200):
        """Descarga las últimas velas para inicializar los indicadores."""
        data = await self._get("/fapi/v1/klines", params={"symbol": symbol, "interval": interval, "limit": limit})
        if not data:
            return []
            
        # Formatear al estándar del market_state
        klines = []
        for row in data:
            klines.append({
                't': row[0],     # Open time
                'o': float(row[1]),
                'h': float(row[2]),
                'l': float(row[3]),
                'c': float(row[4]),
                'v': float(row[5])
            })
        return klines

    async def get_funding_rate(self, symbol="BTCUSDT"):
        data = await self._get("/fapi/v1/premiumIndex", params={"symbol": symbol})
        if data and isinstance(data, dict):
            return float(data.get('lastFundingRate', 0))
        return 0.0

    async def get_open_interest(self, symbol="BTCUSDT"):
        data = await self._get("/fapi/v1/openInterest", params={"symbol": symbol})
        if data and isinstance(data, dict):
            return float(data.get('openInterest', 0))
        return 0.0
