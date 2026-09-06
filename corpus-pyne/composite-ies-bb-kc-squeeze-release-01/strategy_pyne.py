"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF IES probe 05 - bb/kc squeeze", shorttitle="IES_p05_SQZ", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_bb_len=input.int(20, "BB Length", minval=10, maxval=50),
    i_bb_mult=input.float(2.0, "BB Mult", minval=1.0, maxval=3.0, step=0.1),
    i_kc_len=input.int(20, "KC Length", minval=10, maxval=50),
    i_kc_mult=input.float(1.5, "KC Mult", minval=1.0, maxval=3.0, step=0.1)
):

    bb_basis: float = ta.sma(close, i_bb_len)
    bb_dev: float = ta.stdev(close, i_bb_len) * i_bb_mult
    bb_upper: float = bb_basis + bb_dev
    bb_lower: float = bb_basis - bb_dev

    kc_basis: float = ta.ema(close, i_kc_len)
    kc_range: float = ta.atr(i_kc_len) * i_kc_mult
    kc_upper: float = kc_basis + kc_range
    kc_lower: float = kc_basis - kc_range

    squeeze_on: Series[bool] = bb_lower > kc_lower and bb_upper < kc_upper
    squeeze_release: bool = squeeze_on[1] and (not squeeze_on)

    if squeeze_release and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='squeeze release')

    if ta.crossunder(close, kc_basis) and strategy.position_size > 0:
        strategy.close('L', comment='kc basis lost')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
