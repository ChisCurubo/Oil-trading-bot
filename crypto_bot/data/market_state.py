import pandas as pd
from collections import deque

class MarketState:
    def __init__(self, max_klines=500):
        self.max_klines = max_klines
        self.symbol = "BTCUSDT"
        
        # Almacenamiento rápido en memoria
        self.klines_1m = deque(maxlen=max_klines)
        self.klines_5m = deque(maxlen=max_klines)
        
        # Order Book & Live Data
        self.best_bid = 0.0
        self.best_ask = 0.0
        self.funding_rate = 0.0
        self.open_interest = 0.0
        
        # El precio de la última transacción
        self.last_price = 0.0
        self.last_volume = 0.0

    def init_historical_klines(self, timeframe, klines_data):
        """Inicializa las velas históricas (listas de dicts)"""
        target_deque = self.klines_1m if timeframe == "1m" else self.klines_5m
        target_deque.clear()
        for k in klines_data:
            target_deque.append(k)

    def update_kline(self, timeframe, kline_dict):
        """Actualiza la vela actual o añade una nueva al cerrar"""
        target_deque = self.klines_1m if timeframe == "1m" else self.klines_5m
        if not target_deque:
            target_deque.append(kline_dict)
            return

        last_k = target_deque[-1]
        if kline_dict['t'] == last_k['t']:
            # Actualiza la vela en curso
            target_deque[-1] = kline_dict
        elif kline_dict['t'] > last_k['t']:
            # Añade nueva vela
            target_deque.append(kline_dict)

    def get_df(self, timeframe="1m"):
        """Convierte el deque a un DataFrame de Pandas para cálculos matemáticos"""
        target_deque = self.klines_1m if timeframe == "1m" else self.klines_5m
        if not target_deque:
            return pd.DataFrame()
            
        df = pd.DataFrame(list(target_deque))
        df.set_index('t', inplace=True)
        # Convertimos las columnas numéricas
        cols = ['o', 'h', 'l', 'c', 'v']
        df[cols] = df[cols].astype(float)
        return df

    def update_book_ticker(self, bid, ask):
        self.best_bid = float(bid)
        self.best_ask = float(ask)

    def update_trade(self, price, qty):
        self.last_price = float(price)
        self.last_volume = float(qty)
