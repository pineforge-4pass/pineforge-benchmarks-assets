"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, input, na, request, script, strategy, syminfo, ta
from pynecore.types import Persistent


@script.strategy("MTF probe 10 - HTF bracket static", shorttitle="MTF_p10", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_htf=input.timeframe("60", "Higher Timeframe"),
    i_htf_ema=input.int(20, "HTF EMA Length", minval=2, maxval=200),
    i_fast_ema=input.int(9, "Fast EMA Length", minval=2, maxval=50),
    i_slow_ema=input.int(21, "Slow EMA Length", minval=3, maxval=100),
    i_atr_len=input.int(14, "ATR Length", minval=2, maxval=50),
    i_stop_mult=input.float(2.0, "Stop ATR mult", minval=0.5, maxval=5.0, step=0.1),
    i_tp_mult=input.float(4.0, "Take-profit ATR mult", minval=0.5, maxval=10.0, step=0.1)
):

    emaFast: float = ta.ema(close, i_fast_ema)
    emaSlow: float = ta.ema(close, i_slow_ema)
    atrVal: float = ta.atr(i_atr_len)

    _htfEmaSeries: float = ta.ema(close, i_htf_ema)
    htfClose: float = request.security(syminfo.tickerid, i_htf, close, barmerge.gaps_off, barmerge.lookahead_off)

    htfEma: float = request.security(syminfo.tickerid, i_htf, _htfEmaSeries, barmerge.gaps_off, barmerge.lookahead_off)

    htfBull: bool = not na(htfClose) and (not na(htfEma)) and (htfClose > htfEma)

    longSig: bool = ta.crossover(emaFast, emaSlow) and htfBull

    entryStop: Persistent[float] = na(float)
    entryTP: Persistent[float] = na(float)

    if longSig and strategy.position_size == 0 and (not na(atrVal)):
        entryStop = close - atrVal * i_stop_mult
        entryTP = close + atrVal * i_tp_mult
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=entryStop, limit=entryTP, comment='static bracket')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
