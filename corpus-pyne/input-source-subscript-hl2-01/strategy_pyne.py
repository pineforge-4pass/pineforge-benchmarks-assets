"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hl2, input, script, strategy
from pynecore.types import Series


@script.strategy("input.source history subscript", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    src: Series[float] = input.source(hl2, "Source")
):

    mom = src - src[1]
    momPrev = src[1] - src[2]

    if mom > 0 and momPrev <= 0:
        strategy.entry('Long', strategy.long)
    if mom < 0 and momPrev >= 0:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
