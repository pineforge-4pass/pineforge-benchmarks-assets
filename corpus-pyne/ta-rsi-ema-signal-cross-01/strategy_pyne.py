"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hline, input, plot, script, strategy, ta


@script.strategy("RSI EMA Signal", overlay=False, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    rsiLen=input.int(14, "RSI Length", minval=1),
    signalLen=input.int(9, "Signal EMA Length", minval=1)
):

    rsiVal = ta.rsi(close, rsiLen)
    rsiSignal = ta.ema(rsiVal, signalLen)

    longCond = ta.crossover(rsiVal, rsiSignal) and rsiVal < 50
    shortCond = ta.crossunder(rsiVal, rsiSignal) and rsiVal > 50

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(rsiVal, 'RSI', color=color.blue, linewidth=2)
    plot(rsiSignal, 'Signal', color=color.orange)
    hline(50, 'Mid', color=color.gray)
    hline(70, 'OB', color=color.red)
    hline(30, 'OS', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
