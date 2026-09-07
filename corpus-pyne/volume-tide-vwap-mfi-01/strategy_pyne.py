"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, hlc3, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Tide VWAP Volume", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    priceSource: Series[float] = input.source(hlc3, "VWAP Source", group="Signal"),
    mfiLength=input.int(17, "MFI Length", minval=2, group="Signal"),
    entryFlow=input.float(56.0, "Entry Money Flow", minval=50, maxval=90, group="Signal"),
    exitFlow=input.float(43.0, "Exit Money Flow", minval=10, maxval=50, group="Signal"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.1, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    sessionVwap = ta.vwap(priceSource)
    moneyFlow = ta.mfi(hlc3, mfiLength)
    atrValue = ta.atr(atrLength)

    if ta.crossover(priceSource, sessionVwap) and moneyFlow > entryFlow:
        strategy.entry('Tide Long', strategy.long)
    if strategy.position_size > 0 and (ta.crossunder(priceSource, sessionVwap) or moneyFlow < exitFlow):
        strategy.close('Tide Long', comment='Volume flow receded')
    if strategy.position_size > 0:
        strategy.exit('Tide Guard', from_entry='Tide Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(sessionVwap, 'Session VWAP', color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
