class SMCLogic:
    def __init__(self):
        pass

    def detect_market_structure(self, df_5m):
        """
        Analiza la estructura del mercado en 5m para definir la tendencia principal.
        Retorna: 'BULLISH', 'BEARISH' o 'CHOPPY'
        """
        if len(df_5m) < 50:
            return "CHOPPY"
            
        last = df_5m.iloc[-1]
        
        # Filtro de lateralidad por Bollinger Bands
        bb_width = (last['BB_UP'] - last['BB_LOW']) / last['c']
        if bb_width < 0.002: # Si las bandas están extremadamente comprimidas (< 0.2%)
            return "CHOPPY"
            
        if last['c'] > last['EMA_20'] and last['EMA_20'] > last['EMA_50']:
            return "BULLISH"
        elif last['c'] < last['EMA_20'] and last['EMA_20'] < last['EMA_50']:
            return "BEARISH"
            
        return "CHOPPY"

    def evaluate_1m(self, df_1m, structure_5m, market_state):
        """
        Busca entradas precisas usando VWAP, OrderBook y RSI.
        """
        if len(df_1m) < 50 or structure_5m == "CHOPPY":
            return "HOLD", 0, "Mercado sin dirección clara o sin datos suficientes"
            
        last = df_1m.iloc[-1]
        prev = df_1m.iloc[-2]
        
        c = last['c']
        rsi = last['RSI']
        vwap = last['VWAP']
        
        # Funding rate extremo desaconseja ir a favor del rebaño
        funding = market_state.funding_rate
        
        # SMC / Liquidity Sweep (Simplificado)
        # Un fake breakout bajista: El precio rompe el mínimo anterior, pero cierra muy por encima y el RSI está sobrevendido.
        is_bullish_sweep = (last['l'] < prev['l']) and (c > prev['c']) and (rsi < 40)
        
        # Fake breakout alcista: Rompe máximo anterior, pero cierra muy por debajo y RSI sobrecomprado.
        is_bearish_sweep = (last['h'] > prev['h']) and (c < prev['c']) and (rsi > 60)
        
        confidence = 0
        signal = "HOLD"
        reason = "Monitorizando..."

        # LONG Logic
        if structure_5m == "BULLISH":
            # Si el precio toca/rebota en VWAP o hace un sweep alcista
            if c > vwap and (is_bullish_sweep or (prev['l'] <= vwap < prev['c'])):
                if funding < 0.0005: # No operar long si el funding es hiper positivo (peligro de long squeeze)
                    signal = "BUY"
                    confidence = 85 if is_bullish_sweep else 75
                    reason = "Barrido de liquidez alcista / Rebote en VWAP a favor de tendencia."
                    
        # SHORT Logic
        elif structure_5m == "BEARISH":
            if c < vwap and (is_bearish_sweep or (prev['h'] >= vwap > prev['c'])):
                if funding > -0.0005:
                    signal = "SELL"
                    confidence = 85 if is_bearish_sweep else 75
                    reason = "Barrido de liquidez bajista / Rechazo en VWAP a favor de tendencia."

        return signal, confidence, reason
