"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, math, na, script, strategy, ta
from pynecore.types import PersistentSeries


@script.strategy("PF probe kanuck-probe-01-kama-state", shorttitle="PF_kan01_KAMA", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_kama_len=input.int(14, "KAMA length", minval=2),
    i_kama_fast=input.int(2, "KAMA fast end", minval=1),
    i_kama_slow=input.int(30, "KAMA slow end", minval=2)
):

    change_n: float = math.abs(close - close[i_kama_len])
    vol_sum: float = math.sum(math.abs(close - close[1]), i_kama_len)
    er: float = change_n / vol_sum if vol_sum > 0 else 0.0
    fast_sc: float = 2.0 / (i_kama_fast + 1)
    slow_sc: float = 2.0 / (i_kama_slow + 1)
    sc: float = math.pow(er * (fast_sc - slow_sc) + slow_sc, 2)
    kama: PersistentSeries[float] = na(float)
    kama = close if na(kama[1]) else kama[1] + sc * (close - kama[1])

    cross_up: bool = ta.crossover(close, kama)
    cross_down: bool = ta.crossunder(close, kama)

    if cross_up and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='kama cross up')

    if cross_down and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='kama cross down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
