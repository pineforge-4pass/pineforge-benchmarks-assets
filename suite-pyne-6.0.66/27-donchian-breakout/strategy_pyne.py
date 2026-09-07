"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, high, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Donchian Channel Breakout", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    entryLen=input.int(20, "Entry Channel Length", minval=5),
    exitLen=input.int(10, "Exit Channel Length", minval=3)
):

    entryUpper: Series = ta.highest(high, entryLen)
    entryLower: Series = ta.lowest(low, entryLen)
    entryMid = (entryUpper + entryLower) / 2

    exitUpper: Series = ta.highest(high, exitLen)
    exitLower: Series = ta.lowest(low, exitLen)

    longCond = close > entryUpper[1]
    shortCond = close < entryLower[1]

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and close < exitLower[1]:
        strategy.close('Long')
    if strategy.position_size < 0 and close > exitUpper[1]:
        strategy.close('Short')

    plot(entryUpper, 'Entry Upper', color=color.green)
    plot(entryLower, 'Entry Lower', color=color.red)
    plot(entryMid, 'Mid', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
