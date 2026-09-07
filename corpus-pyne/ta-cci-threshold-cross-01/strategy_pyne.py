"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hline, input, plot, script, strategy, ta


@script.strategy("CCI Momentum", overlay=False, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    cciLen=input.int(20, "CCI Length", minval=5),
    obLevel=input.int(100, "Overbought"),
    osLevel=input.int(-100, "Oversold")
):

    cciVal = ta.cci(close, cciLen)

    longCond = ta.crossover(cciVal, osLevel)
    shortCond = ta.crossunder(cciVal, obLevel)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and ta.crossunder(cciVal, 0):
        strategy.close('Long')
    if strategy.position_size < 0 and ta.crossover(cciVal, 0):
        strategy.close('Short')

    plot(cciVal, 'CCI', color=color.blue)
    hline(obLevel, 'Overbought', color=color.red)
    hline(osLevel, 'Oversold', color=color.green)
    hline(0, 'Zero', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
