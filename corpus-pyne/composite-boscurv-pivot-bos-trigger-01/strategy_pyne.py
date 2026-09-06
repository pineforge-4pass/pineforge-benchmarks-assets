"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, nz, script, strategy, ta
from pynecore.types import PersistentSeries


@script.strategy("PF probe bos-curv-probe-01-swing-bos-trigger", shorttitle="PF_bos01_BOS", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_left=input.int(5, "Pivot left bars", minval=1),
    i_right=input.int(5, "Pivot right bars", minval=1)
):

    ph: float = ta.pivothigh(high, i_left, i_right)
    pl: float = ta.pivotlow(low, i_left, i_right)

    last_ph: PersistentSeries[float] = na(float)
    last_pl: PersistentSeries[float] = na(float)

    if not na(ph):
        last_ph = ph
    if not na(pl):
        last_pl = pl

    bos_long: bool = not na(last_ph) and close > last_ph and (close[1] <= nz(last_ph[1], last_ph))
    bos_short: bool = not na(last_pl) and close < last_pl and (close[1] >= nz(last_pl[1], last_pl))

    if bos_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='bos long')

    if bos_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='bos short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
