import time
import os
from datetime import datetime
from dotenv import load_dotenv

from core.data_client import get_crypto_mtf_data
from core.mempool_client import MempoolClient
from core.whatsapp_client import WhatsAppClient
from core.discord_client import DiscordClient
from core.news_client import CryptoNewsClient
from strategies.whale_futures_strategy import WhaleFuturesStrategy
from utils.loggers import setup_logger, ThoughtLogger, TradeLogger
from utils.indicators import calculate_ema, calculate_rsi, calculate_dynamic_support, calculate_dynamic_resistance

load_dotenv("config/.env")
logger = setup_logger("CryptoBot_Main")

def prep_indicators(df_dict):
    """Calcula indicadores necesarios en cada dataframe"""
    if df_dict is None: return False
    
    # 15m Indicators
    df_15m = df_dict['15m']
    df_15m['RSI'] = calculate_rsi(df_15m, 14)
    df_15m['Dynamic_Support'] = calculate_dynamic_support(df_15m, 20)
    df_15m['Dynamic_Resistance'] = calculate_dynamic_resistance(df_15m, 20)
    
    # 1h Indicators
    df_1h = df_dict['1h']
    df_1h['EMA_50'] = calculate_ema(df_1h, 50)
    df_1h['EMA_200'] = calculate_ema(df_1h, 200)
    
    return True

