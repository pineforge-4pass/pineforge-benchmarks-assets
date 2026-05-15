"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, script, strategy, ta


@script.strategy("PF probe scalping-probe-02-fast-ma-trigger", shorttitle="PF_SC02_MA", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast=input.int(5, "Fast EMA", minval=2, maxval=50),
    i_slow=input.int(13, "Slow EMA", minval=3, maxval=100)
):

    ema_fast: float = ta.ema(close, i_fast)
    ema_slow: float = ta.ema(close, i_slow)

    long_signal: bool = ta.crossover(ema_fast, ema_slow)
    short_signal: bool = ta.crossunder(ema_fast, ema_slow)

    if long_signal:
        strategy.entry('L', strategy.long, qty=1, comment='ma flip long')

    if short_signal:
        strategy.entry('S', strategy.short, qty=1, comment='ma flip short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
