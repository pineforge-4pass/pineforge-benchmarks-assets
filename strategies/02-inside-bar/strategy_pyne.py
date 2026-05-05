"""@pyne
Hand-port of strategies/02-inside-bar/strategy.pine for PyneCore.

Pine source (4 lines):
    strategy("InSide Bar Strategy", overlay=true, ...)
    if (high < high[1] and low > low[1])
        if (close > open)
            strategy.entry("InsBarLE", strategy.long, comment="InsBarLE")
        if (close < open)
            strategy.entry("InsBarSE", strategy.short, comment="InsBarSE")
"""
from pynecore.lib import script, strategy, high, low, close, open


@script.strategy("InSide Bar Strategy", overlay=True)
def main():
    if high < high[1] and low > low[1]:
        if close > open:
            strategy.entry("InsBarLE", strategy.long)
        if close < open:
            strategy.entry("InsBarSE", strategy.short)
