"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, input, low, math, open, plot, script,
    strategy, ta
)


@script.strategy("Dual Thrust Breakout", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    lookback=input.int(4, "Lookback Period", minval=1),
    kUp=input.float(0.5, "Upper K Factor", step=0.1),
    kDn=input.float(0.5, "Lower K Factor", step=0.1)
):

    hh = ta.highest(high, lookback)
    lc = ta.lowest(close, lookback)
    hc = ta.highest(close, lookback)
    ll = ta.lowest(low, lookback)

    range1 = hh - lc
    range2 = hc - ll
    dualRange = math.max(range1, range2)

    upperBound = open + kUp * dualRange
    lowerBound = open - kDn * dualRange

    longCond = close > upperBound
    shortCond = close < lowerBound

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and close < lowerBound:
        strategy.close('Long')
    if strategy.position_size < 0 and close > upperBound:
        strategy.close('Short')

    plot(upperBound, 'Upper', color=color.green)
    plot(lowerBound, 'Lower', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)