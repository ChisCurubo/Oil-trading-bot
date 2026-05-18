import pandas as pd
import numpy as np

def calculate_sma(df, period):
    return df['Close'].rolling(window=period).mean()

def calculate_dynamic_support(df, period=20):
    """Mínimo de los últimos N periodos (excluyendo la actual)."""
    return df['Low'].shift(1).rolling(window=period).min()

def calculate_dynamic_resistance(df, period=20):
    """Máximo de los últimos N periodos (excluyendo la actual)."""
    return df['High'].shift(1).rolling(window=period).max()

def calculate_average_volume(df, period=20):
    return df['Volume'].rolling(window=period).mean()

def calculate_rsi(df, period=14):
    """Índice de Fuerza Relativa (RSI)."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    """Rango Verdadero Promedio (ATR)."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calculate_adx(df, period=14):
    """Índice Direccional Promedio (ADX)."""
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = np.abs(minus_dm)
    
    tr = calculate_atr(df, period)
    plus_di = 100 * (plus_dm.rolling(period).mean() / tr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / tr)
    
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    return dx.rolling(window=period).mean()
