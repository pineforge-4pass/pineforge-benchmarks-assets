"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("Swing Pivot ATR", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    pivotLen=input.int(5, "Pivot Length", minval=2),
    atrLen=input.int(14, "ATR Length", minval=1),
    atrMult=input.float(1.5, "ATR SL Multiplier", step=0.1),
    tpMult=input.float(2.0, "ATR TP Multiplier", step=0.1)
):

    pvtHigh = ta.pivothigh(high, pivotLen, pivotLen)
    pvtLow = ta.pivotlow(low, pivotLen, pivotLen)
    atrVal = ta.atr(atrLen)

    lastPvtH: Persistent[float] = na(float)
    lastPvtL: Persistent[float] = na(float)

    if not na(pvtHigh):
        lastPvtH = pvtHigh
    if not na(pvtLow):
        lastPvtL = pvtLow

    longCond = not na(lastPvtH) and close > lastPvtH and (close[1] <= lastPvtH)
    shortCond = not na(lastPvtL) and close < lastPvtL and (close[1] >= lastPvtL)

    if longCond:
        strategy.entry('Long', strategy.long)
        strategy.exit('XL', 'Long', stop=close - atrVal * atrMult, limit=close + atrVal * tpMult)

    if shortCond:
        strategy.entry('Short', strategy.short)
        strategy.exit('XS', 'Short', stop=close + atrVal * atrMult, limit=close - atrVal * tpMult)

    plot(lastPvtH, 'Last Pivot High', color=color.red, style=plot.style_stepline)
    plot(lastPvtL, 'Last Pivot Low', color=color.green, style=plot.style_stepline)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
