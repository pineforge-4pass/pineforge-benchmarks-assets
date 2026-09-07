"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Horizon Next-Bar Close", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    signalLength=input.int(34, "Signal SMA", minval=3, group="Signal"),
    holdBars=input.int(11, "Hold Bars", minval=1, maxval=200, group="Risk"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.2, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    signalAverage = ta.sma(close, signalLength)
    atrValue = ta.atr(atrLength)
    enterLong = ta.crossover(close, signalAverage)
    openedBar: Persistent[int] = na(int)

    if enterLong and strategy.position_size == 0:
        strategy.entry('Horizon Long', strategy.long)

    if strategy.position_size > 0 and strategy.position_size[1] <= 0:
        openedBar = bar_index

    timeExpired = strategy.position_size > 0 and (not na(openedBar)) and (bar_index - openedBar >= holdBars)
    if timeExpired:
        strategy.close('Horizon Long', comment='Deterministic time exit')

    if strategy.position_size > 0:
        strategy.exit('Horizon Stop', from_entry='Horizon Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    if strategy.position_size == 0:
        openedBar = na

    plot(signalAverage, 'Signal SMA', color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
