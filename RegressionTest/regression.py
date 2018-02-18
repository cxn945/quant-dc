from klines_loader import load_kline
from strategy_sma import run_strategy

# load data
load_kline(period=15, symbol="iostusdt")

# run strategy
run_strategy()