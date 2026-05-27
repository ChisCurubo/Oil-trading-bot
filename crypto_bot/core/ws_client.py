import json
import asyncio
import websockets

class BinanceWSClient:
    def __init__(self, market_state, symbol="btcusdt"):
        self.market_state = market_state
        self.symbol = symbol.lower()
        self.base_url = "wss://fstream.binance.com/ws"
        # Streams a suscribir
        self.streams = [
            f"{self.symbol}@kline_1m",
            f"{self.symbol}@kline_5m",
            f"{self.symbol}@bookTicker",
            f"{self.symbol}@trade"
        ]
        self.ws_url = f"wss://fstream.binance.com/stream?streams={'/'.join(self.streams)}"

    async def connect_and_listen(self):
        while True:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    print(f"✅ Conectado a Binance WebSockets: {self.symbol}")
                    while True:
                        msg = await ws.recv()
                        self._handle_message(json.loads(msg))
            except Exception as e:
                print(f"❌ Desconectado de WebSocket. Reconectando en 5s... Error: {e}")
                await asyncio.sleep(5)

    def _handle_message(self, msg):
        if 'data' not in msg:
            return
            
        stream = msg['stream']
        data = msg['data']
        
        if "@kline_" in stream:
            # Procesar vela
            k = data['k']
            kline_dict = {
                't': k['t'],
                'o': float(k['o']),
                'h': float(k['h']),
                'l': float(k['l']),
                'c': float(k['c']),
                'v': float(k['v']),
                'closed': k['x']
            }
            timeframe = "1m" if "1m" in stream else "5m"
            self.market_state.update_kline(timeframe, kline_dict)
            
        elif "@bookTicker" in stream:
            # Procesar el Order Book (Mejor compra y venta)
            self.market_state.update_book_ticker(data['b'], data['a'])
            
        elif "@trade" in stream:
            # Procesar última transacción
            self.market_state.update_trade(data['p'], data['q'])
