"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, display, fixnan, input, na, nz, plot, script,
    strategy, ta
)
from pynecore.types import Persistent


@script.strategy("PineForge — Ledger History NA", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    lookback=input.int(31, "History Lookback", minval=2, group="Signal"),
    smoothLength=input.int(12, "Anchor Smoothing", minval=2, group="Signal"),
    __input_2__=input.float(2.3, "Entry Deviation %", minval=0.2, step=0.1, group="Signal"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.3, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    deviationPercent = __input_2__ * 0.01
    rawAnchor: float = close[lookback] if bar_index >= lookback else na
    carriedAnchor: float = fixnan(rawAnchor)
    safeAnchor: float = nz(carriedAnchor, close)
    smoothAnchor: float = ta.sma(safeAnchor, smoothLength)
    atrValue: float = ta.atr(atrLength)
    completedSignals: Persistent[int] = 0

    entryThreshold = smoothAnchor * (1.0 - deviationPercent)
    exitThreshold = smoothAnchor
    longSignal = not na(rawAnchor) and ta.crossunder(close, entryThreshold)

    if longSignal:
        strategy.entry('Ledger Long', strategy.long)
        completedSignals += 1

    if strategy.position_size > 0 and ta.crossover(close, exitThreshold):
        strategy.close('Ledger Long', comment='Mean return')

    if strategy.position_size > 0:
        strategy.exit('Ledger Guard', from_entry='Ledger Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(smoothAnchor, 'Carried History Anchor', color=color.purple)
    plot(completedSignals, 'Signal Count', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
