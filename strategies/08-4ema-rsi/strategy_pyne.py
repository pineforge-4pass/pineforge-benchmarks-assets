"""@pyne
Hand-port of strategies/08-4ema-rsi/strategy.pine for PyneCore.

Pine source: "4-EMA & RSI Trend Pullback [Binary Options_20260320]"
  - 7/21 EMA cross with 50/200 EMA macro trend filter
  - RSI in centered momentum band (50 < RSI < OB for longs, OS < RSI < 50 for shorts)
  - Exit on opposite EMA cross or break of 50 EMA

The original calls `alert()` for each entry/exit; PyneCore's @pyne runtime
silently ignores `alert()` so the trade list is unaffected.
"""
from pynecore.lib import script, input, ta, strategy, close


@script.strategy("4-EMA & RSI Trend Pullback [Binary Options_20260320]", overlay=True)
def main(
    len7: int = input.int(7, title="EMA 7 (Fast Trigger)"),
    len21: int = input.int(21, title="EMA 21 (Slow Trigger)"),
    len50: int = input.int(50, title="EMA 50 (Trend & Dynamic Stop)"),
    len200: int = input.int(200, title="EMA 200 (Macro Trend)"),
    rsi_len: int = input.int(14, title="RSI Length"),
    rsi_ob: int = input.int(70, title="RSI Overbought (Max for Longs)"),
    rsi_os: int = input.int(30, title="RSI Oversold (Min for Shorts)"),
    rsi_mid: int = input.int(50, title="RSI Centerline (Momentum Shift)"),
):
    ema7 = ta.ema(close, len7)
    ema21 = ta.ema(close, len21)
    ema50 = ta.ema(close, len50)
    ema200 = ta.ema(close, len200)
    rsi_val = ta.rsi(close, rsi_len)

    bullish_macro = ema50 > ema200
    bearish_macro = ema50 < ema200

    rsi_long_ok = rsi_val > rsi_mid and rsi_val < rsi_ob
    rsi_short_ok = rsi_val < rsi_mid and rsi_val > rsi_os

    long_trigger = ta.crossover(ema7, ema21) and rsi_long_ok
    short_trigger = ta.crossunder(ema7, ema21) and rsi_short_ok

    long_exit = ta.crossunder(ema7, ema21) or close < ema50
    short_exit = ta.crossover(ema7, ema21) or close > ema50

    if bullish_macro and long_trigger:
        strategy.entry("Long", strategy.long, comment="Buy")

    if strategy.position_size > 0 and long_exit:
        strategy.close("Long", comment="Exit Long")

    if bearish_macro and short_trigger:
        strategy.entry("Short", strategy.short, comment="Sell")

    if strategy.position_size < 0 and short_exit:
        strategy.close("Short", comment="Exit Short")
