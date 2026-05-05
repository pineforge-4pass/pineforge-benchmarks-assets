"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, input, na, script, strategy, ta


@script.strategy("Pivot Extension Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    leftBars=input(4, "Pivot Lookback Left"),
    rightBars=input(2, "Pivot Lookback Right")
):
    ph = ta.pivothigh(leftBars, rightBars)
    pl = ta.pivotlow(leftBars, rightBars)
    if not na(pl):
        strategy.entry('PivExtLE', strategy.long, comment='PivExtLE')
    if not na(ph):
        strategy.entry('PivExtSE', strategy.short, comment='PivExtSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)