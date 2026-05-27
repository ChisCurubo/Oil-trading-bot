# 🛢️ WTI Turbo Trading Bot (Oil Futures)

Este repositorio contiene tres sistemas de trading algorítmico diseñados exclusivamente para operar futuros de Petróleo Crudo (WTI). Dado que el mercado de commodities tiene comportamientos particulares ligados a la macroeconomía y la geopolítica, los bots integran fuerte análisis fundamental (News Sentiment) junto a la lectura matemática del precio.

---

## 🌎 1. Bot de Tendencia Macro (News & Trend)
- **Archivo a ejecutar:** `main.py`
- **Enfoque:** Top-Down (Filtros Diarios + Rupturas Intradía + Sentimiento Geopolítico).
- **Frecuencia:** Swing / Day Trading lento (Chequeo constante, pocas entradas).

### ¿Cómo opera?
El bot está programado para ser un "francotirador" conservador. Solo operará cuando todas las capas de análisis macroeconómico y técnico estén alineadas:
1. **La Marea Diaria (1D):** Solo permite COMPRAS si el precio diario está sobre la SMA 200, y VENTAS si está debajo. Nunca opera contra la tendencia anual.
2. **Fuerza del Movimiento (ADX):** El indicador ADX(14) debe ser `> 26`, asegurando que el mercado tiene volumen y no está lateral.
3. **Sentimiento Geopolítico:** Lee 50 titulares de noticias usando NewsData.io. Filtra palabras clave de la industria (ej. *War, Shortage* suman puntos alcistas, *Surplus, Glut* suman puntos bajistas). **Solo opera si el sentimiento acompaña al análisis técnico.**
4. **Disparador:** Si las 3 condiciones se cumplen, el bot espera a que el precio en 1 minuto rompa el máximo (o mínimo) de las últimas 20 velas.

---

## ⏱️ 2. Bot de Monitoreo Constante (Range Trader)
- **Archivo a ejecutar:** `main_constante.py`
- **Enfoque:** Reversiones a la Media (Operando el Rango).
- **Frecuencia:** Media.

### ¿Cómo opera?
A diferencia del bot macro que busca grandes tendencias, el `main_constante.py` asume que la mayor parte del tiempo el mercado petrolero se mueve en rangos consolidados. 
1. Usa el **RSI** de 1 minuto para buscar extremos (Sobrecompra `> 70` o Sobreventa `< 30`).
2. Verifica Soportes y Resistencias dinámicas de las últimas velas.
3. Si el precio toca el techo de un rango y el RSI está alto, el bot asume que el precio rebotará hacia el centro y dispara un **SHORT**. Si toca el piso y el RSI está bajo, dispara un **LONG**.

---

## ⚡ 3. WTI Scalper
- **Archivo a ejecutar:** `main_scalper.py`
- **Enfoque:** Alta Frecuencia / Momentum.
- **Frecuencia:** Alta.

### ¿Cómo opera?
Un bot diseñado para estar en y fuera del mercado en cuestión de minutos, ideal para sesiones de alto volumen (Apertura NY).
1. Ignora la tendencia de largo plazo. Solo le importa la **SMA 50** del gráfico de 1 minuto.
2. Analiza la **Vela Anterior:** Si el precio actual supera el máximo de la vela anterior (micro-breakout) estando sobre la SMA 50, dispara la orden inmediata.
3. **Gestión de Riesgo Agresiva:** Utiliza multiplicadores del **ATR (Average True Range)** para fijar límites de pérdida (`0.5x ATR`) y límites de ganancia (`1.0x ATR`). De esta manera, sin importar si el mercado está muy errático o muy tranquilo, el bot asegura matemáticamente un ratio donde sus ganancias superan a sus pérdidas basándose en la volatilidad instantánea.

---

## 🛠️ Archivos del Proyecto
- `core/`: Clientes de datos (Yahoo Finance y NewsData.io).
- `strategies/`: La lógica matemática de cada estilo (Breakout, Rango, Scalping).
- `utils/`: Indicadores técnicos puros (SMA, ADX, ATR, RSI) y el sistema de registro.
- `operaciones_backtest.csv`: El libro contable donde se guardan las simulaciones de Paper Trading.
- `bitacora_analisis.csv`: Un log exhaustivo con todas las decisiones tomadas minuto a minuto por los motores.
