"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("PF probe 100 - dual sma cross", shorttitle="PF_p100_DSMA", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast=input.int(9, "Fast SMA length", minval=2, maxval=100),
    i_slow=input.int(21, "Slow SMA length", minval=3, maxval=200)
):

    fast_ma: float = ta.sma(close, i_fast)
    slow_ma: float = ta.sma(close, i_slow)

    golden_cross: bool = ta.crossover(fast_ma, slow_ma)
    death_cross: bool = ta.crossunder(fast_ma, slow_ma)

    if golden_cross and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='golden cross')

    if death_cross and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='death cross')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
