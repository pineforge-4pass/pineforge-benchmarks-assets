"""@pyne
Hand-port of strategies/06-liquidity-sweep/strategy.pine for PyneCore.

Pine source (AIScripts, MPL-2.0):
    "Liquidity Sweep + Market Structure Strategy"
    - Liquidity sweep detection over `lookback` bars
    - Market-structure break confirmation over `structureLen` bars
    - ATR-sized stop + R/R take-profit per side via strategy.exit
"""
from pynecore import Series
from pynecore.lib import script, input, ta, strategy, high, low, close


@script.strategy("Liquidity Sweep + Market Structure Strategy", overlay=True)
def main(
    lookback: int = input.int(20, title="Liquidity Lookback"),
    structure_len: int = input.int(5, title="Structure Length"),
    atr_len: int = input.int(14, title="ATR Length"),
    atr_mult: float = input.float(1.5, title="Stop ATR Multiplier"),
    rr: float = input.float(2.0, title="Risk Reward"),
):
    recent_high: Series[float] = ta.highest(high[1], lookback)
    recent_low: Series[float] = ta.lowest(low[1], lookback)

    sweep_high: Series[bool] = high > recent_high and close < recent_high
    sweep_low: Series[bool] = low < recent_low and close > recent_low

    structure_high: Series[float] = ta.highest(high, structure_len)
    structure_low: Series[float] = ta.lowest(low, structure_len)

    bull_break = close > structure_high[1]
    bear_break = close < structure_low[1]

    long_cond = sweep_low[1] and bull_break
    short_cond = sweep_high[1] and bear_break

    atr_value = ta.atr(atr_len)

    if long_cond and strategy.position_size == 0:
        strategy.entry("Long", strategy.long)
    if short_cond and strategy.position_size == 0:
        strategy.entry("Short", strategy.short)

    long_stop = strategy.position_avg_price - atr_value * atr_mult
    long_take = strategy.position_avg_price + atr_value * atr_mult * rr
    short_stop = strategy.position_avg_price + atr_value * atr_mult
    short_take = strategy.position_avg_price - atr_value * atr_mult * rr

    strategy.exit("Exit Long", from_entry="Long", stop=long_stop, limit=long_take)
    strategy.exit("Exit Short", from_entry="Short", stop=short_stop, limit=short_take)
