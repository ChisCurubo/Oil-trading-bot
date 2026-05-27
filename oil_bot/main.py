import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Importaciones locales
from core.data_client import get_wti_mtf_data
from core.news_client import NewsClient
from fundamentals.sentiment import analyze_market_sentiment
from strategies.breakout_wti import BreakoutWTI
from utils.indicators import *
from utils.trade_logger import TradeLogger
from utils.thought_logger import ThoughtLogger
from utils.logger import setup_logger

# Configuración inicial
load_dotenv("config/.env")
logger = setup_logger("OilBot_Master")

# --- PARÁMETROS FINANCIEROS ---
CAPITAL_INICIAL = 10000.0
RIESGO_POR_TRADE = 0.01  # 1% del capital

def run_live_monitor():
    """
    Panel de Control Maestro: Visibilidad Total + Gestión de Capital.
    """
    logger.info("="*70)
    logger.info("🛡️  SISTEMA MAESTRO WTI - CONTROL TOTAL ACTIVADO")
    logger.info(f"💰 CAPITAL SEMILLA: ${CAPITAL_INICIAL} USD")
    logger.info("="*70)
    
    trade_ledger = TradeLogger()
    thought_ledger = ThoughtLogger()
    
    balance_actual = CAPITAL_INICIAL
    operacion_abierta = False
    datos_trade = {}
    ticket_id = 1
    
    # Cache de Noticias
    last_news_fetch = 0
    NEWS_FETCH_INTERVAL = 6 * 3600  # 6 horas en segundos
    headlines = []
    sig_fund = "NEUTRAL"

    while True:
        try:
            print(f"\n{'#'*70}")
            print(f"🔄 ESCANEO ACTIVO: {datetime.now().strftime('%H:%M:%S')} | BALANCE: ${balance_actual:.2f}")
            print(f"{'#'*70}")
            
            # 1. Obtención de Datos
            df_macro, df_micro = get_wti_mtf_data()
            if df_macro is None or df_micro is None or len(df_macro) < 2 or len(df_micro) < 2:
                print("⏳ Esperando datos suficientes del mercado...")
                time.sleep(10); continue

            # 2. Cálculos Técnicos
            df_macro['SMA_200'] = calculate_sma(df_macro, 200)
            df_micro['SMA_50'] = calculate_sma(df_micro, 50)
            df_micro['RSI'] = calculate_rsi(df_micro, 14)
            df_micro['ATR'] = calculate_atr(df_micro, 14)
            df_micro['ADX'] = calculate_adx(df_micro, 14)
            df_micro['Dynamic_Support'] = calculate_dynamic_support(df_micro, 20)
            df_micro['Dynamic_Resistance'] = calculate_dynamic_resistance(df_micro, 20)

            # 3. Auditoría de Noticias (Optimizado: cada 6 horas)
            current_time = time.time()
            if current_time - last_news_fetch >= NEWS_FETCH_INTERVAL:
                print("\n📰 [ACTUALIZANDO FLUJO DE NOTICIAS...]")
                news_client = NewsClient(os.getenv("NEWS_API_KEY"))
                headlines = news_client.get_headlines(limit=50)
                sig_fund = analyze_market_sentiment(headlines)
                last_news_fetch = current_time
            else:
                minutos_restantes = (last_news_fetch + NEWS_FETCH_INTERVAL - current_time) / 60
                print(f"\n📰 [NOTICIAS CACHEADAS] (Próxima actualización en {minutos_restantes:.1f} min)")
            
            if headlines:
                for i, h in enumerate(headlines[:15]): # Mostrar 15 principales
                    print(f"   - {h[:90]}...")
            print(f"🔎 SENTIMIENTO PONDERADO: {sig_fund}")

            # 4. Auditoría Técnica
            last_micro = df_micro.iloc[-1]
            last_macro = df_macro.iloc[-1]
            macro_trend = "BULL" if last_micro['Close'] > last_macro['SMA_200'] else "BEAR"
            
            print("\n📊 [INDICADORES TÉCNICOS]")
            print(f"   • PRECIO WTI:     ${last_micro['Close']:.2f}")
            print(f"   • TENDENCIA (1D): {macro_trend} (SMA 200: {last_macro['SMA_200']:.2f})")
            print(f"   • MOMENTUM (1H):  ADX: {last_micro['ADX']:.1f} | RSI: {last_micro['RSI']:.1f}")
            print(f"   • CANAL PRECIOS:  SUP: {last_micro['Dynamic_Resistance']:.2f} | INF: {last_micro['Dynamic_Support']:.2f}")
            print(f"   • VOLATILIDAD:    ATR: {last_micro['ATR']:.2f}")

            # 5. Evaluación de Estrategia
            strat = BreakoutWTI(df_micro, df_macro)
            sig_tech, entry, tp, sl = strat.evaluate()
            
            print(f"\n⚖️  ESTADO ESTRATEGIA: {sig_tech}")

            # 6. Registro de Bitácora (Análisis Continuo)
            thought_ledger.registrar_analisis({
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Precio': round(last_micro['Close'], 2),
                'ADX': round(last_micro['ADX'], 1),
                'RSI': round(last_micro['RSI'], 1),
                'SMA200_Trend': macro_trend,
                'SMA50_Rel': "ABOVE" if last_micro['Close'] > last_micro['SMA_50'] else "BELOW",
                'Soporte': round(last_micro['Dynamic_Support'], 2),
                'Resistencia': round(last_micro['Dynamic_Resistance'], 2),
                'Sentimiento': sig_fund,
                'Decision': sig_tech
            })

            # 7. Lógica de Ejecución y Monitoreo
            if not operacion_abierta:
                if (sig_tech == "VENTA" and sig_fund == "BAJISTA") or \
                   (sig_tech == "COMPRA" and sig_fund == "ALCISTA"):
                    
                    # Gestión de Riesgo Dinámica
                    distancia_sl = abs(entry - sl)
                    if distancia_sl == 0: distancia_sl = 0.1
                    riesgo_usd = balance_actual * RIESGO_POR_TRADE
                    lotes = riesgo_usd / distancia_sl
                    
                    operacion_abierta = True
                    datos_trade = {
                        'Ticket_ID': ticket_id, 'Fecha_Entrada': datetime.now(),
                        'Tipo': sig_tech, 'Precio_Entrada': entry, 'TP': tp, 'SL': sl,
                        'Lotes': lotes, 'Contexto_Noticias': sig_fund
                    }
                    ticket_id += 1
                    logger.warning(f"🔥 ¡ORDEN EJECUTADA! {sig_tech} | Lotes: {lotes:.2f} | Riesgo: ${riesgo_usd:.2f}")
                else:
                    if sig_tech != "ESPERAR":
                        print("   🛑 BLOQUEADO: La técnica indica entrada pero el sentimiento no acompaña.")
                    else:
                        print("   ⏳ Buscando alineación de factores técnicos...")
            else:
                print(f"🚀 POSICIÓN ACTIVA: {datos_trade['Tipo']} | Ent: {datos_trade['Precio_Entrada']:.2f} | TP: {datos_trade['TP']:.2f} | SL: {datos_trade['SL']:.2f}")
                # Monitoreo de salida
                candle = last_micro
                hit_tp = False; hit_sl = False
                tipo = datos_trade['Tipo']
                if tipo == "COMPRA":
                    if candle['Close'] >= datos_trade['TP']: hit_tp = True
                    elif candle['Close'] <= datos_trade['SL']: hit_sl = True
                elif tipo == "VENTA":
                    if candle['Close'] <= datos_trade['TP']: hit_tp = True
                    elif candle['Close'] >= datos_trade['SL']: hit_sl = True

                if hit_tp or hit_sl:
                    precio_salida = datos_trade['TP'] if hit_tp else datos_trade['SL']
                    razon = "TAKE_PROFIT" if hit_tp else "STOP_LOSS"
                    pnl_usd = (precio_salida - datos_trade['Precio_Entrada']) * datos_trade['Lotes']
                    if tipo == "VENTA": pnl_usd *= -1
                    balance_actual += pnl_usd
                    
                    trade_ledger.registrar_trade_cerrado({
                        'Ticket_ID': datos_trade['Ticket_ID'], 'Fecha_Entrada': datos_trade['Fecha_Entrada'],
                        'Tipo': tipo, 'Precio_Entrada': round(datos_trade['Precio_Entrada'], 2),
                        'Fecha_Salida': datetime.now(), 'Precio_Salida': round(precio_salida, 2),
                        'Resultado_USD': round(pnl_usd, 2), 'Balance_Final': round(balance_actual, 2),
                        'Razon_Salida': razon, 'Contexto_Noticias': datos_trade['Contexto_Noticias']
                    })
                    
                    emoji = "🟢" if pnl_usd > 0 else "🔴"
                    logger.warning(f"{emoji} TRADE CERRADO: {razon} | PnL: ${pnl_usd:.2f} | Balance: ${balance_actual:.2f}")
                    operacion_abierta = False

            print(f"\n{'-'*70}\nCiclo completado. Analizando bitácora...")
            time.sleep(60)

        except Exception as e:
            logger.error(f"❌ Error en el loop maestro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_live_monitor()