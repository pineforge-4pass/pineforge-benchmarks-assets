"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, input, low, na, script, strategy, ta


@script.strategy("Stochastic Slow Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    length=input.int(14, "Length", minval=1),
    OverBought=input(80, "Overbought"),
    OverSold=input(20, "Oversold")
):
    smoothK: int = 3
    smoothD: int = 3
    k = ta.sma(ta.stoch(close, high, low, length), smoothK)
    d = ta.sma(k, smoothD)
    co = ta.crossover(k, d)
    cu = ta.crossunder(k, d)
    if not na(k) and (not na(d)):
        if co and k < OverSold:
            strategy.entry('StochLE', strategy.long, comment='StochLE')
        if cu and k > OverBought:
            strategy.entry('StochSE', strategy.short, comment='StochSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)