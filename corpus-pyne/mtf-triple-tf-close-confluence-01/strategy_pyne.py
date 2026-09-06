"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, request, script, strategy, syminfo
from pynecore.types import Series


@script.strategy("PF MTF probe 07 - triple TF close", shorttitle="MTF_p07_3TF", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    h60: Series[float] = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)
    h240: Series[float] = request.security(syminfo.tickerid, '240', close, lookahead=barmerge.lookahead_off)
    hD: Series[float] = request.security(syminfo.tickerid, 'D', close, lookahead=barmerge.lookahead_off)

    allUp: bool = h60 > h60[1] and h240 > h240[1] and (hD > hD[1])
    allDown: bool = h60 < h60[1] and h240 < h240[1] and (hD < hD[1])

    if allUp and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip to long')
        strategy.entry('L', strategy.long, comment='3-TF close up')

    if allDown and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip to short')
        strategy.entry('S', strategy.short, comment='3-TF close down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
