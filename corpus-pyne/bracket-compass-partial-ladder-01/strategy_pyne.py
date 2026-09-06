"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Compass Partial Ladder", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(15, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(49, "Slow EMA", minval=3, group="Signal"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(1.9, "Shared Stop ATR", minval=0.5, step=0.1, group="Risk"),
    firstTargetAtr=input.float(1.4, "First Target ATR", minval=0.5, step=0.1, group="Risk"),
    secondTargetAtr=input.float(3.0, "Second Target ATR", minval=0.5, step=0.1, group="Risk"),
    firstPercent=input.float(40.0, "First Exit Percent", minval=5, maxval=90, step=5, group="Execution")
):
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)

    if ta.crossover(fastEma, slowEma):
        strategy.entry('Compass Ladder Long', strategy.long)

    if strategy.position_size > 0:
        sharedStop = strategy.position_avg_price - atrValue * stopAtr
        strategy.exit('Compass First', from_entry='Compass Ladder Long', qty_percent=firstPercent, stop=sharedStop, limit=strategy.position_avg_price + atrValue * firstTargetAtr)

        strategy.exit('Compass Remainder', from_entry='Compass Ladder Long', qty_percent=100.0 - firstPercent, stop=sharedStop, limit=strategy.position_avg_price + atrValue * secondTargetAtr)

    plot(fastEma, 'Fast EMA', color=color.teal)
    plot(slowEma, 'Slow EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
