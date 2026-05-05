"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, hline, input, plot, script, strategy, ta


@script.strategy("Momentum ROC Combo", overlay=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    momLen=input.int(10, "Momentum Length", minval=1),
    rocLen=input.int(10, "ROC Length", minval=1)
):

    momVal = ta.mom(close, momLen)
    rocVal = ta.roc(close, rocLen)

    longCond = ta.crossover(momVal, 0) and rocVal > 0
    shortCond = ta.crossunder(momVal, 0) and rocVal < 0

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and momVal < 0:
        strategy.close('Long')
    if strategy.position_size < 0 and momVal > 0:
        strategy.close('Short')

    plot(momVal, 'Momentum', color=color.blue)
    plot(rocVal, 'ROC', color=color.green)
    hline(0, 'Zero')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
