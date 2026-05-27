import numpy as np

class ScalperFuturesStrategy:
    def __init__(self, mtf_data):
        self.df_1m = mtf_data['1m']
        
        # Parámetros para apalancamiento 50x
        self.leverage = 50
        
        # SL ajustado y TP dinámico (scalping puro)
        self.atr_sl_multiplier = 0.5  # Stop Loss a 0.5x ATR
        self.atr_tp_multiplier = 0.8  # Take Profit a 0.8x ATR (Buscando ratios rápidos)
        
    def evaluate(self):
        """
        Evalúa el mercado de 1 minuto para micro-operaciones.
        Retorna: (Signal, Entry, TP, SL, Confianza, Motivo)
        """
        if len(self.df_1m) < 3:
            return "HOLD", 0, 0, 0, 0, "Insuficientes datos de 1m"
            
        last = self.df_1m.iloc[-1]
        prev = self.df_1m.iloc[-2]
        
        entry_price = last['Close']
        
        # Indicadores de la vela actual
        sma_50 = last.get('SMA_50', entry_price)
        sma_200 = last.get('SMA_200', entry_price)
        rsi = last.get('RSI', 50)
        atr = last.get('ATR', entry_price * 0.001) # Default 0.1% si falla
        
        # Tendencia micro (1 minuto)
        trend = "BULLISH" if sma_50 > sma_200 else "BEARISH"
        
        signal = "HOLD"
        confianza = 0
        motivo = "Sin micro-rompimiento válido"
        tp = entry_price
        sl = entry_price
        
        # --- LÓGICA DE ENTRADA SCALPER (LONG) ---
        # 1. Rompimiento del máximo de la vela anterior
        # 2. RSI no está sobrecomprado (< 65)
        # 3. Micro-tendencia alcista
        if entry_price > prev['High'] and rsi < 65 and trend == "BULLISH":
            signal = "LONG"
            confianza = 85
            motivo = f"Micro-Breakout Alcista + Trend BULL + RSI {rsi:.1f}"
            
            # Límites basados en ATR
            distancia_riesgo = atr * self.atr_sl_multiplier
            sl = entry_price - distancia_riesgo
            tp = entry_price + (atr * self.atr_tp_multiplier)
            
        # --- LÓGICA DE ENTRADA SCALPER (SHORT) ---
        # 1. Rompimiento del mínimo de la vela anterior
        # 2. RSI no está sobrevendido (> 35)
        # 3. Micro-tendencia bajista
        elif entry_price < prev['Low'] and rsi > 35 and trend == "BEARISH":
            signal = "SHORT"
            confianza = 85
            motivo = f"Micro-Breakout Bajista + Trend BEAR + RSI {rsi:.1f}"
            
            # Límites basados en ATR
            distancia_riesgo = atr * self.atr_sl_multiplier
            sl = entry_price + distancia_riesgo
            tp = entry_price - (atr * self.atr_tp_multiplier)
            
        return signal, entry_price, tp, sl, confianza, motivo
