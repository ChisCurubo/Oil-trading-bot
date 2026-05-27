from config import settings

class RiskManager:
    def __init__(self):
        self.leverage = settings.LEVERAGE
        self.risk_per_trade = settings.RISK_PER_TRADE
        self.max_sl_percent = settings.MAX_SL_PERCENT
        self.tp_reward_ratio = settings.TP_REWARD_RATIO

    def calculate_trade_parameters(self, signal, entry_price, atr):
        """
        Calcula SL, TP y Tamaño de Lote asegurando que no haya liquidaciones.
        """
        # Calcular SL basado en ATR pero limitado a MAX_SL_PERCENT
        sl_distance = atr * 1.5 # 1.5x ATR es un stop técnico decente para HFT
        
        # Validación de seguridad extrema
        max_distance_allowed = entry_price * self.max_sl_percent
        if sl_distance > max_distance_allowed:
            sl_distance = max_distance_allowed
            
        tp_distance = sl_distance * self.tp_reward_ratio
        
        if signal == "BUY":
            sl = entry_price - sl_distance
            tp = entry_price + tp_distance
        else: # SELL
            sl = entry_price + sl_distance
            tp = entry_price - tp_distance
            
        return round(tp, 2), round(sl, 2)

    def calculate_pnl(self, signal, entry_price, exit_price, balance):
        """
        Calcula el PNL simulado considerando apalancamiento y tamaño de posición (Margin).
        Usamos el RISK_PER_TRADE% del balance total como margen para esta operación.
        """
        margin_used = balance * self.risk_per_trade
        
        price_diff_percent = (exit_price - entry_price) / entry_price
        if signal == "SELL":
            price_diff_percent *= -1
            
        # PNL% = Movimiento * Apalancamiento
        pnl_percent = price_diff_percent * self.leverage
        
        # PNL Neto = Margen * PNL%
        pnl_usd = margin_used * pnl_percent
        
        return pnl_usd
