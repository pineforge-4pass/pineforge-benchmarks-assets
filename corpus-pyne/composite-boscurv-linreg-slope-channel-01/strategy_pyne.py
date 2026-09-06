"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("PF probe bos-curv-probe-02-curved-channel", shorttitle="PF_bos02_CRV", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_lr_len=input.int(50, "Linreg length", minval=10),
    i_atr_len=input.int(14, "ATR length", minval=2),
    i_atr_mult=input.float(2.0, "ATR multiplier", minval=0.1, step=0.1),
    i_curve_offset=input.float(5.0, "Slope curve offset", step=0.5)
):

    mid: float = ta.linreg(close, i_lr_len, 0)
    lr_lag: float = ta.linreg(close, i_lr_len, 1)
    slope: float = mid - lr_lag

    width: float = ta.atr(i_atr_len) * i_atr_mult

    upper: float = mid + width + slope * i_curve_offset
    lower: float = mid - width + slope * i_curve_offset

    cross_up: bool = ta.crossover(close, upper)
    cross_down: bool = ta.crossunder(close, lower)

    if cross_up and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='curve cross up')

    if cross_down and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='curve cross down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
