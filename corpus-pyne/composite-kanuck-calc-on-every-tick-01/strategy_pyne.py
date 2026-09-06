"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe kanuck-probe-02-calc-on-every-tick", shorttitle="PF_kan02_TICK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, calc_on_every_tick=True)
def main(
    i_step=input.int(3, "Tick-counter modulo step", minval=1),
    i_fast=input.int(8, "EMA fast length", minval=2),
    i_slow=input.int(21, "EMA slow length", minval=3)
):

    tick_counter: Persistent[int] = 0
    tick_counter += 1

    fast: float = ta.ema(close, i_fast)
    slow: float = ta.ema(close, i_slow)

    cross_up: bool = ta.crossover(fast, slow)
    cross_down: bool = ta.crossunder(fast, slow)

    gate: bool = tick_counter % i_step == 0

    if cross_up and gate and (strategy.position_size <= 0):
        strategy.entry('L', strategy.long, qty=1, comment='tick gated long')

    if cross_down and gate and (strategy.position_size >= 0):
        strategy.entry('S', strategy.short, qty=1, comment='tick gated short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
