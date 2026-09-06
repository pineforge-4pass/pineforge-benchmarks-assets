"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, barstate, close, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF MTF probe 01 — 60m close roll", shorttitle="MTF_p01", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    h60: float = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)
    roll: Series[bool] = ta.change(h60) != 0

    if roll:
        strategy.entry('R', strategy.long, qty=1)
    if roll[1]:
        strategy.close('R')

    if barstate.islast and strategy.position_size > 0:
        strategy.close('R')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
