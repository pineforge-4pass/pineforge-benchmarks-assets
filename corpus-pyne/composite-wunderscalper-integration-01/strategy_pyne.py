"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, close, input, script, strategy, ta


@script.strategy("PF probe wunder-scalper-probe-integration", shorttitle="PF_WSINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast=input.int(5, "Fast EMA", minval=2, maxval=50),
    i_slow=input.int(13, "Slow EMA", minval=3, maxval=100)
):

    ema_fast: float = ta.ema(close, i_fast)
    ema_slow: float = ta.ema(close, i_slow)

    long_signal: bool = ta.crossover(ema_fast, ema_slow)
    short_signal: bool = ta.crossunder(ema_fast, ema_slow)

    if long_signal:
        if strategy.position_size < 0:
            strategy.close_all(comment='integ reverse close short')
        strategy.entry('L', strategy.long, qty=1, comment='integ open long')
        alert('{{strategy.order.action}} {{ticker}} long', alert.freq_once_per_bar)

    if short_signal:
        if strategy.position_size > 0:
            strategy.close_all(comment='integ reverse close long')
        strategy.entry('S', strategy.short, qty=1, comment='integ open short')
        alert('{{strategy.order.action}} {{ticker}} short', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
