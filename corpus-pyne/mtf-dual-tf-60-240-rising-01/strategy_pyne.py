"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, request, script, strategy, syminfo
from pynecore.types import Series


@script.strategy("PF MTF probe 02 — dual TF closes", shorttitle="MTF_p02", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    h60: Series[float] = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)
    h240: Series[float] = request.security(syminfo.tickerid, '240', close, lookahead=barmerge.lookahead_off)

    up60: bool = h60 > h60[1]
    up240: bool = h240 > h240[1]
    bothUp: bool = up60 and up240

    if bothUp and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1)

    exitSig: bool = not up60 and strategy.position_size > 0
    if exitSig:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
