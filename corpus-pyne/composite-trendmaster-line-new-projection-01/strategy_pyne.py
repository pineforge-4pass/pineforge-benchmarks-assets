"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, high, input, line, low, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe trendmaster-probe-01-trend-line-projection", shorttitle="PF_TM01_LINE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, max_lines_count=500)
def main(
    i_pivot=input.int(5, "Pivot strength", minval=2, maxval=20)
):

    ph: float = ta.pivothigh(high, i_pivot, i_pivot)
    pl: float = ta.pivotlow(low, i_pivot, i_pivot)

    last_ph_y: Persistent[float] = na(float)
    last_ph_x: Persistent[int] = na(int)
    prev_ph_y: Persistent[float] = na(float)
    prev_ph_x: Persistent[int] = na(int)
    last_pl_y: Persistent[float] = na(float)
    last_pl_x: Persistent[int] = na(int)
    prev_pl_y: Persistent[float] = na(float)
    prev_pl_x: Persistent[int] = na(int)

    if not na(ph):
        cur_x: int = bar_index - i_pivot
        if not na(last_ph_y) and (not na(last_ph_x)):
            line.new(last_ph_x, last_ph_y, cur_x, ph, color=color.red)
        prev_ph_y = last_ph_y
        prev_ph_x = last_ph_x
        last_ph_y = ph
        last_ph_x = cur_x

    if not na(pl):
        cur_x: int = bar_index - i_pivot
        if not na(last_pl_y) and (not na(last_pl_x)):
            line.new(last_pl_x, last_pl_y, cur_x, pl, color=color.green)
        prev_pl_y = last_pl_y
        prev_pl_x = last_pl_x
        last_pl_y = pl
        last_pl_x = cur_x

    ref_lo: float = na(float)
    if not na(prev_pl_y) and (not na(prev_pl_x)) and (not na(last_pl_y)) and (not na(last_pl_x)) and (last_pl_x != prev_pl_x):
        slope: float = (last_pl_y - prev_pl_y) / (last_pl_x - prev_pl_x)
        ref_lo = last_pl_y + slope * (bar_index - last_pl_x)

    ref_hi: float = na(float)
    if not na(prev_ph_y) and (not na(prev_ph_x)) and (not na(last_ph_y)) and (not na(last_ph_x)) and (last_ph_x != prev_ph_x):
        slope: float = (last_ph_y - prev_ph_y) / (last_ph_x - prev_ph_x)
        ref_hi = last_ph_y + slope * (bar_index - last_ph_x)

    long_signal: bool = not na(ref_lo) and ta.crossover(close, ref_lo)
    short_signal: bool = not na(ref_hi) and ta.crossunder(close, ref_hi)

    if long_signal and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='proj long')

    if short_signal and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='proj short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
