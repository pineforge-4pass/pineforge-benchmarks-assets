"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, na, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF MTF probe 09 - daily EMA warmup", shorttitle="MTF_p09_DEMA", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    htfEma: Series[float] = request.security(syminfo.tickerid, 'D', ta.ema(close, 26), lookahead=barmerge.lookahead_off)
    emaRising: bool = not na(htfEma) and (not na(htfEma[1])) and (htfEma > htfEma[1])
    emaFalling: bool = not na(htfEma) and (not na(htfEma[1])) and (htfEma < htfEma[1])

    if emaRising and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip to long')
        strategy.entry('L', strategy.long, comment='daily EMA rising')

    if emaFalling and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip to short')
        strategy.entry('S', strategy.short, comment='daily EMA falling')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
