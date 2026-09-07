"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Tranche Partial Market Close", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=4, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(19, "Fast EMA Length", minval=2, group="Signal"),
    slowLength=input.int(58, "Slow EMA Length", minval=5, group="Signal"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    trancheAtr=input.float(1.3, "First Tranche ATR", minval=0.2, step=0.1, group="Risk"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    fastLine = ta.ema(close, fastLength)
    slowLine = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)
    enterLong = ta.crossover(fastLine, slowLine)

    trancheTaken: Persistent[bool] = False
    if strategy.position_size == 0:
        trancheTaken = False

    firstObjective = strategy.position_size > 0 and close >= strategy.position_avg_price + atrValue * trancheAtr
    trendEnded = strategy.position_size > 0 and ta.crossunder(fastLine, slowLine)
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Tranche Long', strategy.long)
    elif strategy.position_size > 0 and (not trancheTaken) and firstObjective:
        strategy.close('Tranche Long', qty_percent=50, comment='First tranche')
        trancheTaken = True
    elif strategy.position_size > 0 and (trendEnded or riskExceeded):
        strategy.close('Tranche Long', comment='ATR risk' if riskExceeded else 'Trend ended')

    plot(fastLine, 'Fast EMA', color=color.blue)
    plot(slowLine, 'Slow EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
