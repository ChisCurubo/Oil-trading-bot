import yfinance as yf
import pandas as pd
import logging

def get_wti_mtf_data():
    """
    Descarga datos MTF para el WTI (CL=F).
    Micro configurado a 1 MINUTO para trading de alta frecuencia.
    """
    try:
        ticker = "CL=F"
        # 1. Macro: Diario (6 meses para SMA 200)
        df_macro = yf.download(ticker, period="1y", interval="1d")
        
        # 2. Micro: 1 MINUTO (Yahoo solo permite hasta 7 días para este intervalo)
        df_micro = yf.download(ticker, period="5d", interval="1m")
        
        def clean_and_normalize(df):
            if df is None or df.empty:
                return df
            df_copy = df.copy()
            if df_copy.index.tz is not None:
                df_copy.index = df_copy.index.tz_localize(None)
            if isinstance(df_copy.columns, pd.MultiIndex):
                df_copy.columns = [col[0] for col in df_copy.columns]
            return df_copy[['Open', 'High', 'Low', 'Close', 'Volume']]

        return clean_and_normalize(df_macro), clean_and_normalize(df_micro)
        
    except Exception as e:
        logging.error(f"Error en descarga de datos MTF: {e}")
        return None, None
