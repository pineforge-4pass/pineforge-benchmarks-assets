"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("EMA Ribbon", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    fastLen=input.int(8, "Fast EMA", minval=2),
    midLen=input.int(21, "Mid EMA", minval=5),
    slowLen=input.int(55, "Slow EMA", minval=10)
):

    emaFast = ta.ema(close, fastLen)
    emaMid = ta.ema(close, midLen)
    emaSlow = ta.ema(close, slowLen)

    bullStack = emaFast > emaMid and emaMid > emaSlow
    bearStack = emaFast < emaMid and emaMid < emaSlow

    prevDir: Persistent[int] = 0

    if bullStack and prevDir != 1:
        strategy.entry('Long', strategy.long)
        prevDir = 1
    if bearStack and prevDir != -1:
        strategy.entry('Short', strategy.short)
        prevDir = -1
    if not bullStack and (not bearStack):
        prevDir = 0

    plot(emaFast, 'Fast', color=color.blue)
    plot(emaMid, 'Mid', color=color.orange)
    plot(emaSlow, 'Slow', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
