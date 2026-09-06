"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, high, request, script, strategy, syminfo
from pynecore.types import Series


@script.strategy("PF MTF probe 04 — D high[1] break", shorttitle="MTF_p04", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    dHigh1: Series[float] = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_off)
    crossUp: bool = close > dHigh1 and close[1] <= dHigh1[1]

    if crossUp and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1)

    if close < dHigh1 * 0.995 and strategy.position_size > 0:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
