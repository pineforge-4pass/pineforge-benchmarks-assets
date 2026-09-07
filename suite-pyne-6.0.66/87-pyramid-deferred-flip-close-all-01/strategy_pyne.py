"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, hour, low, minute, script, strategy, ta


@script.strategy("PF Pyramid carry 01 - deferred flip", shorttitle="PYR_p01_FLIP", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=4, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)
    atrVal = ta.atr(14)

    longCond: bool = ta.crossover(emaFast, emaSlow) and rsiVal < 70
    shortStop: bool = ta.crossunder(rsiVal, 50)

    if longCond:
        strategy.entry('L', strategy.long, qty=1, comment='add long market')

    if shortStop:
        strategy.entry('S', strategy.short, qty=1, stop=low - atrVal * 0.25, comment='flip short stop')

    if hour == 21 and minute == 45:
        strategy.close_all(comment='session close_all')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
