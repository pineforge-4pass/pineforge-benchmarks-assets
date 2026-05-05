"""@pyne
Hand-port of strategies/04-macd-histogram/strategy.pine for PyneCore.

Pine source:
    strategy("MACD Histogram Reversal", ...)
    fastLen   = input.int(12, "Fast Length", minval=1)
    slowLen   = input.int(26, "Slow Length", minval=1)
    signalLen = input.int(9,  "Signal Length", minval=1)
    src       = input.source(close, "Source")
    [macdLine, signalLine, histLine] = ta.macd(src, fastLen, slowLen, signalLen)
    longCond  = ta.crossover(macdLine, signalLine)
    shortCond = ta.crossunder(macdLine, signalLine)
    if longCond:  strategy.entry("Long",  strategy.long)
    if shortCond: strategy.entry("Short", strategy.short)
"""
from pynecore import Series
from pynecore.lib import script, input, ta, strategy, close


@script.strategy("MACD Histogram Reversal", overlay=False)
def main(
    fast_len: int = input.int(12, title="Fast Length", minval=1),
    slow_len: int = input.int(26, title="Slow Length", minval=1),
    signal_len: int = input.int(9, title="Signal Length", minval=1),
    src: Series[float] = input.source(close, title="Source"),
):
    macd_line, signal_line, _hist = ta.macd(src, fast_len, slow_len, signal_len)
    if ta.crossover(macd_line, signal_line):
        strategy.entry("Long", strategy.long)
    if ta.crossunder(macd_line, signal_line):
        strategy.entry("Short", strategy.short)
