"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("MACD Histogram Reversal", overlay=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    fastLen=input.int(12, "Fast Length", minval=1),
    slowLen=input.int(26, "Slow Length", minval=1),
    signalLen=input.int(9, "Signal Length", minval=1),
    src: Series[float] = input.source(close, "Source")
):

    macdLine, signalLine, histLine = ta.macd(src, fastLen, slowLen, signalLen)

    longCond = ta.crossover(macdLine, signalLine)
    shortCond = ta.crossunder(macdLine, signalLine)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(histLine, 'Histogram', style=plot.style_histogram, color=color.green if histLine >= 0 else color.red)
    plot(macdLine, 'MACD', color=color.blue)
    plot(signalLine, 'Signal', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)