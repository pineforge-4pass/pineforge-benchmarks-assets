"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF probe 4ema-rsi-probe-01-quad-ema-stack", shorttitle="PF_4ema01_STK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_xs=input.int(8, "EMA xs length", minval=2),
    i_s=input.int(21, "EMA s length", minval=3),
    i_m=input.int(55, "EMA m length", minval=5),
    i_l=input.int(200, "EMA l length", minval=10)
):

    ema_xs: float = ta.ema(close, i_xs)
    ema_s: float = ta.ema(close, i_s)
    ema_m: float = ta.ema(close, i_m)
    ema_l: float = ta.ema(close, i_l)

    stack_bull: Series[bool] = ema_xs > ema_s and ema_s > ema_m and (ema_m > ema_l)

    stack_bear: Series[bool] = ema_xs < ema_s and ema_s < ema_m and (ema_m < ema_l)

    bull_edge: bool = stack_bull and (not stack_bull[1])
    bear_edge: bool = stack_bear and (not stack_bear[1])

    if bull_edge and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='stack bull edge')

    if bear_edge and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='stack bear edge')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
