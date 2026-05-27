import asyncio
import time
from datetime import datetime

from config import settings
from core.ws_client import BinanceWSClient
from core.rest_client import BinanceRestClient
from core.alerts import AsyncAlertClient
from data.market_state import MarketState
from strategies.smc_logic import SMCLogic
from strategies.risk_manager import RiskManager
from utils.advanced_indicators import add_all_indicators
from utils.loggers import setup_logger, ProLogger

logger = setup_logger("ProScalper")

async def engine_loop(market_state, rest_client, ws_client, alerts_client):
    """Bucle del motor de decisión"""
    
    pro_logger = ProLogger()
    smc = SMCLogic()
    risk_mgr = RiskManager()
    
    # State variables
    operacion_abierta = False
    datos_trade = {}
    ticket_id = 5000
    balance_usd = settings.INITIAL_BALANCE
    last_analysis_time = 0
    last_hourly_alert = 0
    HOURLY_ALERT_INTERVAL = 3600
    
    await asyncio.sleep(5) # Dar tiempo al WebSocket a poblar algunos datos
    
    while True:
        try:
            current_time = time.time()
            
            # Solo corremos la lógica profunda cada ~10 segundos (o cuando cambie la vela) para no sobrecargar el CPU
            # Pero la salida de la orden se revisa constantemente
            
            df_1m = market_state.get_df("1m")
            df_5m = market_state.get_df("5m")
            
            if len(df_1m) > 50 and len(df_5m) > 50:
                
                # Exit logic evaluada a la velocidad de la luz (tick-level)
                if operacion_abierta:
                    hit_tp = False; hit_sl = False
                    current_price = market_state.last_price
                    
                    if datos_trade['Tipo'] == "BUY":
                        if current_price >= datos_trade['TP']: hit_tp = True
                        elif current_price <= datos_trade['SL']: hit_sl = True
                    elif datos_trade['Tipo'] == "SELL":
                        if current_price <= datos_trade['TP']: hit_tp = True
                        elif current_price >= datos_trade['SL']: hit_sl = True
                        
                    if hit_tp or hit_sl:
                        exit_price = current_price
                        razon = "TAKE_PROFIT" if hit_tp else "STOP_LOSS"
                        
                        pnl_usd = risk_mgr.calculate_pnl(datos_trade['Tipo'], datos_trade['Entry_Price'], exit_price, balance_usd)
                        balance_usd += pnl_usd
                        
                        pro_logger.log_trade({
                            'Trade_ID': datos_trade['Ticket_ID'],
                            'Time_Entry': datos_trade['Time_Entry'],
                            'Type': datos_trade['Tipo'],
                            'Entry_Price': round(datos_trade['Entry_Price'], 2),
                            'Leverage': f"{settings.LEVERAGE}x",
                            'Time_Exit': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Exit_Price': round(exit_price, 2),
                            'PNL_USD': round(pnl_usd, 2),
                            'Balance': round(balance_usd, 2),
                            'Reason_Exit': razon,
                            'Confidence': datos_trade['Confidence']
                        })
                        
                        msg = (f"✅ ALERTA CIERRE PRO SCALPER ✅\n\n"
                               f"Operación: {datos_trade['Tipo']} CERRADA\n"
                               f"Razón: {razon}\n"
                               f"PNL: {'🟢' if pnl_usd > 0 else '🔴'} ${pnl_usd:.2f}\n"
                               f"Balance Nuevo: ${balance_usd:.2f}")
                               
                        await alerts_client.broadcast(msg)
                        logger.warning(f"💰 OPERACION CERRADA: {razon} | PNL: ${pnl_usd:.2f} | Bal: ${balance_usd:.2f}")
                        operacion_abierta = False

                # Analysis logic evaluada cada 10s
                if current_time - last_analysis_time >= 10:
                    df_1m = add_all_indicators(df_1m)
                    df_5m = add_all_indicators(df_5m)
                    
                    structure_5m = smc.detect_market_structure(df_5m)
                    signal, conf, reason = smc.evaluate_1m(df_1m, structure_5m, market_state)
                    
                    last_1m = df_1m.iloc[-1]
                    current_price = last_1m['c']
                    
                    print(f"\r📊 [BAL: ${balance_usd:.2f}] Precio: {current_price:.2f} | Tendencia(5m): {structure_5m} | Signal: {signal}", end="")
                    
                    pro_logger.log_analysis({
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Symbol': settings.SYMBOL,
                        'Price_1m': round(current_price, 2),
                        'EMA20': round(last_1m.get('EMA_20', 0), 2),
                        'EMA50': round(last_1m.get('EMA_50', 0), 2),
                        'VWAP': round(last_1m.get('VWAP', 0), 2),
                        'RSI': round(last_1m.get('RSI', 50), 2),
                        'FundingRate': market_state.funding_rate,
                        'Structure': structure_5m,
                        'Signal': signal,
                        'Confidence': conf,
                        'Reason': reason
                    })
                    
                    if current_time - last_hourly_alert >= HOURLY_ALERT_INTERVAL:
                        hourly_msg = (f"⏱️ REPORTE HORARIO PRO SMC ⏱️\n\n"
                                      f"💰 Precio BTC: ${current_price:.2f}\n"
                                      f"📈 Tendencia SMC (5m): {structure_5m}\n"
                                      f"🌡️ RSI (1m): {last_1m.get('RSI', 50):.1f}\n"
                                      f"⚖️ Funding Rate: {market_state.funding_rate:.5f}\n"
                                      f"🐳 Open Interest: {market_state.open_interest:.2f}")
                        await alerts_client.broadcast(hourly_msg)
                        last_hourly_alert = current_time
                    
                    if not operacion_abierta and signal in ["BUY", "SELL"]:
                        tp, sl = risk_mgr.calculate_trade_parameters(signal, current_price, last_1m.get('ATR', current_price*0.001))
                        
                        msg = (f"🚨 ALERTA PRO SMC SCALPER 🚨\n\n"
                               f"Señal: {'🟢 BUY' if signal == 'BUY' else '🔴 SELL'}\n"
                               f"Confianza: {conf}%\n"
                               f"Motivo: {reason}\n"
                               f"Apalancamiento: {settings.LEVERAGE}x\n"
                               f"Entrada: ${current_price:.2f}\n"
                               f"Take Profit: ${tp:.2f}\n"
                               f"Stop Loss: ${sl:.2f}\n"
                               f"Riesgo: {settings.RISK_PER_TRADE*100}% del Balance")
                               
                        await alerts_client.broadcast(msg)
                        
                        operacion_abierta = True
                        datos_trade = {
                            'Ticket_ID': ticket_id,
                            'Time_Entry': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Tipo': signal,
                            'Entry_Price': current_price,
                            'TP': tp,
                            'SL': sl,
                            'Confidence': conf
                        }
                        ticket_id += 1
                        print("")
                        logger.warning(f"🚀 SMC OPERACION ABIERTA: {signal} a {current_price:.2f} | TP: {tp:.2f} | SL: {sl:.2f}")
                        
                    last_analysis_time = current_time

            # Dormir cortísimo para permitir que el WebSocket meta datos en el state
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ Error crítico en motor AsyncIO: {e}")
            await asyncio.sleep(5)

async def main():
    logger.info("="*70)
    logger.info("⚡ PRO SMC SCALPER INICIANDO (ASYNCIO) ⚡")
    logger.info("="*70)
    
    market_state = MarketState()
    rest_client = BinanceRestClient()
    ws_client = BinanceWSClient(market_state, settings.SYMBOL)
    alerts_client = AsyncAlertClient()
    
    print("⏳ Descargando contexto histórico (REST API)...")
    klines_1m = await rest_client.get_historical_klines(settings.SYMBOL, "1m", 250)
    klines_5m = await rest_client.get_historical_klines(settings.SYMBOL, "5m", 250)
    
    market_state.init_historical_klines("1m", klines_1m)
    market_state.init_historical_klines("5m", klines_5m)
    
    market_state.funding_rate = await rest_client.get_funding_rate(settings.SYMBOL)
    market_state.open_interest = await rest_client.get_open_interest(settings.SYMBOL)
    
    print("🚀 Contexto descargado. Lanzando tareas asíncronas...")
    
    # Arrancar WebSocket y Motor en paralelo
    await asyncio.gather(
        ws_client.connect_and_listen(),
        engine_loop(market_state, rest_client, ws_client, alerts_client)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot detenido manualmente.")
