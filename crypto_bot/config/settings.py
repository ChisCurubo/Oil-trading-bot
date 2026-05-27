# Settings for Pro SMC Scalper

SYMBOL = "BTCUSDT"
LEVERAGE = 20

# Risk Management
RISK_PER_TRADE = 0.01  # 1% del balance
INITIAL_BALANCE = 1000.0  # Balance inicial para Paper Trading

# SMC Parameters
EMA_FAST = 20
EMA_SLOW = 50
RSI_PERIOD = 14
ATR_PERIOD = 14

# Scalping Limits
MAX_SL_PERCENT = 0.005 # 0.5% max real move (10% a 20x leverage)
TP_REWARD_RATIO = 2.0  # Riesgo:Beneficio 1:2
