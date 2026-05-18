import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Importaciones locales
from core.data_client import get_wti_mtf_data
from core.news_client import NewsClient
from fundamentals.sentiment import analyze_market_sentiment
from strategies.scalper_wti import ScalperWTI
from utils.indicators import *
from utils.trade_logger import TradeLogger
from utils.thought_logger import ThoughtLogger
from utils.logger import setup_logger

# Configuración inicial
load_dotenv("config/.env")
logger = setup_logger("OilBot_Scalper")

# --- PARÁMETROS FINANCIEROS ---
CAPITAL_INICIAL = 10000.0
RIESGO_POR_TRADE = 0.01  # 1% del capital (aunque en scalping podríamos bajarlo, lo mantenemos por consistencia)

def run_scalper_monitor():
    """
    Panel de Control: Estrategia de Scalping (Micro-Transacciones).
    Busca pequeños rompimientos y momentum rápido, con SL y TP muy ajustados.
    """
    logger.info("="*70)
    logger.info("⚡ SISTEMA WTI SCALPER - ALTA FRECUENCIA ACTIVADO")
    logger.info(f"💰 CAPITAL: ${CAPITAL_INICIAL} USD")
    logger.info("="*70)
    
    trade_ledger = TradeLogger()
    thought_ledger = ThoughtLogger() # Añadido para bitácora continua
    balance_actual = CAPITAL_INICIAL
    operacion_abierta = False
    datos_trade = {}
    ticket_id = 1

    # Cache de Noticias
    last_news_fetch = 0
    NEWS_FETCH_INTERVAL = 6 * 3600 # 6 horas
    headlines = []
    sig_fund = "NEUTRAL"

    while True:
        try:
            print(f"\n{'#'*70}")
            print(f"🔄 ESCANEO SCALPING: {datetime.now().strftime('%H:%M:%S')} | BALANCE: ${balance_actual:.2f}")
            print(f"{'#'*70}")
            
            # 1. Datos
            df_macro, df_micro = get_wti_mtf_data()
            if df_macro is None or df_micro is None:
                time.sleep(10); continue

            # 2. Indicadores (usamos los mismos para no romper la estructura, pero la estrategia usa pocos)
            df_micro['SMA_50'] = calculate_sma(df_micro, 50)
            df_micro['RSI'] = calculate_rsi(df_micro, 14)
            df_micro['ATR'] = calculate_atr(df_micro, 14)
            df_micro['ADX'] = calculate_adx(df_micro, 14)
            df_micro['Dynamic_Support'] = calculate_dynamic_support(df_micro, 20)
            df_micro['Dynamic_Resistance'] = calculate_dynamic_resistance(df_micro, 20)

            # 3. Noticias (Cada 6h)
            current_time = time.time()
            if current_time - last_news_fetch >= NEWS_FETCH_INTERVAL:
                print("\n📰 ACTUALIZANDO NOTICIAS (Geopolítica/Oil)...")
                news_client = NewsClient(os.getenv("NEWS_API_KEY"))
                headlines = news_client.get_headlines(limit=30)
                sig_fund = analyze_market_sentiment(headlines)
                last_news_fetch = current_time
            else:
                print(f"\n📰 SENTIMIENTO CACHEADO: {sig_fund}")

            # 4. Auditoría de Niveles Rápidos
            last = df_micro.iloc[-1]
            prev = df_micro.iloc[-2]
            print(f"📊 PRECIO ACTUAL: ${last['Close']:.2f} | RSI: {last['RSI']:.1f} | ATR (Volatilidad): {last['ATR']:.2f}")
            print(f"📏 VELA ANTERIOR: Max ${prev['High']:.2f} - Min ${prev['Low']:.2f}")

            # 5. Estrategia de Scalping
            strat = ScalperWTI(df_micro, sig_fund)
            sig_tech, entry, tp, sl = strat.evaluate()
            
            print(f"⚖️  SEÑAL SCALPER: {sig_tech}")

            # 5.1 Registro de Bitácora (Análisis Continuo)
            # Adaptamos los campos para que encajen en el CSV existente
            thought_ledger.registrar_analisis({
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Precio': round(last['Close'], 2),
                'ADX': round(last['ADX'], 1),
                'RSI': round(last['RSI'], 1),
                'SMA200_Trend': "SCALP", # Indicativo de que es el bot scalper
                'SMA50_Rel': "ABOVE" if last['Close'] > last['SMA_50'] else "BELOW",
                'Soporte': round(prev['Low'], 2), # En scalping vigilamos la vela previa
                'Resistencia': round(prev['High'], 2),
                'Sentimiento': sig_fund,
                'Decision': sig_tech
            })

            # 6. Ejecución
            if not operacion_abierta:
                if "SCALP" in sig_tech:
                    distancia_sl = abs(entry - sl)
                    if distancia_sl == 0: distancia_sl = 0.05
                    # En scalping podríamos usar lotes más altos porque el SL es muy corto, 
                    # pero mantenemos el riesgo fijo del 1% del balance para no quemar la cuenta.
                    riesgo_usd = balance_actual * RIESGO_POR_TRADE
                    lotes = riesgo_usd / distancia_sl
                    
                    operacion_abierta = True
                    datos_trade = {
                        'Ticket_ID': ticket_id, 'Fecha_Entrada': datetime.now(),
                        'Tipo': sig_tech, 'Precio_Entrada': entry, 'TP': tp, 'SL': sl,
                        'Lotes': lotes, 'Contexto_Noticias': sig_fund
                    }
                    ticket_id += 1
                    logger.warning(f"⚡ MICRO-ORDEN EJECUTADA: {sig_tech} | TP: {tp:.2f} | SL: {sl:.2f}")
                else:
                    print("   ⏳ Esperando micro-rompimiento de momentum...")
            else:
                # Monitoreo muy estricto
                print(f"🚀 POSICIÓN ACTIVA: {datos_trade['Tipo']} | Ent: {datos_trade['Precio_Entrada']:.2f} | TP: {datos_trade['TP']:.2f} | SL: {datos_trade['SL']:.2f}")
                candle = last
                hit_tp = False; hit_sl = False
                tipo = datos_trade['Tipo']
                
                # Evaluación de salida (ganar poco / perder poco)
                if "CALL" in tipo:
                    if candle['High'] >= datos_trade['TP']: hit_tp = True
                    elif candle['Low'] <= datos_trade['SL']: hit_sl = True
                elif "PUT" in tipo:
                    if candle['Low'] <= datos_trade['TP']: hit_tp = True
                    elif candle['High'] >= datos_trade['SL']: hit_sl = True

                if hit_tp or hit_sl:
                    precio_salida = datos_trade['TP'] if hit_tp else datos_trade['SL']
                    pnl_usd = (precio_salida - datos_trade['Precio_Entrada']) * datos_trade['Lotes']
                    if "PUT" in tipo: pnl_usd *= -1
                    balance_actual += pnl_usd
                    
                    trade_ledger.registrar_trade_cerrado({
                        'Ticket_ID': datos_trade['Ticket_ID'], 'Fecha_Entrada': datos_trade['Fecha_Entrada'],
                        'Tipo': tipo, 'Precio_Entrada': round(datos_trade['Precio_Entrada'], 2),
                        'Fecha_Salida': datetime.now(), 'Precio_Salida': round(precio_salida, 2),
                        'Resultado_USD': round(pnl_usd, 2), 'Balance_Final': round(balance_actual, 2),
                        'Razon_Salida': "MICRO_TP" if hit_tp else "MICRO_SL", 'Contexto_Noticias': datos_trade['Contexto_Noticias']
                    })
                    logger.warning(f"💰 RESULTADO SCALP: {'🟢' if pnl_usd > 0 else '🔴'} ${pnl_usd:.2f}")
                    operacion_abierta = False

            # Bucle más rápido para scalping (30 segundos en lugar de 60)
            time.sleep(30)
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_scalper_monitor()
