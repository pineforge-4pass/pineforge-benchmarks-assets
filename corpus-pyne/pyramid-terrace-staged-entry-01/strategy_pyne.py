"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Terrace Pyramid", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=3, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    trendLength=input.int(42, "Trend EMA", minval=5, group="Signal"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Signal"),
    firstPullback=input.float(0.25, "First Terrace ATR", minval=0, step=0.05, group="Execution"),
    secondPullback=input.float(0.7, "Second Terrace ATR", minval=0.1, step=0.05, group="Execution"),
    stopAtr=input.float(2.8, "Portfolio Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    trend: Series = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)
    risingTrend = trend > trend[1] and close > trend
    firstTerrace = trend + atrValue * firstPullback
    secondTerrace = trend - atrValue * secondPullback

    if risingTrend and ta.crossover(close, firstTerrace):
        strategy.entry('Terrace One', strategy.long, qty=1)
    if risingTrend and strategy.position_size == 1 and ta.crossunder(close, trend):
        strategy.entry('Terrace Two', strategy.long, qty=1)
    if risingTrend and strategy.position_size == 2 and ta.crossunder(close, secondTerrace):
        strategy.entry('Terrace Three', strategy.long, qty=1)

    if strategy.position_size > 0:
        strategy.exit('Terrace Guard', stop=strategy.position_avg_price - atrValue * stopAtr)
    if strategy.position_size > 0 and trend < trend[1]:
        strategy.close('Terrace One')
        strategy.close('Terrace Two')
        strategy.close('Terrace Three')

    plot(trend, 'Trend EMA', color=color.blue)
    plot(secondTerrace, 'Deep Terrace', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
