"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, hlc3, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Sextant CCI HMA", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    cciLength=input.int(21, "CCI Length", minval=3, group="Signal"),
    hmaLength=input.int(34, "HMA Length", minval=4, group="Trend"),
    entryLevel=input.float(72.0, "Entry CCI", minval=-50, maxval=200, step=1, group="Signal"),
    exitLevel=input.float(-18.0, "Exit CCI", minval=-200, maxval=100, step=1, group="Signal"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.3, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    cciValue = ta.cci(hlc3, cciLength)
    hmaLine: Series = ta.hma(close, hmaLength)
    atrValue = ta.atr(atrLength)
    hmaRising = hmaLine > hmaLine[1]

    enterLong = ta.crossover(cciValue, entryLevel) and hmaRising and (close > hmaLine)
    impulseEnded = ta.crossunder(cciValue, exitLevel) or close < hmaLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Sextant Long', strategy.long)
    elif strategy.position_size > 0 and (impulseEnded or riskExceeded):
        strategy.close('Sextant Long', comment='ATR risk' if riskExceeded else 'Impulse ended')

    plot(hmaLine, 'Hull Direction', color=color.aqua)
    plot(cciValue, 'CCI', color=color.purple, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
