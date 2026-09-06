"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("PF probe kkb-probe-03-margin-100-pct", shorttitle="PF_kkb03_MGN", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, margin_long=100, margin_short=100)
def main(
    i_fast=input.int(5, "Fast SMA length", minval=2),
    i_slow=input.int(20, "Slow SMA length", minval=3)
):

    fast: float = ta.sma(close, i_fast)
    slow: float = ta.sma(close, i_slow)

    cross_up: bool = ta.crossover(fast, slow)
    cross_down: bool = ta.crossunder(fast, slow)

    if cross_up and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='ma cross up')

    if cross_down and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='ma cross down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
