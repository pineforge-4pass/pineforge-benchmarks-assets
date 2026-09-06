"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe 4ema-rsi-probe-integration", shorttitle="PF_4emaINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_xs=input.int(8, "EMA xs length", minval=2),
    i_s=input.int(21, "EMA s length", minval=3),
    i_m=input.int(55, "EMA m length", minval=5),
    i_l=input.int(200, "EMA l length", minval=10),
    i_rsi_len=input.int(14, "RSI length", minval=2),
    i_dip_lo=input.float(48, "Long pullback band", minval=10, maxval=50),
    i_pop_lo=input.float(52, "Long recovery line", minval=40, maxval=70),
    i_dip_hi=input.float(52, "Short pullback band", minval=50, maxval=90),
    i_pop_hi=input.float(48, "Short recovery line", minval=30, maxval=60),
    i_expiry_bars=input.int(8, "Forced exit after N bars", minval=1)
):

    ema_xs: float = ta.ema(close, i_xs)
    ema_s: float = ta.ema(close, i_s)
    ema_m: float = ta.ema(close, i_m)
    ema_l: float = ta.ema(close, i_l)

    stack_bull: bool = ema_xs > ema_s and ema_s > ema_m and (ema_m > ema_l)
    stack_bear: bool = ema_xs < ema_s and ema_s < ema_m and (ema_m < ema_l)

    r: float = ta.rsi(close, i_rsi_len)

    long_armed: Persistent[bool] = False
    short_armed: Persistent[bool] = False

    if r < i_dip_lo:
        long_armed = True
    if r > i_dip_hi:
        short_armed = True

    long_fire: bool = long_armed and ta.crossover(r, i_pop_lo)
    short_fire: bool = short_armed and ta.crossunder(r, i_pop_hi)

    if long_fire:
        long_armed = False
    if short_fire:
        short_armed = False

    go_long: bool = stack_bull and long_fire
    go_short: bool = stack_bear and short_fire

    bars_in_trade: Persistent[int] = 0
    if strategy.position_size != 0:
        bars_in_trade += 1
    else:
        bars_in_trade = 0

    expiry_due: bool = strategy.position_size != 0 and bars_in_trade >= i_expiry_bars

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ long')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ short')

    if expiry_due:
        strategy.close_all(comment='integ bar expiry')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
