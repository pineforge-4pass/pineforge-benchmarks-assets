"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe trendmaster-probe-03-pivot-tp-sl", shorttitle="PF_TM03_PVTP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_pivot=input.int(5, "Pivot strength", minval=2, maxval=20),
    i_rr=input.float(2.0, "Reward:risk ratio", minval=0.5, maxval=10.0, step=0.5),
    i_fast=input.int(5, "Fast EMA", minval=2, maxval=50),
    i_slow=input.int(13, "Slow EMA", minval=3, maxval=100)
):

    ph: float = ta.pivothigh(high, i_pivot, i_pivot)
    pl: float = ta.pivotlow(low, i_pivot, i_pivot)

    last_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)

    if not na(ph):
        last_ph = ph
    if not na(pl):
        last_pl = pl

    ema_fast: float = ta.ema(close, i_fast)
    ema_slow: float = ta.ema(close, i_slow)

    long_signal: bool = ta.crossover(ema_fast, ema_slow)
    short_signal: bool = ta.crossunder(ema_fast, ema_slow)

    if long_signal and (not na(last_pl)) and (strategy.position_size <= 0):
        strategy.entry('L', strategy.long, qty=1, comment='pivot long')

    if short_signal and (not na(last_ph)) and (strategy.position_size >= 0):
        strategy.entry('S', strategy.short, qty=1, comment='pivot short')

    entry_px: float = strategy.position_avg_price

    if strategy.position_size > 0 and (not na(last_pl)):
        sl_px: float = last_pl
        tp_px: float = entry_px + (entry_px - last_pl) * i_rr
        strategy.exit('Brk', from_entry='L', stop=sl_px, limit=tp_px)

    if strategy.position_size < 0 and (not na(last_ph)):
        sl_px: float = last_ph
        tp_px: float = entry_px - (last_ph - entry_px) * i_rr
        strategy.exit('Brk', from_entry='S', stop=sl_px, limit=tp_px)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
