"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import input, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe 104 - supertrend flip", shorttitle="PF_p104_ST", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_factor=input.float(3.0, "Supertrend factor", minval=0.5, maxval=10.0, step=0.1),
    i_atr_len=input.int(10, "Supertrend ATR length", minval=2, maxval=100)
):

    st_trail, st_dir = ta.supertrend(i_factor, i_atr_len)

    prev_dir: Persistent[float] = 0.0
    bull_flip: bool = st_dir == -1 and prev_dir == 1
    bear_flip: bool = st_dir == 1 and prev_dir == -1

    if bull_flip and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='st bull flip')

    if bear_flip and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='st bear flip')

    prev_dir = st_dir


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
