"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, na, nz, script, strategy, ta
from pynecore.types import PersistentSeries


@script.strategy("PF probe kkb-probe-integration", shorttitle="PF_kkbINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, margin_long=100, margin_short=100)
def main(
    i_q=input.float(0.001, "Process variance Q", minval=0.0, step=0.0005),
    i_r=input.float(0.1, "Measurement variance R", minval=0.0001, step=0.01),
    i_band_len=input.int(20, "Band EMA length", minval=2),
    i_atr_len=input.int(14, "ATR length", minval=2),
    i_atr_mult=input.float(1.5, "ATR multiplier", minval=0.1, step=0.1)
):

    x: PersistentSeries[float] = na(float)
    p: PersistentSeries[float] = 1.0

    x_pred: float = nz(x[1], close)
    p_pred: float = nz(p[1], 1.0) + i_q
    k_gain: float = p_pred / (p_pred + i_r)
    x = x_pred + k_gain * (close - x_pred)
    p = (1 - k_gain) * p_pred

    kalman_bull: bool = x > nz(x[1], x)
    kalman_bear: bool = x < nz(x[1], x)

    band: float = ta.ema(close, i_band_len)
    vol: float = ta.atr(i_atr_len)
    upper: float = band + vol * i_atr_mult
    lower: float = band - vol * i_atr_mult

    break_up: bool = ta.crossover(close, upper)
    break_down: bool = ta.crossunder(close, lower)

    go_long: bool = kalman_bull and break_up
    go_short: bool = kalman_bear and break_down

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ long')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
