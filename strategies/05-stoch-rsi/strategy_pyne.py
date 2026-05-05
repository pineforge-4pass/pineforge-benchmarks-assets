"""@pyne
Hand-port of strategies/05-stoch-rsi/strategy.pine for PyneCore.

Pine source:
    strategy("Stochastic RSI", ...)
    rsiLen, stochLen, kSmooth, dSmooth, obLevel, osLevel = ...
    rsiVal = ta.rsi(close, rsiLen)
    stochK = ta.sma(ta.stoch(rsiVal, rsiVal, rsiVal, stochLen), kSmooth)
    stochD = ta.sma(stochK, dSmooth)
    longCond  = ta.crossover(stochK, stochD) and stochK < osLevel
    shortCond = ta.crossunder(stochK, stochD) and stochK > obLevel
    if longCond:  strategy.entry("Long",  strategy.long)
    if shortCond: strategy.entry("Short", strategy.short)
    if strategy.position_size > 0 and stochK > obLevel and ta.crossunder(stochK, stochD):
        strategy.close("Long")
    if strategy.position_size < 0 and stochK < osLevel and ta.crossover(stochK, stochD):
        strategy.close("Short")
"""
from pynecore import Series
from pynecore.lib import script, input, ta, strategy, close


@script.strategy("Stochastic RSI", overlay=True)
def main(
    rsi_len: int = input.int(14, title="RSI Length", minval=1),
    stoch_len: int = input.int(14, title="Stoch Length", minval=1),
    k_smooth: int = input.int(3, title="K Smoothing", minval=1),
    d_smooth: int = input.int(3, title="D Smoothing", minval=1),
    ob_level: int = input.int(80, title="Overbought"),
    os_level: int = input.int(20, title="Oversold"),
):
    rsi_val: Series[float] = ta.rsi(close, rsi_len)
    stoch_k: Series[float] = ta.sma(ta.stoch(rsi_val, rsi_val, rsi_val, stoch_len), k_smooth)
    stoch_d: Series[float] = ta.sma(stoch_k, d_smooth)

    if ta.crossover(stoch_k, stoch_d) and stoch_k < os_level:
        strategy.entry("Long", strategy.long)
    if ta.crossunder(stoch_k, stoch_d) and stoch_k > ob_level:
        strategy.entry("Short", strategy.short)

    if strategy.position_size > 0 and stoch_k > ob_level and ta.crossunder(stoch_k, stoch_d):
        strategy.close("Long")
    if strategy.position_size < 0 and stoch_k < os_level and ta.crossover(stoch_k, stoch_d):
        strategy.close("Short")
