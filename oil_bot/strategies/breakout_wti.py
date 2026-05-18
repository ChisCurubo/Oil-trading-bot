import pandas as pd

class BreakoutWTI:
    """
    Estrategia Avanzada v1.2: Análisis de Múltiples Marcos Temporales (MTF).
    Filtra señales de 1H basadas en la tendencia de la SMA 200 Diaria.
    """
    def __init__(self, df_micro, df_macro):
        self.df_micro = df_micro
        self.df_macro = df_macro

    def evaluate(self):
        """
        Evalúa el mercado aplicando el filtro Top-Down (Macro -> Micro).
        """
        # --- VALIDACIÓN MACRO (DIARIO) ---
        if self.df_macro is None or len(self.df_macro) < 200:
            return "ESPERAR", None, None, None

        macro_last = self.df_macro.iloc[-1]
        macro_close = float(macro_last['Close'])
        macro_sma200 = float(macro_last['SMA_200'])
        
        # Reglas Maestras Direccionales
        macro_bullish = macro_close > macro_sma200
        macro_bearish = macro_close < macro_sma200

        # --- VALIDACIÓN MICRO (1 HORA) ---
        if self.df_micro is None or len(self.df_micro) < 50:
            return "ESPERAR", None, None, None

        micro_last = self.df_micro.iloc[-1]
        close = float(micro_last['Close'])
        atr = float(micro_last['ATR'])
        adx = float(micro_last['ADX'])
        rsi = float(micro_last['RSI'])
        
        # Filtro de Fuerza de Tendencia (ADX > 25)
        if adx <= 25:
            return "ESPERAR", None, None, None

        # --- SEÑAL DE COMPRA (Solo si Macro es Alcista) ---
        if macro_bullish:
            long_tech = (close > micro_last['SMA_50'])
            long_break = (close > micro_last['Dynamic_Resistance'])
            long_momentum = (50 < rsi < 70)
            
            if long_tech and long_break and long_momentum:
                return "COMPRA", close, close + (1.5 * atr), close - (1.5 * atr)

        # --- SEÑAL DE VENTA (Solo si Macro es Bajista) ---
        if macro_bearish:
            short_tech = (close < micro_last['SMA_50'])
            short_break = (close < micro_last['Dynamic_Support'])
            short_momentum = (30 < rsi < 50)
            
            if short_tech and short_break and short_momentum:
                return "VENTA", close, close - (1.5 * atr), close + (1.5 * atr)

        return "ESPERAR", None, None, None
