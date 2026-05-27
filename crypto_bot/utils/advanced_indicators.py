import pandas as pd
import numpy as np

def calculate_ema(df, period, column='c'):
    return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14, column='c'):
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    loss = loss.replace(0, 1e-10)
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    high_low = df['h'] - df['l']
    high_close = np.abs(df['h'] - df['c'].shift())
    low_close = np.abs(df['l'] - df['c'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def calculate_vwap(df):
    """
    Calcula el Volume Weighted Average Price (VWAP) intrabarra.
    Normalmente el VWAP se resetea por sesión (diario), aquí usaremos un VWAP rodante simple
    para el contexto de la ventana de velas proporcionada.
    """
    q = df['v']
    p = (df['h'] + df['l'] + df['c']) / 3
    
    # Cumulative Volume and Cumulative Price*Volume
    df['vwap'] = (p * q).cumsum() / q.cumsum()
    return df['vwap']

def calculate_bollinger_bands(df, period=20, std_dev=2, column='c'):
    sma = df[column].rolling(window=period).mean()
    std = df[column].rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, lower

def add_all_indicators(df):
    if len(df) < 50:
        return df
        
    df['EMA_20'] = calculate_ema(df, 20)
    df['EMA_50'] = calculate_ema(df, 50)
    df['RSI'] = calculate_rsi(df, 14)
    df['ATR'] = calculate_atr(df, 14)
    df['VWAP'] = calculate_vwap(df)
    
    df['BB_UP'], df['BB_LOW'] = calculate_bollinger_bands(df, 20, 2)
    
    return df
