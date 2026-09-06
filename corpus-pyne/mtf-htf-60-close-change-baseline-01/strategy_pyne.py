"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, barstate, close, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PineForge RS parity [15m→60m close]", shorttitle="PF_RS_60m", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    htfClose: float = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)
    htfRoll: Series[bool] = ta.change(htfClose) != 0

    if htfRoll:
        strategy.entry('HTF_ROLL', strategy.long, qty=1, comment='roll')

    if htfRoll[1]:
        strategy.close('HTF_ROLL', comment='roll+1')

    if barstate.islast and strategy.position_size > 0:
        strategy.close('HTF_ROLL', comment='last bar flat')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
