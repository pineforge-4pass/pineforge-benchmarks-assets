"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import array, close, color, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Atlas Array Rotation", overlay=False, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=7, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    sampleCount=input.int(8, "Return Samples", minval=3, maxval=30, group="Signal"),
    rankLength=input.int(55, "Rank Window", minval=10, group="Signal"),
    rsiLength=input.int(14, "RSI Length", minval=2, group="Signal"),
    entryRank=input.float(78.0, "Entry Rank", minval=50, maxval=99, group="Signal"),
    exitRank=input.float(46.0, "Exit Rank", minval=1, maxval=70, group="Signal"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.4, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    returns: Persistent[list[float]] = array.new_float()
    oneBarReturn = 0.0 if na(close[1]) else 100.0 * (close / close[1] - 1.0)
    array.push(returns, oneBarReturn)
    if array.size(returns) > sampleCount:
        array.shift(returns)

    rollingImpulse = array.avg(returns) if array.size(returns) == sampleCount else na
    priceRank = ta.percentrank(close, rankLength)
    rsiValue = ta.rsi(close, rsiLength)
    atrValue = ta.atr(atrLength)

    enterLong = ta.crossover(priceRank, entryRank) and rollingImpulse > 0 and (rsiValue > 54)
    leaveLong = ta.crossunder(priceRank, exitRank) or rollingImpulse < 0 or rsiValue < 44

    if enterLong:
        strategy.entry('Atlas Long', strategy.long)
    if strategy.position_size > 0 and leaveLong:
        strategy.close('Atlas Long', comment='Momentum rank cooled')
    if strategy.position_size > 0:
        strategy.exit('Atlas Guard', from_entry='Atlas Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(priceRank, 'Price Percent Rank', color=color.blue)
    plot(rollingImpulse, 'Array Mean Return', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
