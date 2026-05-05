"""@pyne
Hand-port of strategies/03-supertrend/strategy.pine for PyneCore.

Pine source:
    strategy("Supertrend Strategy", ...)
    atrPeriod = input(10, "ATR Length")
    factor    = input.float(3.0, "Factor", step=0.01)
    [_, direction] = ta.supertrend(factor, atrPeriod)
    if ta.change(direction) < 0
        strategy.entry("My Long Entry Id", strategy.long)
    if ta.change(direction) > 0
        strategy.entry("My Short Entry Id", strategy.short)
"""
from pynecore.lib import script, input, ta, strategy


@script.strategy("Supertrend Strategy", overlay=True)
def main(
    atr_period: int = input.int(10, title="ATR Length"),
    factor: float = input.float(3.0, title="Factor", step=0.01),
):
    _, direction = ta.supertrend(factor, atr_period)
    chg = ta.change(direction)
    if chg < 0:
        strategy.entry("My Long Entry Id", strategy.long)
    if chg > 0:
        strategy.entry("My Short Entry Id", strategy.short)
