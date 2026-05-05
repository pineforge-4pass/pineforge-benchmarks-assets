"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("RSI with Bollinger Bands", overlay=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    rsiLen=input.int(14, "RSI Length", minval=1),
    bbLen=input.int(50, "BB Length on RSI", minval=5),
    bbMult=input.float(2.0, "BB Mult", step=0.1)
):

    rsiVal: Series = ta.rsi(close, rsiLen)

    rsiBBMid = ta.sma(rsiVal, bbLen)
    rsiDev = ta.stdev(rsiVal, bbLen) * bbMult
    rsiBBUp = rsiBBMid + rsiDev
    rsiBBDn = rsiBBMid - rsiDev

    longCond = rsiVal < rsiBBDn and rsiVal > rsiVal[1]
    shortCond = rsiVal > rsiBBUp and rsiVal < rsiVal[1]

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and rsiVal > rsiBBMid:
        strategy.close('Long')
    if strategy.position_size < 0 and rsiVal < rsiBBMid:
        strategy.close('Short')

    plot(rsiVal, 'RSI', color=color.blue, linewidth=2)
    plot(rsiBBUp, 'RSI BB Upper', color=color.red)
    plot(rsiBBMid, 'RSI BB Mid', color=color.gray)
    plot(rsiBBDn, 'RSI BB Lower', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
