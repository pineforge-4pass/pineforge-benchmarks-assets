"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import array, close, color, display, input, math, plot, script, strategy, ta
from pynecore.types import Persistent, Series


@script.strategy("PineForge — Spectrum Array Deque", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    sampleCount=input.int(17, "Deque Samples", minval=4, maxval=60, group="Breadth"),
    minimumPositiveShare=input.float(0.64, "Minimum Positive Share", minval=0.1, maxval=0.95, step=0.01, group="Breadth"),
    trendLength=input.int(49, "Trend EMA Length", minval=5, group="Trend"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    returnDeque: Persistent[list[float]] = array.new_float()
    array.push(returnDeque, ta.roc(close, 1))
    if array.size(returnDeque) > sampleCount:
        array.shift(returnDeque)

    returnSum: float = 0.0
    positiveCount: int = 0
    for sample in returnDeque:
        returnSum += sample
        if sample > 0:
            positiveCount += 1

    sampleSize = math.max(array.size(returnDeque), 1)
    positiveShare: Series = positiveCount / sampleSize
    averageReturn = returnSum / sampleSize
    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)

    enterLong = positiveShare >= minimumPositiveShare and averageReturn > 0 and (close > trendLine) and (positiveShare[1] < minimumPositiveShare)
    breadthEnded = positiveShare < 0.46 or averageReturn < 0 or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Spectrum Long', strategy.long)
    elif strategy.position_size > 0 and (breadthEnded or riskExceeded):
        strategy.close('Spectrum Long', comment='ATR risk' if riskExceeded else 'Breadth ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(positiveShare, 'Positive Share', color=color.blue, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
