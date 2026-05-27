import pandas as pd
import numpy as np

def calculate_sma(df, period):
    return df['Close'].rolling(window=period).mean()

def calculate_ema(df, period):
    return df['Close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # Avoid division by zero
    loss = loss.replace(0, 1e-10)
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def calculate_bollinger_bands(df, period=20, std_dev=2):
    sma = calculate_sma(df, period)
    std = df['Close'].rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, lower

def calculate_dynamic_support(df, period=20):
    return df['Low'].rolling(window=period).min()

def calculate_dynamic_resistance(df, period=20):
    return df['High'].rolling(window=period).max()

def identify_trend(df):
    """
    Identifies the trend based on EMA 50 and EMA 200.
    Returns: 'BULLISH', 'BEARISH', or 'SIDEWAYS'
    """
    if 'EMA_50' not in df.columns:
        df['EMA_50'] = calculate_ema(df, 50)
    if 'EMA_200' not in df.columns:
        df['EMA_200'] = calculate_ema(df, 200)
        
    last = df.iloc[-1]
    if pd.isna(last['EMA_200']):
        return "UNKNOWN"
        
    if last['EMA_50'] > last['EMA_200'] and last['Close'] > last['EMA_50']:
        return "BULLISH"
    elif last['EMA_50'] < last['EMA_200'] and last['Close'] < last['EMA_50']:
        return "BEARISH"
    else:
        return "SIDEWAYS"
