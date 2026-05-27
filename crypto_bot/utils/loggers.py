import os
import csv
import logging
from datetime import datetime

def setup_logger(name, log_file='crypto_bot.log'):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh = logging.FileHandler(f'logs/{log_file}', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

class ThoughtLogger:
    def __init__(self, filename='bitacora_analisis.csv'):
        self.filename = filename
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Fecha', 'Precio_1m', 'Precio_15m', 'Precio_1h', 'RSI_15m', 
                    'Tendencia_Macro', 'Soporte_Local', 'Resistencia_Local', 
                    'Volumen_24h', 'Sentimiento_Noticias', 'Estado_Mempool', 
                    'Señal_Ballena', 'Decision', 'Confianza'
                ])

    def registrar_analisis(self, data):
        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('Fecha'), data.get('Precio_1m'), data.get('Precio_15m'),
                data.get('Precio_1h'), data.get('RSI_15m'), data.get('Tendencia_Macro'),
                data.get('Soporte_Local'), data.get('Resistencia_Local'),
                data.get('Volumen_24h'), data.get('Sentimiento_Noticias'),
                data.get('Estado_Mempool'), data.get('Señal_Ballena'),
                data.get('Decision'), data.get('Confianza')
            ])

class TradeLogger:
    def __init__(self, filename='operaciones_backtest.csv'):
        self.filename = filename
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Ticket_ID', 'Fecha_Entrada', 'Tipo', 'Precio_Entrada', 'Apalancamiento',
                    'Fecha_Salida', 'Precio_Salida', 'Resultado_USD', 'Balance_Final',
                    'Razon_Salida', 'Confianza_Entrada'
                ])

    def registrar_trade_cerrado(self, data):
        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('Ticket_ID'), data.get('Fecha_Entrada'), data.get('Tipo'),
                data.get('Precio_Entrada'), data.get('Apalancamiento'),
                data.get('Fecha_Salida'), data.get('Precio_Salida'),
                data.get('Resultado_USD'), data.get('Balance_Final'),
                data.get('Razon_Salida'), data.get('Confianza_Entrada')
            ])

class ProLogger:
    def __init__(self):
        self.bitacora_file = 'logs/pro_bitacora_analisis.csv'
        self.backtest_file = 'logs/pro_operaciones_backtest.csv'
        self._init_csvs()

    def _init_csvs(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        if not os.path.exists(self.bitacora_file):
            with open(self.bitacora_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Symbol', 'Price_1m', 'EMA20', 'EMA50', 'VWAP', 'RSI', 
                    'FundingRate', 'Structure', 'Signal', 'Confidence', 'Reason'
                ])
                
        if not os.path.exists(self.backtest_file):
            with open(self.backtest_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Trade_ID', 'Time_Entry', 'Type', 'Entry_Price', 'Leverage',
                    'Time_Exit', 'Exit_Price', 'PNL_USD', 'Balance',
                    'Reason_Exit', 'Confidence'
                ])

    def log_analysis(self, data):
        with open(self.bitacora_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('Timestamp'), data.get('Symbol'), data.get('Price_1m'),
                data.get('EMA20'), data.get('EMA50'), data.get('VWAP'),
                data.get('RSI'), data.get('FundingRate'), data.get('Structure'),
                data.get('Signal'), data.get('Confidence'), data.get('Reason')
            ])

    def log_trade(self, data):
        with open(self.backtest_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('Trade_ID'), data.get('Time_Entry'), data.get('Type'),
                data.get('Entry_Price'), data.get('Leverage'),
                data.get('Time_Exit'), data.get('Exit_Price'),
                data.get('PNL_USD'), data.get('Balance'),
                data.get('Reason_Exit'), data.get('Confidence')
            ])
