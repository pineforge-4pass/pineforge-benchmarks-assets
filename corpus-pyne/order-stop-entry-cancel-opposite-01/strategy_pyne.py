"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, low, script, strategy, ta


@script.strategy("PF probe 52 - stop entry cancel", shorttitle="PF_P52_CANCEL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    fast = ta.ema(close, 8)
    slow = ta.ema(close, 21)

    longStop = high[1]
    shortStop = low[1]

    if fast > slow:
        strategy.entry('LE', strategy.long, stop=longStop, comment='live long stop')
        strategy.cancel('SE')
    else:
        strategy.entry('SE', strategy.short, stop=shortStop, comment='live short stop')
        strategy.cancel('LE')

    if strategy.position_size > 0 and fast < slow:
        strategy.close('LE', comment='flip flat long')

    if strategy.position_size < 0 and fast > slow:
        strategy.close('SE', comment='flip flat short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
