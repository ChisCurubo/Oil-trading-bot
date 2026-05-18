import pandas as pd

class ScalperWTI:
    """
    Estrategia de Micro-Transacciones (Scalping).
    Busca ganar poco o perder poco aprovechando impulsos inmediatos (momentum).
    Utiliza rompimientos de la vela anterior y un RSI rápido.
    """
    def __init__(self, df_micro, sentiment):
        self.df_micro = df_micro
        self.sentiment = sentiment # "ALCISTA", "BAJISTA", "NEUTRAL"

    def evaluate(self):
        if self.df_micro is None or len(self.df_micro) < 10:
            return "ESPERAR", None, None, None

        # Obtener la vela actual y la vela anterior
        current_candle = self.df_micro.iloc[-1]
        prev_candle = self.df_micro.iloc[-2]

        close = float(current_candle['Close'])
        rsi = float(current_candle['RSI'])
        atr = float(current_candle['ATR'])
        
        # Rompimientos mínimos (Micro-Breakout)
        # Romper el máximo o mínimo de la vela anterior indica momentum inmediato
        micro_break_up = close > float(prev_candle['High'])
        micro_break_down = close < float(prev_candle['Low'])

        # Riesgo ultra-ajustado: Ganar poco / Perder poco (0.6 veces el ATR)
        risk_multiplier = 0.6 
        
        # --- LÓGICA DE COMPRA RÁPIDA (CALL) ---
        # 1. Rompimiento al alza
        # 2. RSI muestra fuerza (ej. > 55) pero no extrema sobrecompra (< 80)
        # 3. Sentimiento no es bajista
        if micro_break_up and (55 < rsi < 80) and self.sentiment in ["ALCISTA", "NEUTRAL"]:
            tp = close + (risk_multiplier * atr)
            sl = close - (risk_multiplier * atr)
            return "CALL (SCALP)", close, tp, sl

        # --- LÓGICA DE VENTA RÁPIDA (PUT) ---
        # 1. Rompimiento a la baja
        # 2. RSI muestra debilidad (ej. < 45) pero no extrema sobreventa (> 20)
        # 3. Sentimiento no es alcista
        if micro_break_down and (20 < rsi < 45) and self.sentiment in ["BAJISTA", "NEUTRAL"]:
            tp = close - (risk_multiplier * atr)
            sl = close + (risk_multiplier * atr)
            return "PUT (SCALP)", close, tp, sl

        return "ESPERAR", None, None, None
