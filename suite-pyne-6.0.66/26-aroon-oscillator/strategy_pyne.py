"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, high, input, low, plot, script, strategy, ta


@script.strategy("Highest Lowest Breakout", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    lookback=input.int(20, "Lookback", minval=5)
):

    barsToHigh = ta.highestbars(high, lookback)
    barsToLow = ta.lowestbars(low, lookback)
    hh = ta.highest(high, lookback)
    ll = ta.lowest(low, lookback)

    newHigh = barsToHigh == 0
    newLow = barsToLow == 0

    maVal = ta.ema(close, 50)

    longCond = newHigh and close > maVal
    shortCond = newLow and close < maVal

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    midChan = (hh + ll) / 2
    if strategy.position_size > 0 and close < midChan:
        strategy.close('Long')
    if strategy.position_size < 0 and close > midChan:
        strategy.close('Short')

    plot(hh, 'Highest', color=color.green)
    plot(ll, 'Lowest', color=color.red)
    plot(midChan, 'Mid', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
