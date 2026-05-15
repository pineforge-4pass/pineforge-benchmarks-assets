"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, high, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Liquidity Sweep + Market Structure Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    lookback=input.int(20, "Liquidity Lookback"),
    structureLen=input.int(5, "Structure Length"),
    atrLen=input.int(14, "ATR Length"),
    atrMult=input.float(1.5, "Stop ATR Multiplier"),
    rr=input.float(2.0, "Risk Reward")
):

    recentHigh = ta.highest(high[1], lookback)
    recentLow = ta.lowest(low[1], lookback)

    sweepHigh: Series = high > recentHigh and close < recentHigh
    sweepLow: Series = low < recentLow and close > recentLow

    structureHigh: Series = ta.highest(high, structureLen)
    structureLow: Series = ta.lowest(low, structureLen)

    bullStructureBreak = close > structureHigh[1]
    bearStructureBreak = close < structureLow[1]

    longCondition = sweepLow[1] and bullStructureBreak
    shortCondition = sweepHigh[1] and bearStructureBreak

    atrValue = ta.atr(atrLen)

    if longCondition and strategy.position_size == 0:
        strategy.entry('Long', strategy.long)

    if shortCondition and strategy.position_size == 0:
        strategy.entry('Short', strategy.short)

    longStop = strategy.position_avg_price - atrValue * atrMult
    longTake = strategy.position_avg_price + atrValue * atrMult * rr

    shortStop = strategy.position_avg_price + atrValue * atrMult
    shortTake = strategy.position_avg_price - atrValue * atrMult * rr

    strategy.exit('Exit Long', from_entry='Long', stop=longStop, limit=longTake)
    strategy.exit('Exit Short', from_entry='Short', stop=shortStop, limit=shortTake)

    plot(recentHigh, title='Liquidity High', color=color.red)
    plot(recentLow, title='Liquidity Low', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)