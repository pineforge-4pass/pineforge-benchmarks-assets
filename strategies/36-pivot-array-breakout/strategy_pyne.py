"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, close, color, currency, high, input, low, na, plot, script,
    strategy, ta
)
from pynecore.types import Persistent


@script.strategy("Pivot Array Breakout", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    pivotLen=input.int(5, "Pivot Length", minval=2),
    maxPivots=input.int(5, "Max Stored Pivots", minval=2)
):

    resistanceLevels: Persistent[list[float]] = array.new_float(0)
    supportLevels: Persistent[list[float]] = array.new_float(0)

    pvtHigh = ta.pivothigh(high, pivotLen, pivotLen)
    pvtLow = ta.pivotlow(low, pivotLen, pivotLen)

    if not na(pvtHigh):
        array.unshift(resistanceLevels, pvtHigh)
        if array.size(resistanceLevels) > maxPivots:
            array.pop(resistanceLevels)

    if not na(pvtLow):
        array.unshift(supportLevels, pvtLow)
        if array.size(supportLevels) > maxPivots:
            array.pop(supportLevels)

    keyRes: Persistent[float] = na(float)
    keySup: Persistent[float] = na(float)

    if array.size(resistanceLevels) > 0:
        keyRes = array.get(resistanceLevels, 0)
    if array.size(supportLevels) > 0:
        keySup = array.get(supportLevels, 0)

    longCond = not na(keyRes) and close > keyRes and (close[1] <= keyRes)
    shortCond = not na(keySup) and close < keySup and (close[1] >= keySup)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and (not na(keySup)) and (close < keySup):
        strategy.close('Long')
    if strategy.position_size < 0 and (not na(keyRes)) and (close > keyRes):
        strategy.close('Short')

    plot(keyRes, 'Resistance', color=color.red, style=plot.style_stepline)
    plot(keySup, 'Support', color=color.green, style=plot.style_stepline)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
