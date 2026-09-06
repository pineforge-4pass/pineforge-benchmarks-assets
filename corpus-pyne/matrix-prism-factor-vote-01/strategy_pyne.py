"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, color, input, matrix, plot, script, strategy, ta
from pynecore.types import Matrix, Persistent


@script.strategy("PineForge — Prism Matrix Vote", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(16, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(44, "Slow EMA", minval=3, group="Signal"),
    rsiLength=input.int(13, "RSI Length", minval=2, group="Signal"),
    minimumScore=input.float(2.0, "Minimum Vote Score", minval=1, maxval=4, group="Signal"),
    atrLength=input.int(19, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.2, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    rsiValue = ta.rsi(close, rsiLength)
    atrValue = ta.atr(atrLength)

    factorGrid: Persistent[Matrix[float]] = matrix.new(2, 2, 0.0)
    matrix.set(factorGrid, 0, 0, 1.0 if fastEma > slowEma else -1.0)
    matrix.set(factorGrid, 0, 1, 1.0 if close > fastEma else -1.0)
    matrix.set(factorGrid, 1, 0, 1.0 if rsiValue > 52.0 else -1.0)
    matrix.set(factorGrid, 1, 1, 1.0 if atrValue / close < 0.04 else -1.0)

    voteScore: float = 0.0
    for row in pine_range(0, 1):
        for column in pine_range(0, 1):
            voteScore += matrix.get(factorGrid, row, column)

    if ta.crossover(voteScore, minimumScore):
        strategy.entry('Prism Long', strategy.long)
    if strategy.position_size > 0 and voteScore <= 0:
        strategy.close('Prism Long', comment='Factor vote reversed')
    if strategy.position_size > 0:
        strategy.exit('Prism Guard', from_entry='Prism Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(fastEma, 'Fast EMA', color=color.aqua)
    plot(slowEma, 'Slow EMA', color=color.purple)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
