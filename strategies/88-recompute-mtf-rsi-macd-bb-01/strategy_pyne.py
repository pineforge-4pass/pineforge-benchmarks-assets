"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, currency, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF TA recompute probe 01 - MTF RSI MACD BB", shorttitle="TArec_p01_MTF", overlay=True, initial_capital=1000000, currency=currency.USD, use_bar_magnifier=False, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    def f_rsi(src: Series[float], len: int):
        return ta.rsi(src, len)

    def f_macd_hist(src: Series[float], fast: int, slow: int, sig: int):
        macdLine: float = ta.ema(src, fast) - ta.ema(src, slow)
        sigLine: float = ta.ema(macdLine, sig)
        return macdLine - sigLine

    def f_bb_mid(src: Series[float], len: int):
        return ta.sma(src, len)

    htfRsi: float = request.security(syminfo.tickerid, '60', f_rsi(close, 14), lookahead=barmerge.lookahead_off)
    htfHist: float = request.security(syminfo.tickerid, '60', f_macd_hist(close, 12, 26, 9), lookahead=barmerge.lookahead_off)
    htfBbM: float = request.security(syminfo.tickerid, '60', f_bb_mid(close, 20), lookahead=barmerge.lookahead_off)
    htfClose: float = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)

    bullAgree: bool = htfRsi > 55.0 and htfHist > 0.0 and (htfClose > htfBbM)
    bearAgree: bool = htfRsi < 45.0 or htfHist < 0.0 or htfClose < htfBbM

    if bullAgree and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if bearAgree and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
