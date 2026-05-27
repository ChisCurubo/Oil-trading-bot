import numpy as np

class WhaleFuturesStrategy:
    def __init__(self, mtf_data, mempool_data, news_sentiment):
        self.df_1m = mtf_data['1m']
        self.df_15m = mtf_data['15m']
        self.df_1h = mtf_data['1h']
        self.df_1d = mtf_data['1d']
        
        self.mempool_data = mempool_data
        self.news_sentiment = news_sentiment
        
        # Parámetros para apalancamiento 50x
        self.leverage = 50
        self.max_sl_percent = 0.01 # Max 1% de pérdida del precio real (50% de la posición apalancada)
        
    def evaluate(self):
        """
        Evalúa todas las condiciones y genera una señal de Futuros.
        Retorna: (Signal, Entry, TP, SL, Confianza, Motivo)
        """
        last_1m = self.df_1m.iloc[-1]
        last_15m = self.df_15m.iloc[-1]
        last_1h = self.df_1h.iloc[-1]
        
        entry_price = last_1m['Close']
        
        # 1. Análisis On-Chain (Ballenas)
        whales = self.mempool_data.get('whales_detected', [])
        whale_signal = "NEUTRAL"
        monto_ballena = 0
        if whales:
            monto_ballena = sum(w['btc_amount'] for w in whales)
            # Simplificación: Asumimos que si hay mucho movimiento on-chain y el precio en 15m está cayendo,
            # es una ballena vendiendo (presión bajista). Si el precio sube, presión alcista.
            if last_15m['Close'] < last_15m['Open']:
                whale_signal = "BEARISH_WHALE"
            else:
                whale_signal = "BULLISH_WHALE"
                
        # 2. Análisis Técnico
        # Soportes y Resistencias (15m para alta precisión)
        soporte_15m = last_15m.get('Dynamic_Support', entry_price * 0.99)
        resist_15m = last_15m.get('Dynamic_Resistance', entry_price * 1.01)
        rsi_15m = last_15m.get('RSI', 50)
        
        # Tendencia general
        trend_1h = "BULLISH" if last_1h['Close'] > last_1h.get('EMA_50', 0) else "BEARISH"
        
        signal = "HOLD"
        confianza = 0
        motivo = "Buscando oportunidad..."
        tp = entry_price
        sl = entry_price
        
        # --- LÓGICA DE ENTRADA ALCISTA (LONG) ---
        # Si el RSI está sobrevendido en 15m y estamos cerca del soporte
        distancia_soporte = (entry_price - soporte_15m) / entry_price
        if rsi_15m < 35 and distancia_soporte < 0.005: 
            if trend_1h == "BULLISH" or whale_signal == "BULLISH_WHALE":
                signal = "LONG"
                confianza = 80
                if whale_signal == "BULLISH_WHALE":
                    confianza = 95
                    motivo = f"Rebote en soporte 15m + RSI Sobrevendido + Ballena ({monto_ballena:.0f} BTC)"
                else:
                    motivo = "Rebote en soporte 15m + RSI Sobrevendido a favor de tendencia"
                    
        # --- LÓGICA DE ENTRADA BAJISTA (SHORT) ---
        distancia_resist = (resist_15m - entry_price) / entry_price
        if rsi_15m > 65 and distancia_resist < 0.005:
            if trend_1h == "BEARISH" or whale_signal == "BEARISH_WHALE":
                signal = "SHORT"
                confianza = 80
                if whale_signal == "BEARISH_WHALE":
                    confianza = 95
                    motivo = f"Rechazo en resistencia 15m + RSI Sobrecomprado + Ballena ({monto_ballena:.0f} BTC)"
                else:
                    motivo = "Rechazo en resistencia 15m + RSI Sobrecomprado a favor de tendencia"
                    
        # Filtro de Noticias Macro (Sentimiento Fuerte)
        if signal == "LONG" and self.news_sentiment == "BAJISTA":
            signal = "HOLD"
            motivo = "Señal LONG cancelada por noticias BAJISTAS"
        elif signal == "SHORT" and self.news_sentiment == "ALCISTA":
            signal = "HOLD"
            motivo = "Señal SHORT cancelada por noticias ALCISTAS"
            
        # Cálculo de SL y TP ajustado a 50x (Risk:Reward = 1:2)
        if signal == "LONG":
            # SL justo debajo del soporte, max 1% de caída
            sl_ideal = soporte_15m * 0.999
            if (entry_price - sl_ideal) / entry_price > self.max_sl_percent:
                sl_ideal = entry_price * (1 - self.max_sl_percent)
            sl = sl_ideal
            distancia_riesgo = entry_price - sl
            tp = entry_price + (distancia_riesgo * 2) # Ratio 1:2
            
        elif signal == "SHORT":
            sl_ideal = resist_15m * 1.001
            if (sl_ideal - entry_price) / entry_price > self.max_sl_percent:
                sl_ideal = entry_price * (1 + self.max_sl_percent)
            sl = sl_ideal
            distancia_riesgo = sl - entry_price
            tp = entry_price - (distancia_riesgo * 2) # Ratio 1:2
            
        return signal, entry_price, tp, sl, confianza, motivo
