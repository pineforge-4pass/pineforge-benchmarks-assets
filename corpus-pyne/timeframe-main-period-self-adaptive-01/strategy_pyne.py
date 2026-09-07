"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta, timeframe


@script.strategy("PF timeframe.main_period adaptive", shorttitle="PF_TF_MAINPERIOD", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    on_15m: bool = timeframe.main_period == '15'
    fast = ta.sma(close, 10)
    slow = ta.sma(close, 30)

    if on_15m and ta.crossover(fast, slow) and (strategy.position_size <= 0):
        strategy.entry('L', strategy.long)

    if on_15m and ta.crossunder(fast, slow) and (strategy.position_size >= 0):
        strategy.entry('S', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
