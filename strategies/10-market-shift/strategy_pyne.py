"""@pyne
Hand-port of strategies/10-market-shift/strategy.pine for PyneCore.

Pine source: "Market Shift Levels + 152MA Strategy - v2" (ChartPrime, MPL-2.0)
  - HMA(55) trend-shift detection: bull when HMA cross above HMA[5], bear inverse
  - Bar coloured green/red relative to the persistent shift-level
  - SMA(152) macro trend filter
  - Multiple exit rules:
      * Long exit if red bar AND close below entry, OR red bar AND close < SMA152
      * Long exit if last 2 bars green AND close[1] < SMA152[1] AND current bar red
      * Mirror set for shorts
      * Optional daily-close at hour=4 minute>=55 (overridden via input)
  - Implicit reversal: long entry while short → close short then go long
"""
from pynecore import Series, Persistent
from pynecore.lib import script, input, ta, strategy, close, high, low, hour, minute


@script.strategy("Market Shift Levels + 152MA Strategy - v2", overlay=True)
def main(
    length: int = input.int(55, title="Market Shift Length"),
    allow_overnight: bool = input.bool(False, title="Allow Overnight Position"),
):
    ma_period = 152
    close_hour = 4
    close_minute = 55

    level: Persistent[float] = float("nan")

    hma1: Series[float] = ta.hma(close, length)
    hma2 = hma1[5]

    if ta.crossover(hma1, hma2):
        level = low
    if ta.crossunder(hma1, hma2):
        level = high

    sma152: Series[float] = ta.sma(close, ma_period)

    is_red_bar: Series[bool] = close < level
    is_green_bar: Series[bool] = not is_red_bar
    is_below_sma: Series[bool] = close < sma152
    is_above_sma: Series[bool] = not is_below_sma

    is_close_time = False
    if not allow_overnight:
        is_close_time = (hour == close_hour and minute >= close_minute)

    # Time-of-day forced close
    if is_close_time and strategy.position_size != 0:
        if strategy.position_size > 0:
            strategy.close("Long", comment="Daily Close")
        else:
            strategy.close("Short", comment="Daily Close")

    # LONG exits
    if strategy.position_size > 0 and is_red_bar and close < strategy.position_avg_price:
        strategy.close("Long", comment="red+below_entry")
    if strategy.position_size > 0 and is_red_bar and is_below_sma:
        strategy.close("Long", comment="red+below_sma152")
    if strategy.position_size > 0:
        if is_green_bar[1] and is_green_bar[2] and close[1] < sma152[1]:
            if is_red_bar:
                strategy.close("Long", comment="2green_below_sma+red")

    # SHORT exits
    if strategy.position_size < 0 and is_green_bar and close > strategy.position_avg_price:
        strategy.close("Short", comment="green+above_entry")
    if strategy.position_size < 0 and is_green_bar and is_above_sma:
        strategy.close("Short", comment="green+above_sma152")
    if strategy.position_size < 0:
        if is_red_bar[1] and is_red_bar[2] and close[1] > sma152[1]:
            if is_green_bar:
                strategy.close("Short", comment="2red_above_sma+green")

    # LONG entry (with implicit reversal)
    long_entry = is_green_bar and is_above_sma
    if long_entry and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close("Short")
        strategy.entry("Long", strategy.long)

    # SHORT entry (with implicit reversal)
    short_entry = is_red_bar and is_below_sma
    if short_entry and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close("Long")
        strategy.entry("Short", strategy.short)
