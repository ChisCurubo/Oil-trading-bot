import pandas as pd

class RangeTraderWTI:
    """
    Estrategia de Reversión a la Media (Range Trading).
    Ideal para mercados con ADX bajo, operando en 'pisos' (soportes) y 'techos' (resistencias).
    Integra el sentimiento de noticias como filtro de seguridad.
    """
    def __init__(self, df_micro, sentiment):
        self.df_micro = df_micro
        self.sentiment = sentiment # "ALCISTA", "BAJISTA", "NEUTRAL"

    def evaluate(self):
        if self.df_micro is None or len(self.df_micro) < 30:
            return "ESPERAR", None, None, None

        last = self.df_micro.iloc[-1]
        close = float(last['Close'])
        rsi = float(last['RSI'])
        atr = float(last['ATR'])
        support = float(last['Dynamic_Support'])
        resistance = float(last['Dynamic_Resistance'])
        adx = float(last['ADX'])

        # --- LÓGICA DE COMPRA (Pisos) ---
        # 1. El precio está cerca del soporte (piso)
        near_support = close <= support * 1.002 # Dentro del 0.2% del piso
        # 2. RSI indica sobreventa o neutralidad baja
        oversold = rsi < 45
        # 3. Sentimiento NO es bajista (filtro de noticias)
        news_ok_long = self.sentiment in ["ALCISTA", "NEUTRAL"]
        # 4. Mercado no está en una tendencia bajista fuerte (ADX bajo o tendencia suave)
        not_strong_down = not (adx > 30 and close < last['SMA_50'])

        if near_support and oversold and news_ok_long and not_strong_down:
            tp = close + (1.2 * atr)
            sl = close - (1.0 * atr)
            return "CALL (COMPRA)", close, tp, sl

        # --- LÓGICA DE VENTA (Techos / PUT) ---
        # 1. El precio está cerca de la resistencia (techo)
        near_resistance = close >= resistance * 0.998 # Dentro del 0.2% del techo
        # 2. RSI indica sobrecompra o neutralidad alta
        overbought = rsi > 55
        # 3. Sentimiento NO es alcista (filtro de noticias)
        news_ok_short = self.sentiment in ["BAJISTA", "NEUTRAL"]
        # 4. Mercado no está en una tendencia alcista fuerte
        not_strong_up = not (adx > 30 and close > last['SMA_50'])

        if near_resistance and overbought and news_ok_short and not_strong_up:
            tp = close - (1.2 * atr)
            sl = close + (1.0 * atr)
            return "PUT (VENTA)", close, tp, sl

        return "ESPERAR", None, None, None
