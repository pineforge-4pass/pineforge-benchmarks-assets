"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("PF probe 99 - keltner channel break", shorttitle="PF_p99_KCH", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_ema_len=input.int(20, "Channel EMA length", minval=2, maxval=200),
    i_atr_len=input.int(10, "Channel ATR length", minval=2, maxval=100),
    i_mult=input.float(2.0, "Channel multiple", minval=0.5, maxval=10.0, step=0.1)
):

    mid_line: float = ta.ema(close, i_ema_len)
    half_w: float = ta.atr(i_atr_len) * i_mult
    upper: float = mid_line + half_w
    lower: float = mid_line - half_w

    long_break: bool = ta.crossover(close, upper)
    short_break: bool = ta.crossunder(close, lower)
    long_exit: bool = ta.crossunder(close, mid_line)
    short_exit: bool = ta.crossover(close, mid_line)

    if long_break and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='upper break')

    if short_break and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='lower break')

    if long_exit and strategy.position_size > 0:
        strategy.close('L', comment='back to mid')

    if short_exit and strategy.position_size < 0:
        strategy.close('S', comment='back to mid')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
