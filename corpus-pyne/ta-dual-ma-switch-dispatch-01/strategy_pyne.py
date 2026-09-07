"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Dual MA with Switch", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    maType=input.string("EMA", "MA Type", options=("EMA", "SMA", "WMA", "HMA")),
    fastLen=input.int(10, "Fast Length", minval=2),
    slowLen=input.int(30, "Slow Length", minval=5),
    src: Series[float] = input.source(close, "Source")
):

    def getMA(source, length):
        __block_result__ = na
        __switch__ = maType
        if __switch__ == "EMA":
            __block_result__ = ta.ema(source, length)
        elif __switch__ == "SMA":
            __block_result__ = ta.sma(source, length)
        elif __switch__ == "WMA":
            __block_result__ = ta.wma(source, length)
        elif __switch__ == "HMA":
            __block_result__ = ta.hma(source, length)
        else:
            __block_result__ = ta.sma(source, length)
        return __block_result__

    fastMA = getMA(src, fastLen)
    slowMA = getMA(src, slowLen)

    longCond = ta.crossover(fastMA, slowMA)
    shortCond = ta.crossunder(fastMA, slowMA)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(fastMA, 'Fast', color=color.blue, linewidth=2)
    plot(slowMA, 'Slow', color=color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
