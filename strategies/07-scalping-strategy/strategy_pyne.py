"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, input, low, math, open, plot, script,
    strategy, ta
)


@script.strategy("Scalping Strategy Improved v2", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    emaFast=input.int(50),
    emaSlow=input.int(200),
    rsiLen=input.int(3),
    rsiOB=input.int(80),
    rsiOS=input.int(20),
    adxLen=input.int(5),
    adxLevel=input.int(20),
    atrLen=input.int(14),
    atrMult=input.float(1.2)
):

    ema50 = ta.ema(close, emaFast)
    ema200 = ta.ema(close, emaSlow)

    rsi = ta.rsi(close, rsiLen)

    diplus, diminus, adx = ta.dmi(adxLen, adxLen)

    atr = ta.atr(atrLen)

    body = math.abs(close - open)
    candleRange = high - low
    strongBull = close > open and body > candleRange * 0.5
    strongBear = close < open and body > candleRange * 0.5

    trendLong = close > ema50 and ema50 > ema200
    trendShort = close < ema50 and ema50 < ema200

    rsiLong = ta.crossover(rsi, rsiOS)
    rsiShort = ta.crossunder(rsi, rsiOB)

    trendStrength = adx > adxLevel

    longCondition = trendLong and rsiLong and trendStrength and strongBull
    shortCondition = trendShort and rsiShort and trendStrength and strongBear

    longStop = close - atr * atrMult
    shortStop = close + atr * atrMult

    longTP = close + (close - longStop) * 2
    shortTP = close - (shortStop - close) * 2

    if longCondition:
        strategy.entry('BUY', strategy.long)
        strategy.exit('TP/SL BUY', 'BUY', stop=longStop, limit=longTP, trail_points=atr)

    if shortCondition:
        strategy.entry('SELL', strategy.short)
        strategy.exit('TP/SL SELL', 'SELL', stop=shortStop, limit=shortTP, trail_points=atr)

    plot(ema50, color=color.orange, linewidth=2)
    plot(ema200, color=color.blue, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)