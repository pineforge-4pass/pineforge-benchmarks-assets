"""@pyne
Hand-port of strategies/07-scalping-strategy/strategy.pine for PyneCore.

Pine source: "Scalping Strategy Improved v2"
  - 50/200 EMA trend filter
  - 3-period RSI mean-reversion trigger
  - DMI/ADX trend strength
  - ATR-sized stop + 2:1 take-profit + ATR trailing stop
"""
from pynecore.lib import script, input, ta, math, strategy, close, open, high, low


@script.strategy("Scalping Strategy Improved v2", overlay=True)
def main(
    ema_fast: int = input.int(50),
    ema_slow: int = input.int(200),
    rsi_len: int = input.int(3),
    rsi_ob: int = input.int(80),
    rsi_os: int = input.int(20),
    adx_len: int = input.int(5),
    adx_level: int = input.int(20),
    atr_len: int = input.int(14),
    atr_mult: float = input.float(1.2),
):
    ema50 = ta.ema(close, ema_fast)
    ema200 = ta.ema(close, ema_slow)
    rsi = ta.rsi(close, rsi_len)
    _diplus, _diminus, adx = ta.dmi(adx_len, adx_len)
    atr = ta.atr(atr_len)

    body = math.abs(close - open)
    candle_range = high - low
    strong_bull = close > open and body > candle_range * 0.5
    strong_bear = close < open and body > candle_range * 0.5

    trend_long = close > ema50 and ema50 > ema200
    trend_short = close < ema50 and ema50 < ema200

    rsi_long = ta.crossover(rsi, rsi_os)
    rsi_short = ta.crossunder(rsi, rsi_ob)

    trend_strength = adx > adx_level

    long_cond = trend_long and rsi_long and trend_strength and strong_bull
    short_cond = trend_short and rsi_short and trend_strength and strong_bear

    long_stop = close - atr * atr_mult
    short_stop = close + atr * atr_mult
    long_tp = close + (close - long_stop) * 2
    short_tp = close - (short_stop - close) * 2

    if long_cond:
        strategy.entry("BUY", strategy.long)
        strategy.exit("TP/SL BUY", "BUY", stop=long_stop, limit=long_tp, trail_points=atr)

    if short_cond:
        strategy.entry("SELL", strategy.short)
        strategy.exit("TP/SL SELL", "SELL", stop=short_stop, limit=short_tp, trail_points=atr)
