"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("input.source runtime override", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    src: Series[float] = input.source(close, "Source"),
    fastLen=input.int(10, "Fast Length", minval=2),
    slowLen=input.int(30, "Slow Length", minval=5)
):

    fast = ta.sma(src, fastLen)
    slow = ta.sma(src, slowLen)

    if ta.crossover(fast, slow):
        strategy.entry('Long', strategy.long)
    if ta.crossunder(fast, slow):
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
