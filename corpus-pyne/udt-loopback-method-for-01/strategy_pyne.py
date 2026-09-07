"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, color, display, input, na, plot, script, strategy, ta


@udt
class HorizonLedger:
    value: float = na(float)


@script.strategy("PineForge — Loopback Method For", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    horizonCount=input.int(5, "Horizon Count", minval=2, maxval=8, group="Horizons"),
    horizonSpacing=input.int(4, "Horizon Spacing", minval=1, maxval=12, group="Horizons"),
    minimumVote=input.float(0.55, "Minimum Average Vote", minval=-1, maxval=1, step=0.05, group="Horizons"),
    trendLength=input.int(51, "Trend EMA Length", minval=5, group="Trend"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    @method
    def directionAgainst(self: HorizonLedger, referenceValue: float):
        return 1.0 if self.value > referenceValue else -1.0

    ledger: HorizonLedger = HorizonLedger(close)
    voteSum: float = 0.0
    for horizon in pine_range(1, horizonCount):
        historicalValue = close[horizon * horizonSpacing]
        voteSum += 0.0 if na(historicalValue) else directionAgainst(ledger, historicalValue)

    averageVote = voteSum / horizonCount
    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)

    enterLong = ta.crossover(averageVote, minimumVote) and close > trendLine
    voteEnded = averageVote < 0 or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Loopback Long', strategy.long)
    elif strategy.position_size > 0 and (voteEnded or riskExceeded):
        strategy.close('Loopback Long', comment='ATR risk' if riskExceeded else 'Vote ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(averageVote, 'Average Horizon Vote', color=color.blue, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
