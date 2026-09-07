"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("Stochastic RSI", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    rsiLen=input.int(14, "RSI Length", minval=1),
    stochLen=input.int(14, "Stoch Length", minval=1),
    kSmooth=input.int(3, "K Smoothing", minval=1),
    dSmooth=input.int(3, "D Smoothing", minval=1),
    obLevel=input.int(80, "Overbought"),
    osLevel=input.int(20, "Oversold")
):

    rsiVal = ta.rsi(close, rsiLen)
    stochK = ta.sma(ta.stoch(rsiVal, rsiVal, rsiVal, stochLen), kSmooth)
    stochD = ta.sma(stochK, dSmooth)

    longCond = ta.crossover(stochK, stochD) and stochK < osLevel
    shortCond = ta.crossunder(stochK, stochD) and stochK > obLevel

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and stochK > obLevel and ta.crossunder(stochK, stochD):
        strategy.close('Long')
    if strategy.position_size < 0 and stochK < osLevel and ta.crossover(stochK, stochD):
        strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
