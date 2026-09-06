"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, input, low, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe liquidity-sweep-probe-01-pivot-swing", shorttitle="PF_lsp01_SWG", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
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

    higher_high: bool = not na(ph) and (not na(prev_ph)) and (ph > prev_ph)
    lower_low: bool = not na(pl) and (not na(prev_pl)) and (pl < prev_pl)

    if higher_high and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='hh long')

    if lower_low and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='ll short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
