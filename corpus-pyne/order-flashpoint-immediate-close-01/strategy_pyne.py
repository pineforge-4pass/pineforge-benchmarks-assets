"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta


@script.strategy("PineForge — Flashpoint Immediate Close", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    trendLength=input.int(47, "Trend EMA Length", minval=5, group="Signal"),
    momentumLength=input.int(12, "Momentum ROC Length", minval=2, group="Signal"),
    entryMomentum=input.float(0.6, "Entry Momentum %", minval=0.1, step=0.1, group="Signal"),
    shockThreshold=input.float(-2.4, "Immediate Shock %", maxval=-0.2, step=0.1, group="Risk")
):
    trendLine = ta.ema(close, trendLength)
    momentum = ta.roc(close, momentumLength)
    oneBarReturn = ta.roc(close, 1)

    enterLong = ta.crossover(momentum, entryMomentum) and close > trendLine
    ordinaryExit = strategy.position_size > 0 and close < trendLine
    flashpoint = strategy.position_size > 0 and oneBarReturn <= shockThreshold

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Flashpoint Long', strategy.long)
    elif flashpoint:
        strategy.close('Flashpoint Long', comment='Immediate shock', immediately=True)
    elif ordinaryExit:
        strategy.close('Flashpoint Long', comment='Trend ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(oneBarReturn, 'One-Bar Return %', color=color.red, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
