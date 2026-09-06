"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, close, color, high, input, low, plot, request, script,
    strategy, syminfo, ta
)


@script.strategy("PineForge — Rangefinder Daily Reference", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    minimumRangePercent=input.float(1.2, "Minimum Prior-Day Range %", minval=0.1, step=0.1, group="Daily Reference"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.5, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    priorDailyHigh, priorDailyLow = request.security(syminfo.tickerid, 'D', (high[1], low[1]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    priorDailyMidpoint = (priorDailyHigh + priorDailyLow) * 0.5
    priorDailyRangePercent = (priorDailyHigh - priorDailyLow) / priorDailyLow * 100 if priorDailyLow > 0 else 0.0
    atrValue = ta.atr(atrLength)

    enterLong = priorDailyRangePercent >= minimumRangePercent and ta.crossover(close, priorDailyHigh)
    referenceLost = strategy.position_size > 0 and close < priorDailyMidpoint
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Rangefinder Long', strategy.long)
    elif strategy.position_size > 0 and (referenceLost or riskExceeded):
        strategy.close('Rangefinder Long', comment='ATR risk' if riskExceeded else 'Daily midpoint')

    plot(priorDailyHigh, 'Prior Daily High', color=color.green)
    plot(priorDailyLow, 'Prior Daily Low', color=color.red)
    plot(priorDailyMidpoint, 'Prior Daily Midpoint', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
