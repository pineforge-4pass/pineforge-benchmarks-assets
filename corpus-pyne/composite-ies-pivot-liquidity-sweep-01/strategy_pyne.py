"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF IES probe 06 - pivot sweep", shorttitle="IES_p06_SWP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_swing_left=input.int(10, "Swing Left Bars", minval=3, maxval=30),
    i_swing_right=input.int(5, "Swing Right Bars", minval=2, maxval=15)
):

    swing_high: float = ta.pivothigh(high, i_swing_left, i_swing_right)
    swing_low: float = ta.pivotlow(low, i_swing_left, i_swing_right)

    last_swing_high: Persistent[float] = na(float)
    last_swing_low: Persistent[float] = na(float)

    if not na(swing_high):
        last_swing_high = swing_high
    if not na(swing_low):
        last_swing_low = swing_low

    sweep_high: bool = not na(last_swing_high) and high > last_swing_high and (close < last_swing_high)
    sweep_low: bool = not na(last_swing_low) and low < last_swing_low and (close > last_swing_low)

    if sweep_low and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip')
        strategy.entry('L', strategy.long, qty=1, comment='sweep low → long')

    if sweep_high and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip')
        strategy.entry('S', strategy.short, qty=1, comment='sweep high → short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
