"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import array, close, request, script, strategy, syminfo
from pynecore.types import Persistent


@script.strategy("MTF Array Stats", overlay=False, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    htf_c = request.security(syminfo.tickerid, 'D', close)
    a: Persistent[list[float]] = array.new_float()
    array.push(a, htf_c)
    if array.size(a) > 20:
        array.shift(a)

    if array.size(a) == 20:
        med = array.median(a)
        pr = array.percentrank(a, array.size(a) - 1)

        if pr < 10:
            strategy.entry('Long', strategy.long)
        if pr > 90:
            strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
