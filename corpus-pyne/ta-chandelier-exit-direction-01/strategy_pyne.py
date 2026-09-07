"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, plot, script, strategy, ta
from pynecore.types import PersistentSeries, Series


@script.strategy("Chandelier Exit", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    atrLen=input.int(22, "ATR Length", minval=1),
    atrMult=input.float(3.0, "ATR Multiplier", step=0.1),
    lookback=input.int(22, "Lookback", minval=1)
):

    atrVal = ta.atr(atrLen)

    highestHigh = ta.highest(high, lookback)
    lowestLow = ta.lowest(low, lookback)

    chandLong: Series = highestHigh - atrVal * atrMult
    chandShort: Series = lowestLow + atrVal * atrMult

    direction: PersistentSeries[int] = 0

    if close > chandShort[1]:
        direction = 1
    if close < chandLong[1]:
        direction = -1

    longCond = direction == 1 and direction[1] != 1
    shortCond = direction == -1 and direction[1] != -1

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(chandLong, 'Chandelier Long', color=color.green, linewidth=2)
    plot(chandShort, 'Chandelier Short', color=color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
