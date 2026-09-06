"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe market-shift-probe-01-shift-state", shorttitle="PF_MS01_STATE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_pivot=input.int(5, "Pivot strength (left=right)", minval=2, maxval=20)
):

    ph: float = ta.pivothigh(high, i_pivot, i_pivot)
    pl: float = ta.pivotlow(low, i_pivot, i_pivot)

    last_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)

    if not na(ph):
        last_ph = ph
    if not na(pl):
        last_pl = pl

    market_state: Persistent[int] = 0

    break_up: bool = not na(last_ph) and close > last_ph
    break_down: bool = not na(last_pl) and close < last_pl

    if break_up:
        market_state = 1
    elif break_down:
        market_state = -1

    if market_state == 1 and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='state bull')

    if market_state == -1 and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='state bear')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
