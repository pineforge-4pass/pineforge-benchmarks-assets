"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("VWMA vs SMA Divergence", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    len=input.int(20, "Length", minval=5)
):

    vwmaVal = ta.vwma(close, len)
    smaVal = ta.sma(close, len)

    vwmaDiff = vwmaVal - smaVal

    longCond = ta.crossover(vwmaDiff, 0)
    shortCond = ta.crossunder(vwmaDiff, 0)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(vwmaVal, 'VWMA', color=color.blue, linewidth=2)
    plot(smaVal, 'SMA', color=color.orange, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
