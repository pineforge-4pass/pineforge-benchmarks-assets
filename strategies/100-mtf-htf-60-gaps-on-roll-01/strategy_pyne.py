"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, currency, na, request, script, strategy, syminfo
from pynecore.types import Persistent


@script.strategy("PF TV golden 47 - security gaps on", shorttitle="PF_G47_GAPS", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    h60Gap = request.security(syminfo.tickerid, '60', close, gaps=barmerge.gaps_on, lookahead=barmerge.lookahead_off)
    lastHtfClose: Persistent[float] = na(float)
    hasHtfValue: bool = not na(h60Gap)
    rollUp: bool = False
    rollDown: bool = False

    if hasHtfValue:
        rollUp = not na(lastHtfClose) and h60Gap > lastHtfClose
        rollDown = not na(lastHtfClose) and h60Gap < lastHtfClose
        lastHtfClose = h60Gap

    if rollUp and strategy.position_size == 0:
        strategy.entry('GAP_UP', strategy.long, qty=1, comment='gap roll up')

    if rollDown and strategy.position_size > 0:
        strategy.close('GAP_UP', comment='gap roll down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
