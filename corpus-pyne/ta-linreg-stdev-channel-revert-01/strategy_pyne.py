"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("Linear Regression Channel", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    regLen=input.int(50, "Regression Length", minval=10),
    devMult=input.float(2.0, "Deviation Multiplier", step=0.1)
):

    regLine = ta.linreg(close, regLen, 0)
    regDev = ta.stdev(close, regLen) * devMult
    upperBand = regLine + regDev
    lowerBand = regLine - regDev

    longCond = close < lowerBand and close > close[1]
    shortCond = close > upperBand and close < close[1]

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and close > regLine:
        strategy.close('Long')
    if strategy.position_size < 0 and close < regLine:
        strategy.close('Short')

    plot(regLine, 'Regression', color=color.yellow, linewidth=2)
    plot(upperBand, 'Upper', color=color.red)
    plot(lowerBand, 'Lower', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
