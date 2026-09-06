"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe trendmaster-probe-02-multi-tier-ma", shorttitle="PF_TM02_STACK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast=input.int(21, "EMA fast", minval=3, maxval=100),
    i_mid=input.int(55, "EMA mid", minval=10, maxval=200),
    i_slow=input.int(200, "EMA slow", minval=50, maxval=500)
):

    ema_fast: float = ta.ema(close, i_fast)
    ema_mid: float = ta.ema(close, i_mid)
    ema_slow: float = ta.ema(close, i_slow)

    stack_bull: bool = ema_fast > ema_mid and ema_mid > ema_slow
    stack_bear: bool = ema_fast < ema_mid and ema_mid < ema_slow

    stack_state: Persistent[int] = 0
    prev_state: Persistent[int] = 0

    if stack_bull:
        stack_state = 1
    elif stack_bear:
        stack_state = -1
    else:
        stack_state = 0

    long_edge: bool = stack_state == 1 and prev_state != 1
    short_edge: bool = stack_state == -1 and prev_state != -1

    if long_edge and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='stack bull edge')

    if short_edge and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='stack bear edge')

    prev_state = stack_state


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
