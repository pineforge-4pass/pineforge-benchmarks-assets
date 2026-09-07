"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta
from pynecore.types import Persistent, Series


@script.strategy("BB Squeeze Breakout", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    bbLen=input.int(20, "BB Length", minval=5),
    bbMult=input.float(2.0, "BB Multiplier", step=0.1),
    kcLen=input.int(20, "KC Length", minval=5),
    kcMult=input.float(1.5, "KC Multiplier", step=0.1),
    src: Series[float] = input.source(close, "Source")
):

    bbMid, bbUpper, bbLower = ta.bb(src, bbLen, bbMult)

    kcMid, kcUpper, kcLower = ta.kc(src, kcLen, kcMult)

    sqzOn = bbLower > kcLower and bbUpper < kcUpper
    sqzOff = bbLower < kcLower or bbUpper > kcUpper

    mom = ta.linreg(src - bbMid, bbLen, 0)

    wasSqueezed: Persistent[bool] = False
    if sqzOn:
        wasSqueezed = True

    sqzFired = wasSqueezed and sqzOff

    if sqzFired and mom > 0:
        strategy.entry('Long', strategy.long)
        wasSqueezed = False
    if sqzFired and mom < 0:
        strategy.entry('Short', strategy.short)
        wasSqueezed = False

    if strategy.position_size > 0 and mom < 0:
        strategy.close('Long')
    if strategy.position_size < 0 and mom > 0:
        strategy.close('Short')

    plot(bbUpper, 'BB Upper', color=color.blue)
    plot(bbLower, 'BB Lower', color=color.blue)
    plot(kcUpper, 'KC Upper', color=color.orange)
    plot(kcLower, 'KC Lower', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
