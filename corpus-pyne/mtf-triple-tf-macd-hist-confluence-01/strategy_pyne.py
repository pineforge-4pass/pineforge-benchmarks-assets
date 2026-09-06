"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF MTF probe 08 - triple TF MACD hist", shorttitle="MTF_p08_3MACD", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    def f_macd_hist(src: Series[float], fast: int, slow: int, sig: int):
        macd_val: float = ta.ema(src, fast) - ta.ema(src, slow)
        macd_sig: float = ta.ema(macd_val, sig)
        return macd_val - macd_sig

    h1: float = request.security(syminfo.tickerid, '60', f_macd_hist(close, 12, 26, 9), lookahead=barmerge.lookahead_off)
    h2: float = request.security(syminfo.tickerid, '240', f_macd_hist(close, 12, 26, 9), lookahead=barmerge.lookahead_off)
    h3: float = request.security(syminfo.tickerid, 'D', f_macd_hist(close, 12, 26, 9), lookahead=barmerge.lookahead_off)

    allBull: bool = h1 > 0 and h2 > 0 and (h3 > 0)
    allBear: bool = h1 < 0 and h2 < 0 and (h3 < 0)

    if allBull and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip to long')
        strategy.entry('L', strategy.long, comment='3-TF MACD bull')

    if allBear and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip to short')
        strategy.entry('S', strategy.short, comment='3-TF MACD bear')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
