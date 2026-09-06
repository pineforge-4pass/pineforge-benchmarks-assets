"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Rivet Calc Fill", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=True, calc_on_order_fills=True)
def main(
    fastLength=input.int(11, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(37, "Slow EMA", minval=3, group="Signal"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(1.7, "Stop ATR", minval=0.5, step=0.1, group="Risk"),
    targetAtr=input.float(2.2, "Target ATR", minval=0.5, step=0.1, group="Risk")
):
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)

    if ta.crossover(fastEma, slowEma) and strategy.position_size == 0:
        strategy.entry('Rivet Long', strategy.long)

    if strategy.position_size > 0:
        strategy.exit('Rivet Attached Risk', from_entry='Rivet Long', stop=strategy.position_avg_price - atrValue * stopAtr, limit=strategy.position_avg_price + atrValue * targetAtr)

    plot(fastEma, 'Fast EMA', color=color.aqua)
    plot(slowEma, 'Slow EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
