"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, script, strategy, ta
from pynecore.types import Persistent, Series


@script.strategy("PF probe market-shift-probe-integration", shorttitle="PF_MSINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_pivot=input.int(5, "Pivot strength", minval=2, maxval=20),
    i_window=input.int(50, "Rolling window length", minval=10, maxval=200)
):

    ph: float = ta.pivothigh(high, i_pivot, i_pivot)
    pl: float = ta.pivotlow(low, i_pivot, i_pivot)

    last_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)

    if not na(ph):
        last_ph = ph
    if not na(pl):
        last_pl = pl

    roll_hi: Series[float] = ta.highest(high, i_window)
    roll_lo: Series[float] = ta.lowest(low, i_window)

    ref_hi: float = roll_hi[1]
    ref_lo: float = roll_lo[1]

    extreme_up: bool = ta.crossover(close, ref_lo)
    extreme_down: bool = ta.crossunder(close, ref_hi)

    market_state: Persistent[int] = 0
    prev_state: Persistent[int] = 0

    pivot_break_up: bool = not na(last_ph) and close > last_ph
    pivot_break_down: bool = not na(last_pl) and close < last_pl

    if pivot_break_up:
        market_state = 1
    elif pivot_break_down:
        market_state = -1

    state_long_edge: bool = market_state == 1 and prev_state != 1
    state_short_edge: bool = market_state == -1 and prev_state != -1

    go_long: bool = state_long_edge or (market_state == 1 and extreme_up)
    go_short: bool = state_short_edge or (market_state == -1 and extreme_down)

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ bull')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ bear')

    prev_state = market_state


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
