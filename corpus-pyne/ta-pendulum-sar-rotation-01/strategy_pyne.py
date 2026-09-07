"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Pendulum SAR Rotation", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    sarStart=input.float(0.018, "SAR Start", minval=0.001, maxval=0.2, step=0.001, group="Signal"),
    sarIncrement=input.float(0.021, "SAR Increment", minval=0.001, maxval=0.2, step=0.001, group="Signal"),
    sarMaximum=input.float(0.19, "SAR Maximum", minval=0.01, maxval=1.0, step=0.01, group="Signal"),
    trendLength=input.int(73, "Trend EMA Length", minval=5, group="Signal"),
    maximumHoldBars=input.int(96, "Maximum Hold Bars", minval=8, group="Risk")
):
    sarLine = ta.sar(sarStart, sarIncrement, sarMaximum)
    trendLine = ta.ema(close, trendLength)
    enterLong = ta.crossover(close, sarLine) and close > trendLine

    entryBar: Persistent[int] = na(int)
    if strategy.position_size == 0 and enterLong:
        strategy.entry('Pendulum Long', strategy.long)
        entryBar = bar_index

    ageExceeded = strategy.position_size > 0 and (not na(entryBar)) and (bar_index - entryBar >= maximumHoldBars)
    rotationEnded = strategy.position_size > 0 and (ta.crossunder(close, sarLine) or close < trendLine)
    if rotationEnded or ageExceeded:
        strategy.close('Pendulum Long', comment='Age guard' if ageExceeded else 'SAR rotation')

    if strategy.position_size == 0 and strategy.position_size[1] > 0:
        entryBar = na

    plot(sarLine, 'Parabolic SAR', color=color.purple, style=plot.style_cross)
    plot(trendLine, 'Trend EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
