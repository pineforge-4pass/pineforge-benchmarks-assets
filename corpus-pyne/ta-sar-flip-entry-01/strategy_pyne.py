"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF probe 101 - parabolic sar flip", shorttitle="PF_p101_SAR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_start=input.float(0.02, "SAR start", minval=0.001, maxval=1.0, step=0.01),
    i_inc=input.float(0.02, "SAR increment", minval=0.001, maxval=1.0, step=0.01),
    i_max=input.float(0.2, "SAR max AF", minval=0.01, maxval=1.0, step=0.01)
):

    sar_val: Series[float] = ta.sar(i_start, i_inc, i_max)

    sar_below_now: bool = sar_val < close
    sar_below_prior: bool = sar_val[1] < close[1]

    bull_flip: bool = sar_below_now and (not sar_below_prior)
    bear_flip: bool = not sar_below_now and sar_below_prior

    if bull_flip and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='sar bull flip')

    if bear_flip and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='sar bear flip')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
