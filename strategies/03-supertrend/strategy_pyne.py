"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, input, script, strategy, ta


@script.strategy("Supertrend Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    atrPeriod=input(10, "ATR Length"),
    factor=input.float(3.0, "Factor", step=0.01)
):
    _, direction = ta.supertrend(factor, atrPeriod)

    if ta.change(direction) < 0:
        strategy.entry('My Long Entry Id', strategy.long)

    if ta.change(direction) > 0:
        strategy.entry('My Short Entry Id', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)