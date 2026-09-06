"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF probe market-shift-probe-02-rolling-extreme", shorttitle="PF_MS02_ROLL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_window=input.int(50, "Rolling window length", minval=10, maxval=200)
):

    roll_hi: Series[float] = ta.highest(high, i_window)
    roll_lo: Series[float] = ta.lowest(low, i_window)

    ref_hi: float = roll_hi[1]
    ref_lo: float = roll_lo[1]

    long_signal: bool = ta.crossover(close, ref_lo)
    short_signal: bool = ta.crossunder(close, ref_hi)

    if long_signal and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='rebound long')

    if short_signal and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='rebound short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
