import time
import os
from datetime import datetime
from dotenv import load_dotenv

from core.data_client import get_crypto_mtf_data
from core.whatsapp_client import WhatsAppClient
from core.discord_client import DiscordClient
from strategies.scalper_futures_strategy import ScalperFuturesStrategy
from utils.loggers import setup_logger, ThoughtLogger, TradeLogger
from utils.indicators import calculate_sma, calculate_rsi, calculate_atr

load_dotenv("config/.env")
logger = setup_logger("CryptoBot_Scalper")

def prep_scalping_indicators(df_dict):
    """Calcula indicadores necesarios en el dataframe de 1 minuto"""
    if df_dict is None or len(df_dict['1m']) < 200: 
        return False
    
    df_1m = df_dict['1m']
    df_1m['SMA_50'] = calculate_sma(df_1m, 50)
    df_1m['SMA_200'] = calculate_sma(df_1m, 200)
    df_1m['RSI'] = calculate_rsi(df_1m, 14)
    df_1m['ATR'] = calculate_atr(df_1m, 14)
    
    return True

def run_scalper():
    logger.info("="*70)
    logger.info("⚡ SISTEMA BITCOIN SCALPER ACTIVADO (FUTUROS 50x) ⚡")
    logger.info("="*70)
    
    wp_client = WhatsAppClient()
    discord_client = DiscordClient()
    
    # Creamos archivos separados para el scalper si se desea, o usamos los mismos.
    # Por defecto usamos los mismos para centralizar el PNL.
    thought_ledger = ThoughtLogger()
    trade_ledger = TradeLogger()
    
    # Control State
    operacion_abierta = False
    datos_trade = {}
    ticket_id = 1000 # Empieza en 1000 para diferenciar del bot principal
    balance_usd = 1000.0 # Balance inicial simulado
    
    while True:
        try:
            print(f"\n{'#'*70}")
            print(f"🔄 ESCANEO SCALPER (30s): {datetime.now().strftime('%H:%M:%S')} | BALANCE: ${balance_usd:.2f}")
            print(f"{'#'*70}")
                
            # 1. Fetch MTF Data (Solo necesitamos 1m, pero get_crypto_mtf_data baja todos)
            mtf_data = get_crypto_mtf_data("BTC-USD")
            if not prep_scalping_indicators(mtf_data):
                print("⏳ Esperando suficientes datos de 1 minuto para inicializar SMA 200...")
                time.sleep(15)
                continue
                
            # 2. Evaluate Strategy
            strategy = ScalperFuturesStrategy(mtf_data)
            signal, entry, tp, sl, confianza, motivo = strategy.evaluate()
            
            # Logger context
            last_1m = mtf_data['1m'].iloc[-1]
            prev_1m = mtf_data['1m'].iloc[-2]
            
            print(f"📊 PRECIO: ${last_1m['Close']:.2f} | RSI: {last_1m['RSI']:.1f} | ATR: {last_1m['ATR']:.2f}")
            print(f"📏 VELA ANTERIOR: Max ${prev_1m['High']:.2f} - Min ${prev_1m['Low']:.2f}")
            print(f"⚖️  SEÑAL ACTUAL: {signal}")
            
            # Guardamos en bitácora
            thought_ledger.registrar_analisis({
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Precio_1m': round(last_1m['Close'], 2),
                'Precio_15m': "N/A",
                'Precio_1h': "N/A",
                'RSI_15m': round(last_1m['RSI'], 1), # Guardamos el de 1m aquí por conveniencia
                'Tendencia_Macro': "BULLISH" if last_1m['SMA_50'] > last_1m['SMA_200'] else "BEARISH",
                'Soporte_Local': round(prev_1m['Low'], 2),
                'Resistencia_Local': round(prev_1m['High'], 2),
                'Volumen_24h': "SCALPER",
                'Sentimiento_Noticias': "N/A",
                'Estado_Mempool': "N/A",
                'Señal_Ballena': "N/A",
                'Decision': signal,
                'Confianza': f"{confianza}%"
            })
            
            # 3. Execution Logic
            if not operacion_abierta:
                if signal in ["LONG", "SHORT"]:
                    msg = (f"⚡ ALERTA SCALPER 50x ⚡\n\n"
                           f"Señal: {'🟢' if signal == 'LONG' else '🔴'} {signal}\n"
                           f"Entrada: ${entry:.2f}\n"
                           f"TP: ${tp:.2f} | SL: ${sl:.2f}\n"
                           f"Confianza: {confianza}%")
                    wp_client.send_message(msg)
                    discord_client.send_message(msg)
                    operacion_abierta = True
                    datos_trade = {
                        'Ticket_ID': ticket_id,
                        'Fecha_Entrada': datetime.now(),
                        'Tipo': signal,
                        'Precio_Entrada': entry,
                        'TP': tp,
                        'SL': sl,
                        'Lotes': (balance_usd * 0.1) / entry, # Arriesga 10% del margen
                        'Confianza': confianza
                    }
                    ticket_id += 1
                    logger.warning(f"⚡ MICRO-OPERACION ABIERTA: {signal} a {entry:.2f} | TP: {tp:.2f} | SL: {sl:.2f}")
                else:
                    print(f"   ⏳ Monitorizando. Motivo actual: {motivo}")
            else:
                print(f"🚀 POSICIÓN SCALP ACTIVA: {datos_trade['Tipo']} | Ent: ${datos_trade['Precio_Entrada']:.2f} | TP: ${datos_trade['TP']:.2f} | SL: ${datos_trade['SL']:.2f}")
                
                # Exit Logic (Close Price)
                hit_tp = False; hit_sl = False
                current_price = last_1m['Close']
                
                if datos_trade['Tipo'] == "LONG":
                    if current_price >= datos_trade['TP']: hit_tp = True
                    elif current_price <= datos_trade['SL']: hit_sl = True
                elif datos_trade['Tipo'] == "SHORT":
                    if current_price <= datos_trade['TP']: hit_tp = True
                    elif current_price >= datos_trade['SL']: hit_sl = True
                    
                if hit_tp or hit_sl:
                    precio_salida = current_price
                    razon = "MICRO_TP" if hit_tp else "MICRO_SL"
                    
                    # Calcular PNL con Apalancamiento 50x
                    porcentaje_movimiento = (precio_salida - datos_trade['Precio_Entrada']) / datos_trade['Precio_Entrada']
                    if datos_trade['Tipo'] == "SHORT":
                        porcentaje_movimiento *= -1
                        
                    pnl_porcentual_apalancado = porcentaje_movimiento * 50
                    pnl_usd = (balance_usd * 0.1) * pnl_porcentual_apalancado
                    
                    balance_usd += pnl_usd
                    
                    trade_ledger.registrar_trade_cerrado({
                        'Ticket_ID': datos_trade['Ticket_ID'],
                        'Fecha_Entrada': datos_trade['Fecha_Entrada'],
                        'Tipo': datos_trade['Tipo'],
                        'Precio_Entrada': round(datos_trade['Precio_Entrada'], 2),
                        'Apalancamiento': '50x',
                        'Fecha_Salida': datetime.now(),
                        'Precio_Salida': round(precio_salida, 2),
                        'Resultado_USD': round(pnl_usd, 2),
                        'Balance_Final': round(balance_usd, 2),
                        'Razon_Salida': razon,
                        'Confianza_Entrada': datos_trade['Confianza']
                    })
                    msg_exit = (f"✅ ALERTA CIERRE SCALPER ✅\n\n"
                                f"Operación: {datos_trade['Tipo']} CERRADA\n"
                                f"Razón: {razon}\n"
                                f"PNL: {'🟢' if pnl_usd > 0 else '🔴'} ${pnl_usd:.2f}\n"
                                f"Balance Nuevo: ${balance_usd:.2f}")
                    wp_client.send_message(msg_exit)
                    discord_client.send_message(msg_exit)
                    
                    logger.warning(f"💰 MICRO-OPERACION CERRADA: {razon} | PNL: ${pnl_usd:.2f}")
                    operacion_abierta = False
            
            # Polling Interval más rápido para scalping (30s)
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ Error crítico en scalper: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_scalper()
