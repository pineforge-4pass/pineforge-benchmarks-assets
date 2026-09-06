"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, math, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("ATR Trailing Stop", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    atrLen=input.int(14, "ATR Length", minval=1),
    atrMult=input.float(2.0, "ATR Multiplier", step=0.1),
    maLen=input.int(20, "MA Length", minval=5)
):

    atrVal = ta.atr(atrLen)
    maVal = ta.ema(close, maLen)

    trailStop: Persistent[float] = na(float)
    isLong: Persistent[bool] = False

    longEntry = ta.crossover(close, maVal)
    shortEntry = ta.crossunder(close, maVal)

    if longEntry:
        strategy.entry('Long', strategy.long)
        isLong = True
        trailStop = close - atrVal * atrMult

    if shortEntry:
        strategy.entry('Short', strategy.short)
        isLong = False
        trailStop = close + atrVal * atrMult

    if isLong and strategy.position_size > 0:
        newStop = close - atrVal * atrMult
        if not na(trailStop):
            trailStop = math.max(trailStop, newStop)
        else:
            trailStop = newStop
        if close < trailStop:
            strategy.close('Long')
            isLong = False

    if not isLong and strategy.position_size < 0:
        newStop = close + atrVal * atrMult
        if not na(trailStop):
            trailStop = math.min(trailStop, newStop)
        else:
            trailStop = newStop
        if close > trailStop:
            strategy.close('Short')

    plot(trailStop, 'Trail Stop', color=color.green if isLong else color.red, style=plot.style_stepline)
    plot(maVal, 'MA', color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
