# 🪙 Crypto Trading Bots (Bitcoin Futures)

Este repositorio contiene tres sistemas algorítmicos distintos diseñados para operar Futuros de Bitcoin (BTCUSDT). Cada bot tiene su propia filosofía, gestión de riesgo y arquitectura tecnológica, adaptándose a diferentes perfiles de trading (desde macro hasta alta frecuencia institucional).

---

## 🐋 1. Bot Principal (Cazador de Ballenas Macro)
- **Archivo a ejecutar:** `main.py`
- **Enfoque:** Top-Down (Análisis Técnico Macro + Análisis On-Chain + Sentimiento de Noticias).
- **Fuente de Datos:** Binance REST API (Velas de 1m, 15m, 1h, 1d) y Mempool.space.
- **Apalancamiento Recomendado:** 50x

### ¿Cómo opera?
Este es un bot de swing/intradía que busca **confluencias fuertes**. Solo disparará una operación cuando múltiples factores se alineen:
1.  **Zona de Interés (15m/1h):** El precio en el gráfico de 1 minuto debe estar tocando exactamente una zona de soporte o resistencia calculada en el gráfico de 15 minutos (tolerancia del 0.5%).
2.  **Confirmación de Tendencia:** El RSI no debe estar en su contra y la tendencia macro (SMA 50 > SMA 200) debe estar a favor del rebote.
3.  **El Gatillo On-Chain:** Si hay un rebote técnico, la confianza es del 80%. Pero si en ese exacto instante el bot detecta vía Mempool que una ballena movió grandes cantidades de BTC en una dirección que favorece el trade, la confianza sube al 95% y entra al mercado.

---

## ⚡ 2. Bot Scalper Técnico (Alta Frecuencia Básica)
- **Archivo a ejecutar:** `main_scalper.py`
- **Enfoque:** Acción del Precio Pura (Micro-Breakouts).
- **Fuente de Datos:** Yahoo Finance (yfinance).
- **Apalancamiento:** 50x

### ¿Cómo opera?
Este bot ignora por completo las noticias y a las ballenas. Está ciego a todo lo que no sea el precio y los indicadores matemáticos de cortísimo plazo (vela a vela).
1.  **Tendencia:** Lee las SMA 50 y SMA 200 en el gráfico de 1 minuto.
2.  **Filtro:** Usa el RSI para asegurarse de no comprar en sobrecompra ni vender en sobreventa.
3.  **Gatillo:** Entra al mercado **rompiendo la vela anterior**. Si la vela actual rompe el máximo de la vela anterior y la tendencia es alcista, abre un LONG.
4.  **Gestión de Riesgo Dinámica:** Como opera en 50x, su Stop Loss es súper ajustado (0.5 * ATR) y su Take Profit es rápido (0.8 * ATR), adaptándose a la volatilidad viva.

---

## 🏛️ 3. Pro SMC Scalper (Institucional AsyncIO)
- **Archivo a ejecutar:** `main_pro.py`
- **Enfoque:** Smart Money Concepts (SMC) + Order Flow + Latencia Cero.
- **Fuente de Datos:** Binance WebSockets (Stream en tiempo real) y REST (Open Interest, Funding Rate).
- **Apalancamiento Recomendado:** 20x

### ¿Cómo opera?
Esta es la obra maestra del proyecto. Construido sobre Python Asíncrono (`asyncio`), este bot no "despierta" cada minuto, sino que "escucha" el mercado en tiempo real, milisegundo a milisegundo, viendo el Order Book de Binance.
1.  **Filtro Anti-Lateralidad:** Usando las Bandas de Bollinger, si el mercado está plano/muerto (compresión del <0.2%), el bot entra en modo `CHOPPY` y se bloquea por seguridad.
2.  **Tendencia (5m):** Establece el sesgo institucional cruzando EMAs en 5 minutos.
3.  **Barridos de Liquidez (Liquidity Sweeps):** No persigue el precio. Espera a que el mercado haga un *falso rompimiento* (rompa un mínimo para estafar a los retailers y liquidarlos) pero que cierre rebotando violentamente por encima del **VWAP** (precio institucional).
4.  **Order Flow:** El bot revisa el *Funding Rate* y el *Open Interest*. Si todo el mercado está yendo en LONG (Funding hiper positivo), el bot aborta operaciones de compra porque huele que el exchange buscará liquidarlos hacia abajo (Long Squeeze).
5.  **Ejecución Rápida:** Sus cálculos se ejecutan en microsegundos usando DataFrames basados en memoria RAM (Deque), sin escribir a disco hasta que se cierra la operación.

---

## 🛠️ Requisitos e Instalación
Para el bot Pro (AsyncIO) necesitas instalar las dependencias asíncronas:
```bash
pip install aiohttp websockets pandas textblob yfinance requests python-dotenv numpy
```

## 📊 Sistema de Notificaciones y Bitácora
Todos los bots enviarán notificaciones de entrada/salida a tu **Discord** y a **WhatsApp** a través de la Evolution API de manera autónoma (si están configurados en el `.env`). Además, todas las operaciones de papel (Paper Trading) se auditan en los archivos `logs/operaciones_backtest.csv` para análisis de rentabilidad.
