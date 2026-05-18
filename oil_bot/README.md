# 🛢️ WTI Turbo Trading Bot v1.5 (Turbo 1min)

Este bot es un sistema de trading algorítmico cuantitativo diseñado para operar futuros de Petróleo Crudo (WTI) utilizando un enfoque de **Análisis de Múltiples Marcos Temporales** (Top-Down) y **Sentimiento Fundamental Ponderado**.

## 🚀 Parámetros de Operación (1 Minuto)

El bot está programado para ser un "francotirador". Solo operará cuando todas las capas de análisis estén alineadas. Aquí están las condiciones exactas que busca:

### 1. Filtro Maestro (Marea del Mercado)
- **Marco Temporal**: Diario (1D).
- **Indicador**: Media Móvil Simple (SMA) de 200 periodos.
- **Regla**: 
  - Solo permite **COMPRAS** si el precio diario > SMA 200.
  - Solo permite **VENTAS** si el precio diario < SMA 200.

### 2. Filtro de Fuerza y Volatilidad
- **ADX (14)**: Debe ser **> 26**. Esto asegura que el mercado no esté "muerto" o lateral.
- **RSI (14)**: 
  - Para COMPRA: Entre **50 y 70** (Fuerza sin sobrecompra).
  - Para VENTA: Entre **30 y 50** (Debilidad sin sobreventa).

### 3. Disparador Técnico (Ruptura de 1 Minuto)
- **Ruptura de Canal**: El precio debe romper el máximo (Resistencia) o mínimo (Soporte) de las últimas **20 velas** de 1 minuto.
- **Confirmación SMA**: El precio debe estar por encima (Compra) o debajo (Venta) de la **SMA 50** de corto plazo.

### 4. Alineación Fundamental (Sentimiento Ponderado)
- **Fuente**: 50 titulares de NewsData.io.
- **Lógica**: Se analiza la polaridad de las noticias pero con **pesos industriales**:
  - Palabras como *War, Cut, Shortage* dan puntos **ALCISTAS**.
  - Palabras como *Surplus, Glut, Inventory Rise* dan puntos **BAJISTAS**.
- **Umbral**: Solo opera si el puntaje promedio es **> 0.05 (Alcista)** o **< -0.05 (Bajista)**.

### 5. Gestión de Riesgo (ATR Dinámico)
- **Salida**: No usa puntos fijos. Usa el **ATR (Average True Range)**.
- **Take Profit / Stop Loss**: Se colocan a **1.5 * ATR**. Esto significa que si el mercado está muy volátil, el Stop es más ancho; si está tranquilo, es más ajustado.

---

## 🛠️ Cómo leer el Log de Consola
- **"Técnica: ESPERAR"**: Al menos una de las condiciones de ADX, RSI o Ruptura no se ha cumplido.
- **"Técnica: COMPRA | Fundamental: NEUTRAL"**: El gráfico dice "adelante" pero las noticias no confirman. El bot **NO operará**.
- **"🔥 ¡ORDEN EJECUTADA!"**: Todas las condiciones anteriores se cumplieron simultáneamente.

## 📁 Archivos del Proyecto
- `core/`: Clientes de datos (Yahoo Finance) y noticias.
- `strategies/`: Lógica matemática de la estrategia Breakout.
- `utils/`: Indicadores técnicos puros y sistema de registro (Ledger).
- `operaciones_backtest.csv`: Tu bitácora de guerra con todos los resultados.
