"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, input, low, math, open, plot, script,
    strategy, ta
)
from pynecore.types import Series


@script.strategy("Candlestick Patterns", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    trendLen=input.int(20, "Trend MA Length", minval=5)
):

    trendMA = ta.sma(close, trendLen)
    upTrend = close > trendMA
    dnTrend = close < trendMA

    bodySize: Series = math.abs(close - open)
    upperWick = high - math.max(open, close)
    lowerWick = math.min(open, close) - low
    totalRange = high - low

    bullEngulf = close > open and close[1] < open[1] and (close > open[1]) and (open < close[1])

    bearEngulf = close < open and close[1] > open[1] and (close < open[1]) and (open > close[1])

    hammer = lowerWick > bodySize * 2 and upperWick < bodySize * 0.5 and (bodySize > 0)

    shootStar = upperWick > bodySize * 2 and lowerWick < bodySize * 0.5 and (bodySize > 0)

    doji = bodySize < totalRange * 0.1 and totalRange > 0

    morningStar = close[2] < open[2] and bodySize[1] < bodySize[2] * 0.3 and (close > open) and (close > (open[2] + close[2]) / 2)

    bullSignal = (bullEngulf or hammer or morningStar) and dnTrend
    bearSignal = (bearEngulf or shootStar) and upTrend

    if bullSignal:
        strategy.entry('Long', strategy.long)
    if bearSignal:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and bearSignal:
        strategy.close('Long')
    if strategy.position_size < 0 and bullSignal:
        strategy.close('Short')

    plot(trendMA, 'Trend MA', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
