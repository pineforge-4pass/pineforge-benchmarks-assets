"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, low, open, script, strategy


@script.strategy("InSide Bar Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    if high < high[1] and low > low[1]:
        if close > open:
            strategy.entry('InsBarLE', strategy.long, comment='InsBarLE')
        if close < open:
            strategy.entry('InsBarSE', strategy.short, comment='InsBarSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)