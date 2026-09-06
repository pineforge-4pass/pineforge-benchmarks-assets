"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, request, script, strategy, syminfo, ta, volume


@script.strategy("PF MTF probe 06 — 60m volume sum", shorttitle="MTF_p06", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    htfVol: float = request.security(syminfo.tickerid, '60', volume, lookahead=barmerge.lookahead_off)
    htfVolSma: float = request.security(syminfo.tickerid, '60', ta.sma(volume, 20), lookahead=barmerge.lookahead_off)

    spike: bool = htfVol > htfVolSma * 2.0

    if spike and strategy.position_size == 0:
        strategy.entry('V', strategy.long, qty=1)

    if not spike and strategy.position_size > 0:
        strategy.close('V')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
