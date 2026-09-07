"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, color, display, input, math, na, plot, script, strategy, ta
from pynecore.types import Series


@udt
class ThresholdLadder:
    firstLevel: float = na(float)
    increment: float = na(float)


@script.strategy("PineForge — Breaker Method While", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    firstLevel=input.float(42.0, "First RSI Level", minval=10, maxval=70, step=1, group="Ladder"),
    levelIncrement=input.float(4.0, "Level Increment", minval=1, maxval=12, step=0.5, group="Ladder"),
    maximumLevel=input.float(70.0, "Maximum RSI Level", minval=40, maxval=90, step=1, group="Ladder"),
    maximumSteps=input.int(10, "Maximum Steps", minval=2, maxval=16, group="Ladder"),
    requiredPasses=input.int(4, "Required Passed Levels", minval=1, maxval=10, group="Ladder"),
    trendLength=input.int(45, "Trend EMA Length", minval=5, group="Trend"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.3, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    @method
    def levelAt(self: ThresholdLadder, index: int):
        return self.firstLevel + self.increment * index

    ladder: ThresholdLadder = ThresholdLadder(firstLevel, levelIncrement)
    rsiValue = ta.rsi(close, 14)
    index: int = 0
    passedLevels: int = 0
    while index < maximumSteps:
        currentLevel = levelAt(ladder, index)
        if currentLevel > maximumLevel:
            break
        if rsiValue > currentLevel:
            passedLevels += 1
        index += 1

    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)
    ladderReady: Series = passedLevels >= requiredPasses

    enterLong = ladderReady and (not ladderReady[1]) and (close > trendLine)
    ladderEnded = passedLevels < math.max(requiredPasses - 2, 1) or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Breaker Long', strategy.long)
    elif strategy.position_size > 0 and (ladderEnded or riskExceeded):
        strategy.close('Breaker Long', comment='ATR risk' if riskExceeded else 'Ladder ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(passedLevels, 'Passed Levels', color=color.purple, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
