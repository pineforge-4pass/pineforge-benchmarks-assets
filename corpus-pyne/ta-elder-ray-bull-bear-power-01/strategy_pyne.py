"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, hline, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Elder Ray Index", overlay=False, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    emaLen=input.int(13, "EMA Length", minval=1)
):

    emaVal = ta.ema(close, emaLen)
    bullPower: Series = high - emaVal
    bearPower: Series = low - emaVal

    emaTrend = ta.ema(close, 50)
    upTrend = close > emaTrend
    dnTrend = close < emaTrend

    longCond = upTrend and bearPower < 0 and (bearPower > bearPower[1])

    shortCond = dnTrend and bullPower > 0 and (bullPower < bullPower[1])

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and bearPower > 0 and (bearPower < bearPower[1]):
        strategy.close('Long')
    if strategy.position_size < 0 and bullPower < 0 and (bullPower > bullPower[1]):
        strategy.close('Short')

    plot(bullPower, 'Bull Power', color=color.green, style=plot.style_histogram)
    plot(bearPower, 'Bear Power', color=color.red, style=plot.style_histogram)
    hline(0, 'Zero')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
