"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta


@script.strategy("PineForge — Ledger Outcome Throttle", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(17, "Fast EMA Length", minval=2, group="Signal"),
    slowLength=input.int(49, "Slow EMA Length", minval=5, group="Signal"),
    fullQuantity=input.float(2.0, "Full Quantity", minval=0.1, step=0.1, group="Sizing"),
    recoveryQuantity=input.float(1.0, "Recovery Quantity", minval=0.1, step=0.1, group="Sizing"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.3, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    fastLine = ta.ema(close, fastLength)
    slowLine = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)

    nextQuantity: float = fullQuantity
    if strategy.closedtrades > 0:
        lastClosedIndex = strategy.closedtrades - 1
        lastRealizedProfit = strategy.closedtrades.profit(lastClosedIndex)
        nextQuantity = recoveryQuantity if lastRealizedProfit < 0 else fullQuantity

    enterLong = ta.crossover(fastLine, slowLine)
    trendEnded = ta.crossunder(fastLine, slowLine)
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Ledger Throttle Long', strategy.long, qty=nextQuantity)
    elif strategy.position_size > 0 and (trendEnded or riskExceeded):
        strategy.close('Ledger Throttle Long', comment='ATR risk' if riskExceeded else 'Trend ended')

    plot(fastLine, 'Fast EMA', color=color.blue)
    plot(slowLine, 'Slow EMA', color=color.orange)
    plot(nextQuantity, 'Next Quantity', color=color.purple, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
