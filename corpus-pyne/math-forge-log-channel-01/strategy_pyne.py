"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, color, high, input, low, math, plot, script, strategy, ta


@script.strategy("PineForge — Forge Loop Channel", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    channelLength=input.int(24, "Channel Length", minval=5, maxval=80, group="Signal"),
    logBuffer=input.float(0.18, "Log Buffer Multiplier", minval=0, step=0.02, group="Signal"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.3, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    channelHigh: float = high[1]
    channelLow: float = low[1]
    logMovement: float = 0.0
    for offset in pine_range(2, channelLength):
        channelHigh = math.max(channelHigh, high[offset])
        channelLow = math.min(channelLow, low[offset])
        logMovement += math.abs(math.log(close[offset - 1] / close[offset]))

    averageLogMove = logMovement / math.max(channelLength - 1, 1)
    upperTrigger = channelHigh * (1.0 + averageLogMove * logBuffer)
    lowerTrigger = channelLow * (1.0 - averageLogMove * logBuffer)
    atrValue = ta.atr(atrLength)

    if ta.crossover(close, upperTrigger):
        strategy.entry('Forge Long', strategy.long)
    if ta.crossunder(close, lowerTrigger):
        strategy.entry('Forge Short', strategy.short)

    if strategy.position_size > 0:
        strategy.exit('Forge Long Guard', from_entry='Forge Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    if strategy.position_size < 0:
        strategy.exit('Forge Short Guard', from_entry='Forge Short', stop=strategy.position_avg_price + atrValue * stopAtr)

    plot(upperTrigger, 'Adaptive Upper', color=color.green)
    plot(lowerTrigger, 'Adaptive Lower', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
