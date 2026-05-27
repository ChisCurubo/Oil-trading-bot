import pandas as pd
import asyncio
from core.rest_client import BinanceRestClient

async def fetch_all_timeframes(symbol="BTCUSDT"):
    client = BinanceRestClient()
    
    # Descargar datos asíncronamente para máxima velocidad
    tasks = [
        client.get_historical_klines(symbol, "1m", 100),
        client.get_historical_klines(symbol, "15m", 100),
        client.get_historical_klines(symbol, "1h", 200),
        client.get_historical_klines(symbol, "1d", 100)
    ]
    
    results = await asyncio.gather(*tasks)
    return results

def format_binance_df(klines):
    if not klines:
        return pd.DataFrame()
        
    df = pd.DataFrame(klines)
    # Convertir nombres de columnas a formato yfinance para compatibilidad con el resto del código
    df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
    df.set_index('t', inplace=True) # Open time as index
    
    # Asegurar tipo numérico
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[cols] = df[cols].astype(float)
    return df

def get_crypto_mtf_data(ticker="BTCUSDT"):
    """
    Obtiene múltiples marcos temporales para Bitcoin usando la API de Binance Futures.
    Retorna un diccionario con df_1m, df_15m, df_1h, df_1d
    """
    try:
        results = asyncio.run(fetch_all_timeframes(ticker))
        
        df_1m = format_binance_df(results[0])
        df_15m = format_binance_df(results[1])
        df_1h = format_binance_df(results[2])
        df_1d = format_binance_df(results[3])
        
        if df_1m.empty or df_15m.empty or df_1h.empty or df_1d.empty:
            print("Advertencia: No se pudieron descargar todos los timeframes de Binance.")
            return None
            
        return {
            "1m": df_1m,
            "15m": df_15m,
            "1h": df_1h,
            "1d": df_1d
        }
    except Exception as e:
        print(f"Error descargando datos de Binance para {ticker}: {e}")
        return None
