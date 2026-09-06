"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, nz, script, strategy, ta
from pynecore.types import PersistentSeries


@script.strategy("PF probe bos-curv-probe-integration", shorttitle="PF_bosINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_left=input.int(5, "Pivot left bars", minval=1),
    i_right=input.int(5, "Pivot right bars", minval=1),
    i_lr_len=input.int(50, "Linreg length", minval=10),
    i_atr_len=input.int(14, "ATR length", minval=2),
    i_atr_mult=input.float(2.0, "ATR multiplier", minval=0.1, step=0.1),
    i_curve_offset=input.float(5.0, "Slope curve offset", step=0.5)
):

    ph: float = ta.pivothigh(high, i_left, i_right)
    pl: float = ta.pivotlow(low, i_left, i_right)

    last_ph: PersistentSeries[float] = na(float)
    last_pl: PersistentSeries[float] = na(float)

    if not na(ph):
        last_ph = ph
    if not na(pl):
        last_pl = pl

    bos_long: bool = not na(last_ph) and close > last_ph and (close[1] <= nz(last_ph[1], last_ph))
    bos_short: bool = not na(last_pl) and close < last_pl and (close[1] >= nz(last_pl[1], last_pl))

    mid: float = ta.linreg(close, i_lr_len, 0)
    lr_lag: float = ta.linreg(close, i_lr_len, 1)
    slope: float = mid - lr_lag
    width: float = ta.atr(i_atr_len) * i_atr_mult
    upper: float = mid + width + slope * i_curve_offset
    lower: float = mid - width + slope * i_curve_offset

    channel_bull: bool = close > mid + slope * i_curve_offset
    channel_bear: bool = close < mid + slope * i_curve_offset

    go_long: bool = bos_long and channel_bull
    go_short: bool = bos_short and channel_bear

    exit_long: bool = strategy.position_size > 0 and ta.crossunder(close, lower)
    exit_short: bool = strategy.position_size < 0 and ta.crossover(close, upper)

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ long')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ short')

    if exit_long:
        strategy.close('L', comment='integ exit long')
    if exit_short:
        strategy.close('S', comment='integ exit short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
