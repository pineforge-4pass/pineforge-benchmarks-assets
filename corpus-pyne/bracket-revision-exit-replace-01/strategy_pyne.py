"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Revision Exit Replacement", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(20, "Fast EMA Length", minval=2, group="Signal"),
    slowLength=input.int(61, "Slow EMA Length", minval=5, group="Signal"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Bracket"),
    revisionBars=input.int(14, "Revision Hold Bars", minval=2, group="Bracket"),
    wideStopAtr=input.float(2.8, "Initial Stop ATR", minval=0.5, step=0.1, group="Bracket"),
    wideTargetAtr=input.float(4.2, "Initial Target ATR", minval=0.5, step=0.1, group="Bracket"),
    narrowStopAtr=input.float(1.4, "Revised Stop ATR", minval=0.2, step=0.1, group="Bracket"),
    narrowTargetAtr=input.float(2.4, "Revised Target ATR", minval=0.5, step=0.1, group="Bracket")
):
    fastLine = ta.ema(close, fastLength)
    slowLine = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)
    enterLong = ta.crossover(fastLine, slowLine)

    admittedAt: Persistent[int] = na(int)
    if strategy.position_size == 0 and enterLong:
        strategy.entry('Revision Long', strategy.long)

    if strategy.position_size > 0 and strategy.position_size[1] <= 0:
        admittedAt = bar_index
    if strategy.position_size == 0:
        admittedAt = na

    heldBars = 0 if na(admittedAt) else bar_index - admittedAt
    if strategy.position_size > 0 and heldBars < revisionBars:
        strategy.exit('Revision Guard', from_entry='Revision Long', stop=strategy.position_avg_price - atrValue * wideStopAtr, limit=strategy.position_avg_price + atrValue * wideTargetAtr, comment='Initial bracket')
    elif strategy.position_size > 0:
        strategy.exit('Revision Guard', from_entry='Revision Long', stop=strategy.position_avg_price - atrValue * narrowStopAtr, limit=strategy.position_avg_price + atrValue * narrowTargetAtr, comment='Revised bracket')

    if strategy.position_size > 0 and ta.crossunder(fastLine, slowLine):
        strategy.close('Revision Long', comment='Trend ended')

    plot(fastLine, 'Fast EMA', color=color.blue)
    plot(slowLine, 'Slow EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
