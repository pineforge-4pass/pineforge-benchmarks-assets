"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, open, script, strategy, ta
from pynecore.types import Persistent, PersistentSeries


@script.strategy("PF probe liquidity-sweep-probe-integration", shorttitle="PF_lspINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_left=input.int(5, "Pivot left bars", minval=1),
    i_right=input.int(5, "Pivot right bars", minval=1)
):

    ph: float = ta.pivothigh(high, i_left, i_right)
    pl: float = ta.pivotlow(low, i_left, i_right)

    last_ph: Persistent[float] = na(float)
    prev_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)
    prev_pl: Persistent[float] = na(float)

    if not na(ph):
        prev_ph = last_ph
        last_ph = ph
    if not na(pl):
        prev_pl = last_pl
        last_pl = pl

    struct_bull: Persistent[bool] = False
    struct_bear: Persistent[bool] = False

    if not na(ph) and (not na(prev_ph)):
        if ph > prev_ph:
            struct_bull = True
            struct_bear = False
    if not na(pl) and (not na(prev_pl)):
        if pl < prev_pl:
            struct_bear = True
            struct_bull = False

    sweep_high: bool = not na(last_ph) and high > last_ph and (close < last_ph)
    sweep_low: bool = not na(last_pl) and low < last_pl and (close > last_pl)

    wait_long: PersistentSeries[int] = 0
    wait_short: PersistentSeries[int] = 0

    if sweep_low and struct_bull:
        wait_long = 1
    elif wait_long > 0:
        wait_long = wait_long - 1

    if sweep_high and struct_bear:
        wait_short = 1
    elif wait_short > 0:
        wait_short = wait_short - 1

    fire_long: bool = wait_long == 0 and wait_long[1] == 1 and (close > open)
    fire_short: bool = wait_short == 0 and wait_short[1] == 1 and (close < open)

    if fire_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ long')

    if fire_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
