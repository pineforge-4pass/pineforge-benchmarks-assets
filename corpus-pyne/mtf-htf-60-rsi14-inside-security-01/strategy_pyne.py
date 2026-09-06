"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, request, script, strategy, syminfo, ta


@script.strategy("PF MTF probe 05 — 60m RSI(14)", shorttitle="MTF_p05", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    htfRsi: float = request.security(syminfo.tickerid, '60', ta.rsi(close, 14), lookahead=barmerge.lookahead_off)
    longCond: bool = ta.crossover(htfRsi, 50)
    shortCond: bool = ta.crossunder(htfRsi, 50)

    if longCond:
        strategy.entry('L', strategy.long, qty=1)
    if shortCond and strategy.position_size > 0:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
