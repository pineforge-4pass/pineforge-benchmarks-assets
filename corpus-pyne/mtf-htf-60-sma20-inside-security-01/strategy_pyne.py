"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF MTF probe 03 — 60m SMA(20)", shorttitle="MTF_p03", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    htfSma: Series[float] = request.security(syminfo.tickerid, '60', ta.sma(close, 20), lookahead=barmerge.lookahead_off)
    htfCl: Series[float] = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)

    longCond: bool = htfCl > htfSma and htfCl[1] <= htfSma[1]

    if longCond:
        strategy.entry('L', strategy.long, qty=1)

    exitCond: bool = htfCl < htfSma and strategy.position_size > 0
    if exitCond:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