def run_bot():
    logger.info("="*70)
    logger.info("🐋 SISTEMA BITCOIN WHALE TRACKER ACTIVADO (FUTUROS 50x) 🐋")
    logger.info("="*70)
    
    mempool_client = MempoolClient()
    wp_client = WhatsAppClient()
    discord_client = DiscordClient()
    news_client = CryptoNewsClient()
    
    thought_ledger = ThoughtLogger()
    trade_ledger = TradeLogger()
    
    # Control State
    operacion_abierta = False
    datos_trade = {}
    ticket_id = 1
    balance_usd = 1000.0 # Balance inicial simulado
    
    # News Cache (12 hours)
    last_news_fetch = 0
    NEWS_FETCH_INTERVAL = 12 * 3600
    news_sentiment = "NEUTRAL"
    
    # Hourly Alert Cron
    last_hourly_alert = 0
    HOURLY_ALERT_INTERVAL = 3600
    
    while True:
        try:
            current_time = time.time()
            
            # 1. Fetch News
            if current_time - last_news_fetch >= NEWS_FETCH_INTERVAL:
                print("\n📰 Obteniendo Noticias Diarias de Cripto...")
                news_sentiment = news_client.analyze_sentiment()
                last_news_fetch = current_time
                
            # 2. Fetch MTF Data from Binance
            mtf_data = get_crypto_mtf_data("BTCUSDT")
            if not prep_indicators(mtf_data):
                time.sleep(15)
                continue
                
            # 3. Fetch Mempool Data
            mempool_data = mempool_client.get_network_status()
            
            # Extraer variables para el dashboard
            last_1m = mtf_data['1m'].iloc[-1]
            last_15m = mtf_data['15m'].iloc[-1]
            last_1h = mtf_data['1h'].iloc[-1]
            
            current_price = last_1m['Close']
            rsi_15m = last_15m.get('RSI', 50)
            sma50_1h = last_1h.get('EMA_50', current_price)
            sma200_1h = last_1h.get('EMA_200', current_price)
            tendencia = "ALCISTA" if sma50_1h > sma200_1h else "BAJISTA"
            
            whales_text = f"{len(mempool_data['whales_detected'])} detectadas" if mempool_data['whales_detected'] else "Ninguna"

            print(f"\n{'#'*70}")
            print(f"🔄 DASHBOARD WHALE BOT: {datetime.now().strftime('%H:%M:%S')} | BALANCE: ${balance_usd:.2f}")
            print(f"{'#'*70}")
            print(f"💰 Precio BTC: ${current_price:.2f}")
            print(f"📈 Tendencia 1H: {tendencia} | RSI 15m: {rsi_15m:.1f}")
            print(f"📰 Sentimiento Noticias: {news_sentiment}")
            print(f"🐋 Ballenas (Mempool): {whales_text}")
            print(f"{'#'*70}")
            
            # Enviar Reporte Horario
            if current_time - last_hourly_alert >= HOURLY_ALERT_INTERVAL:
                hourly_msg = (f"⏱️ REPORTE HORARIO WHALE BOT ⏱️\n\n"
                              f"💰 Precio BTC: ${current_price:.2f}\n"
                              f"📈 Tendencia (1H): {tendencia}\n"
                              f"🌡️ RSI (15m): {rsi_15m:.1f}\n"
                              f"🐋 Actividad Ballenas: {whales_text}\n"
                              f"📰 Noticias Generales: {news_sentiment}")
                wp_client.send_message(hourly_msg)
                discord_client.send_message(hourly_msg)
                last_hourly_alert = current_time
            
            # 4. Evaluate Strategy
            strategy = WhaleFuturesStrategy(mtf_data, mempool_data, news_sentiment)
            signal, entry, tp, sl, confianza, motivo = strategy.evaluate()
            
            # Logger context
                
            thought_ledger.registrar_analisis({
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Precio_1m': round(last_1m['Close'], 2),
                'Precio_15m': round(last_15m['Close'], 2),
                'Precio_1h': round(last_1h['Close'], 2),
                'RSI_15m': round(last_15m.get('RSI', 50), 1),
                'Tendencia_Macro': "BULLISH" if last_1h['Close'] > last_1h.get('EMA_50', 0) else "BEARISH",
                'Soporte_Local': round(last_15m.get('Dynamic_Support', 0), 2),
                'Resistencia_Local': round(last_15m.get('Dynamic_Resistance', 0), 2),
                'Volumen_24h': "N/A", # yfinance volume is not always accurate live
                'Sentimiento_Noticias': news_sentiment,
                'Estado_Mempool': mempool_data['estado'],
                'Señal_Ballena': whales_text,
                'Decision': signal,
                'Confianza': f"{confianza}%"
            })
            
            print(f"⚖️  SEÑAL ACTUAL: {signal} | Confianza: {confianza}%")
            
            # 5. Execution Logic
            if not operacion_abierta:
                if signal in ["LONG", "SHORT"]:
                    # Enviar WhatsApp
                    msg = (f"🚨 ALERTA CRIPTO WHALE BOT 🚨\n\n"
                           f"Señal: 🟢 {signal}\n" if signal == "LONG" else f"Señal: 🔴 {signal}\n"
                           f"Confianza: {confianza}%\n"
                           f"Motivo: {motivo}\n"
                           f"Apalancamiento Recomendado: 50x\n"
                           f"Entrada: ${entry:.2f}\n"
                           f"Take Profit: ${tp:.2f}\n"
                           f"Stop Loss: ${sl:.2f}\n\n"
                           f"Sentimiento Global: {news_sentiment}")
                    
                    if mempool_data['whales_detected']:
                        msg += f"\n🔗 Link Whale TX: {mempool_data['whales_detected'][0]['link']}"
                        
                    wp_client.send_message(msg)
                    discord_client.send_message(msg)
                    
                    # Simular la entrada
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
                    logger.warning(f"🚀 OPERACION ABIERTA: {signal} a {entry:.2f}")
                else:
                    print(f"   ⏳ Monitorizando. Motivo actual: {motivo}")
            else:
                print(f"🚀 POSICIÓN ACTIVA: {datos_trade['Tipo']} | Ent: ${datos_trade['Precio_Entrada']:.2f} | TP: ${datos_trade['TP']:.2f} | SL: ${datos_trade['SL']:.2f}")
                
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
                    razon = "TAKE_PROFIT" if hit_tp else "STOP_LOSS"
                    
                    # Calcular PNL con Apalancamiento 50x
                    # PNL % = ((Precio_Salida - Precio_Entrada) / Precio_Entrada) * Apalancamiento
                    porcentaje_movimiento = (precio_salida - datos_trade['Precio_Entrada']) / datos_trade['Precio_Entrada']
                    if datos_trade['Tipo'] == "SHORT":
                        porcentaje_movimiento *= -1
                        
                    pnl_porcentual_apalancado = porcentaje_movimiento * 50
                    pnl_usd = (balance_usd * 0.1) * pnl_porcentual_apalancado # PNL basado en margen usado
                    
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
                    
                    # Notificar cierre
                    msg = (f"✅ ALERTA CIERRE CRIPTO ✅\n\n"
                           f"Operación: {datos_trade['Tipo']} CERRADA\n"
                           f"Razón: {razon}\n"
                           f"PNL: {'🟢' if pnl_usd > 0 else '🔴'} ${pnl_usd:.2f}\n"
                           f"Balance Nuevo: ${balance_usd:.2f}")
                    wp_client.send_message(msg)
                    discord_client.send_message(msg)
                    
                    logger.warning(f"💰 OPERACION CERRADA: {razon} | PNL: ${pnl_usd:.2f}")
                    operacion_abierta = False
            
            # Polling Interval (yfinance 1m data needs ~60s)
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"❌ Error crítico en bucle principal: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_bot()
