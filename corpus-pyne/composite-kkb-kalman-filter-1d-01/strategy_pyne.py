"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, na, nz, script, strategy, ta
from pynecore.types import PersistentSeries


@script.strategy("PF probe kkb-probe-01-kalman-filter", shorttitle="PF_kkb01_KAL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_q=input.float(0.001, "Process variance Q", minval=0.0, step=0.0005),
    i_r=input.float(0.1, "Measurement variance R", minval=0.0001, step=0.01)
):

    x: PersistentSeries[float] = na(float)
    p: PersistentSeries[float] = 1.0

    x_pred: float = nz(x[1], close)
    p_pred: float = nz(p[1], 1.0) + i_q
    k_gain: float = p_pred / (p_pred + i_r)
    x = x_pred + k_gain * (close - x_pred)
    p = (1 - k_gain) * p_pred

    cross_up: bool = ta.crossover(close, x)
    cross_down: bool = ta.crossunder(close, x)

    if cross_up and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='kalman cross up')

    if cross_down and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='kalman cross down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
