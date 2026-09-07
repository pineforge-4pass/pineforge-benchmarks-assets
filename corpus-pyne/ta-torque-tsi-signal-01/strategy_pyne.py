"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hline, input, plot, script, strategy, ta


@script.strategy("PineForge — Torque TSI Signal", overlay=False, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    shortLength=input.int(14, "TSI Short Length", minval=2, group="Signal"),
    longLength=input.int(29, "TSI Long Length", minval=3, group="Signal"),
    signalLength=input.int(9, "RMA Signal Length", minval=2, group="Signal"),
    trendLength=input.int(68, "Trend EMA Length", minval=5, group="Signal"),
    minimumStrength=input.float(0.0, "Minimum TSI Strength", minval=-1.0, maxval=1.0, step=0.01, group="Signal")
):
    strength = ta.tsi(close, shortLength, longLength)
    strengthSignal = ta.rma(strength, signalLength)
    trendLine = ta.ema(close, trendLength)

    enterLong = ta.crossover(strength, strengthSignal) and strength > minimumStrength and (close > trendLine)
    momentumEnded = ta.crossunder(strength, strengthSignal)
    regimeEnded = close < trendLine

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Torque Long', strategy.long)
    elif strategy.position_size > 0 and (momentumEnded or regimeEnded):
        strategy.close('Torque Long', comment='Momentum ended' if momentumEnded else 'Regime ended')

    plot(strength, 'True Strength Index', color=color.blue)
    plot(strengthSignal, 'RMA Signal', color=color.orange)
    hline(minimumStrength, 'Minimum Strength', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
