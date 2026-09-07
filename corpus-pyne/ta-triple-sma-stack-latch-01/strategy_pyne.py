"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("MA Stack Array", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    ma1Len=input.int(10, "MA 1 Length", minval=2),
    ma2Len=input.int(20, "MA 2 Length", minval=2),
    ma3Len=input.int(50, "MA 3 Length", minval=2)
):

    ma1 = ta.sma(close, ma1Len)
    ma2 = ta.sma(close, ma2Len)
    ma3 = ta.sma(close, ma3Len)

    bullStack = ma1 > ma2 and ma2 > ma3
    bearStack = ma1 < ma2 and ma2 < ma3

    prevBull: Persistent[bool] = False
    prevBear: Persistent[bool] = False

    if bullStack and (not prevBull):
        strategy.entry('Long', strategy.long)
    if bearStack and (not prevBear):
        strategy.entry('Short', strategy.short)

    prevBull = bullStack
    prevBear = bearStack

    if strategy.position_size > 0 and (not bullStack):
        strategy.close('Long')
    if strategy.position_size < 0 and (not bearStack):
        strategy.close('Short')

    plot(ma1, 'MA 10', color=color.blue)
    plot(ma2, 'MA 20', color=color.green)
    plot(ma3, 'MA 50', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
