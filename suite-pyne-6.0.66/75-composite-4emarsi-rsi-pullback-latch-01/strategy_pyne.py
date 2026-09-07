"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF probe 4ema-rsi-probe-02-rsi-pullback", shorttitle="PF_4ema02_RSI", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_rsi_len=input.int(14, "RSI length", minval=2),
    i_dip_lo=input.float(40, "Long pullback band", minval=10, maxval=50),
    i_pop_lo=input.float(50, "Long recovery line", minval=40, maxval=60),
    i_dip_hi=input.float(60, "Short pullback band", minval=50, maxval=90),
    i_pop_hi=input.float(50, "Short recovery line", minval=40, maxval=60)
):

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

    if long_fire and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='rsi pullback long')

    if short_fire and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='rsi pullback short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
