"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, high, input, low, math, plot, script, strategy, ta
from pynecore.types import Persistent, PersistentSeries


@script.strategy("Range Filter", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    filterLen=input.int(50, "Filter Length", minval=5),
    filterMult=input.float(2.5, "Range Multiplier", step=0.1)
):

    avgRange = ta.ema(high - low, filterLen)
    smoothRng = avgRange * filterMult

    rangeFilter: Persistent[float] = close
    filterDir: PersistentSeries[int] = 0

    hiTarget = rangeFilter + smoothRng
    loTarget = rangeFilter - smoothRng

    if close > hiTarget:
        rangeFilter = close - smoothRng
        filterDir = 1
    elif close < loTarget:
        rangeFilter = close + smoothRng
        filterDir = -1
    else:
        if filterDir == 1:
            newFilter = close - smoothRng
            rangeFilter = math.max(rangeFilter, newFilter)
        elif filterDir == -1:
            newFilter = close + smoothRng
            rangeFilter = math.min(rangeFilter, newFilter)

    longCond = filterDir == 1 and filterDir[1] != 1
    shortCond = filterDir == -1 and filterDir[1] != -1

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(rangeFilter, 'Range Filter', color=color.green if filterDir == 1 else color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
