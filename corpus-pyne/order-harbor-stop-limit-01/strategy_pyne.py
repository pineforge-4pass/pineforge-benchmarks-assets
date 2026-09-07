"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import bar_index, close, color, high, input, low, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Harbor Stop Limit", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    harborLength=input.int(35, "Harbor Range", minval=5, group="Signal"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Signal"),
    activationAtr=input.float(0.1, "Activation Buffer ATR", minval=0, step=0.02, group="Execution"),
    limitAtr=input.float(0.28, "Maximum Fill Distance ATR", minval=0.05, step=0.01, group="Execution"),
    stopAtr=input.float(2.4, "Protective Stop ATR", minval=0.5, step=0.1, group="Risk"),
    maximumBars=input.int(64, "Maximum Hold Bars", minval=5, group="Risk")
):
    atrValue = ta.atr(atrLength)
    rangeHigh = inline_series(ta.highest(high, harborLength), 1)
    rangeMid = (inline_series(ta.highest(high, harborLength), 1) + inline_series(ta.lowest(low, harborLength), 1)) / 2.0
    activationPrice = rangeHigh + atrValue * activationAtr
    limitPrice = activationPrice + atrValue * limitAtr
    validSetup = close > rangeMid and close < activationPrice
    fillBar: Persistent[int] = na(int)

    if strategy.position_size == 0 and validSetup:
        strategy.entry('Harbor Breakout', strategy.long, stop=activationPrice, limit=limitPrice)
    elif strategy.position_size == 0:
        strategy.cancel('Harbor Breakout')

    if strategy.position_size > 0 and strategy.position_size[1] <= 0:
        fillBar = bar_index
    if strategy.position_size == 0:
        fillBar = na

    if strategy.position_size > 0:
        strategy.exit('Harbor Guard', from_entry='Harbor Breakout', stop=strategy.position_avg_price - atrValue * stopAtr)

        if not na(fillBar) and bar_index - fillBar >= maximumBars:
            strategy.close('Harbor Breakout', comment='Harbor time limit')

    plot(rangeHigh, 'Range High', color=color.blue)
    plot(limitPrice, 'Stop-Limit Ceiling', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
