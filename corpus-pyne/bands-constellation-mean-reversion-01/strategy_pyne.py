"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Constellation Bands", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    bandLength=input.int(31, "Band Length", minval=5, group="Signal"),
    bandWidth=input.float(2.15, "Band Width", minval=0.5, step=0.05, group="Signal"),
    stopDeviation=input.float(1.35, "Stop Deviation", minval=0.5, step=0.05, group="Risk"),
    targetFraction=input.float(0.85, "Target Toward Basis", minval=0.2, maxval=1.2, step=0.05, group="Risk")
):
    basis, upperBand, lowerBand = ta.bb(close, bandLength, bandWidth)
    deviation = ta.stdev(close, bandLength)
    reentry = ta.crossover(close, lowerBand)

    if reentry and close < basis:
        strategy.entry('Constellation Long', strategy.long)
    if strategy.position_size > 0:
        target = strategy.position_avg_price + (basis - strategy.position_avg_price) * targetFraction
        stopPrice = strategy.position_avg_price - deviation * stopDeviation
        strategy.exit('Constellation Risk', from_entry='Constellation Long', stop=stopPrice, limit=target)

    plot(basis, 'Band Basis', color=color.gray)
    plot(upperBand, 'Upper Band', color=color.purple)
    plot(lowerBand, 'Lower Band', color=color.purple)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
