"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Switchback All-In Reversal", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=50, margin_short=50, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(31, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(97, "Slow EMA", minval=3, group="Signal")
):
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)

    turnLong = ta.crossover(fastEma, slowEma)
    turnShort = ta.crossunder(fastEma, slowEma)

    if turnLong:
        strategy.entry('Switchback Long', strategy.long)
        strategy.close('Switchback Short', comment='Atomic prior-side close')

    if turnShort:
        strategy.entry('Switchback Short', strategy.short)
        strategy.close('Switchback Long', comment='Atomic prior-side close')

    plot(fastEma, 'Fast EMA', color=color.aqua)
    plot(slowEma, 'Slow EMA', color=color.fuchsia)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
