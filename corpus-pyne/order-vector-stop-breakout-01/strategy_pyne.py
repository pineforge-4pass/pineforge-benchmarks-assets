"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import bar_index, color, high, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Vector Stop Breakout", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    breakoutLength=input.int(28, "Breakout Length", minval=5, group="Signal"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Signal"),
    contractionRatio=input.float(0.82, "ATR Contraction Ratio", minval=0.2, maxval=1.5, step=0.02, group="Signal"),
    entryBufferAtr=input.float(0.12, "Entry Buffer ATR", minval=0, step=0.02, group="Execution"),
    stopAtr=input.float(2.0, "Stop ATR", minval=0.5, step=0.1, group="Risk"),
    maxBars=input.int(72, "Maximum Hold Bars", minval=5, group="Risk")
):
    atrValue = ta.atr(atrLength)
    atrBaseline = ta.sma(atrValue, breakoutLength)
    breakoutLevel = inline_series(ta.highest(high, breakoutLength), 1)
    contracted = atrValue < atrBaseline * contractionRatio
    stopTrigger = breakoutLevel + atrValue * entryBufferAtr
    entryBar: Persistent[int] = na(int)

    if strategy.position_size == 0 and contracted:
        strategy.entry('Vector Breakout', strategy.long, stop=stopTrigger)
    elif strategy.position_size == 0:
        strategy.cancel('Vector Breakout')

    if strategy.position_size > 0 and strategy.position_size[1] <= 0:
        entryBar = bar_index
    if strategy.position_size == 0:
        entryBar = na

    if strategy.position_size > 0:
        strategy.exit('Vector Guard', from_entry='Vector Breakout', stop=strategy.position_avg_price - atrValue * stopAtr)

        if not na(entryBar) and bar_index - entryBar >= maxBars:
            strategy.close('Vector Breakout', comment='Time boundary')

    plot(breakoutLevel, 'Breakout Level', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
