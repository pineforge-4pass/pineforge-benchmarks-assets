"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta


@script.strategy("HMA Crossover", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    fastLen=input.int(9, "Fast HMA", minval=2),
    slowLen=input.int(21, "Slow HMA", minval=2)
):

    hmaFast = ta.hma(close, fastLen)
    hmaSlow = ta.hma(close, slowLen)

    longCond = ta.crossover(hmaFast, hmaSlow)
    shortCond = ta.crossunder(hmaFast, hmaSlow)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(hmaFast, 'Fast HMA', color=color.blue, linewidth=2)
    plot(hmaSlow, 'Slow HMA', color=color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
