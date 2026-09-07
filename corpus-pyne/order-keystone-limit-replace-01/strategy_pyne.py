"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Keystone Limit Pullback", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    trendLength=input.int(48, "Trend EMA", minval=5, group="Signal"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Signal"),
    pullbackAtr=input.float(0.55, "Pullback ATR", minval=0.1, step=0.05, group="Execution"),
    stopAtr=input.float(2.3, "Stop ATR", minval=0.5, step=0.1, group="Risk"),
    targetAtr=input.float(2.0, "Target ATR", minval=0.5, step=0.1, group="Risk")
):
    trend: Series = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)
    risingTrend = trend > trend[1] and close > trend
    workingLimit = trend - atrValue * pullbackAtr

    if strategy.position_size == 0 and risingTrend:
        strategy.entry('Keystone Pullback', strategy.long, limit=workingLimit)
    elif strategy.position_size == 0:
        strategy.cancel('Keystone Pullback')

    if strategy.position_size > 0:
        strategy.exit('Keystone Risk', from_entry='Keystone Pullback', stop=strategy.position_avg_price - atrValue * stopAtr, limit=strategy.position_avg_price + atrValue * targetAtr)

    plot(trend, 'Trend EMA', color=color.teal)
    plot(workingLimit, 'Working Limit', color=color.yellow)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
