"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, na, plot, script, strategy, ta, timeframe


@script.strategy("PineForge — Dial Main Period", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fiveFast=input.int(43, "5m Fast EMA", minval=2, group="Adaptation"),
    fiveSlow=input.int(96, "5m Slow EMA", minval=5, group="Adaptation"),
    fifteenFast=input.int(20, "15m Fast EMA", minval=2, group="Adaptation"),
    fifteenSlow=input.int(44, "15m Slow EMA", minval=5, group="Adaptation"),
    hourFast=input.int(11, "60m Fast EMA", minval=2, group="Adaptation"),
    hourSlow=input.int(24, "60m Slow EMA", minval=5, group="Adaptation"),
    fourHourFast=input.int(6, "240m Fast EMA", minval=2, group="Adaptation"),
    fourHourSlow=input.int(14, "240m Slow EMA", minval=5, group="Adaptation"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    fast5 = ta.ema(close, fiveFast)
    slow5 = ta.ema(close, fiveSlow)
    fast15 = ta.ema(close, fifteenFast)
    slow15 = ta.ema(close, fifteenSlow)
    fast60 = ta.ema(close, hourFast)
    slow60 = ta.ema(close, hourSlow)
    fast240 = ta.ema(close, fourHourFast)
    slow240 = ta.ema(close, fourHourSlow)

    __block_result__ = na
    __switch__ = timeframe.main_period
    if __switch__ == "5":
        __block_result__ = fast5
    elif __switch__ == "15":
        __block_result__ = fast15
    elif __switch__ == "60":
        __block_result__ = fast60
    elif __switch__ == "240":
        __block_result__ = fast240
    else:
        __block_result__ = fast15
    fastLine = __block_result__
    __block_result__ = na
    __switch__ = timeframe.main_period
    if __switch__ == "5":
        __block_result__ = slow5
    elif __switch__ == "15":
        __block_result__ = slow15
    elif __switch__ == "60":
        __block_result__ = slow60
    elif __switch__ == "240":
        __block_result__ = slow240
    else:
        __block_result__ = slow15
    slowLine = __block_result__
    __block_result__ = na
    __switch__ = timeframe.main_period
    if __switch__ == "5":
        __block_result__ = fiveSlow
    elif __switch__ == "15":
        __block_result__ = fifteenSlow
    elif __switch__ == "60":
        __block_result__ = hourSlow
    elif __switch__ == "240":
        __block_result__ = fourHourSlow
    else:
        __block_result__ = fifteenSlow
    selectedSlowLength = __block_result__
    atrValue = ta.atr(atrLength)
    enterLong = ta.crossover(fastLine, slowLine)
    trendEnded = ta.crossunder(fastLine, slowLine)
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Dial Long', strategy.long)
    elif strategy.position_size > 0 and (trendEnded or riskExceeded):
        strategy.close('Dial Long', comment='ATR risk' if riskExceeded else 'Period trend')

    plot(fastLine, 'Adaptive Fast EMA', color=color.blue)
    plot(slowLine, 'Adaptive Slow EMA', color=color.orange)
    plot(selectedSlowLength, 'Selected Slow Length', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
