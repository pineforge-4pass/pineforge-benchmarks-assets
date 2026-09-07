"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import close, color, input, math, na, plot, script, strategy, ta


@script.strategy("PineForge — Caliper Scalar Switch", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    filterMode=input.string("EMA", "Filter Mode", options=("EMA", "SMA", "Blend"), group="Signal"),
    baseLength=input.int(29, "Base Length", minval=3, group="Signal"),
    lengthScale=input.float(1.35, "Length Scale", minval=0.5, maxval=3, step=0.05, group="Signal"),
    confirmationLength=input.int(113, "Confirmation EMA", minval=10, group="Signal"),
    allowShort=input.bool(True, "Allow Short", group="Execution"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.0, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    scaledLength: int = cast_int(math.round(baseLength * lengthScale))
    emaFilter = ta.ema(close, scaledLength)
    smaFilter = ta.sma(close, scaledLength)
    __block_result__ = na
    __switch__ = filterMode
    if __switch__ == "EMA":
        __block_result__ = emaFilter
    elif __switch__ == "SMA":
        __block_result__ = smaFilter
    else:
        __block_result__ = (emaFilter + smaFilter) / 2.0
    selectedFilter: float = __block_result__
    confirmationFilter = ta.ema(close, confirmationLength)

    atrValue = ta.atr(atrLength)
    if ta.crossover(selectedFilter, confirmationFilter):
        strategy.entry('Caliper Long', strategy.long)
    if allowShort and ta.crossunder(selectedFilter, confirmationFilter):
        strategy.entry('Caliper Short', strategy.short)

    if strategy.position_size > 0:
        strategy.exit('Caliper Long Guard', from_entry='Caliper Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    if strategy.position_size < 0:
        strategy.exit('Caliper Short Guard', from_entry='Caliper Short', stop=strategy.position_avg_price + atrValue * stopAtr)

    plot(selectedFilter, 'Selected Filter', color=color.yellow)
    plot(confirmationFilter, 'Confirmation EMA', color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
