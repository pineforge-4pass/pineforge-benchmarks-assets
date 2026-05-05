"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, script, strategy, ta


@script.strategy("MovingAvg2Line Cross", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    fastLength=input(9),
    slowLength=input(18)
):
    price = close
    mafast = ta.sma(price, fastLength)
    maslow = ta.sma(price, slowLength)
    if ta.crossover(mafast, maslow):
        strategy.entry('MA2CrossLE', strategy.long, comment='MA2CrossLE')
    if ta.crossunder(mafast, maslow):
        strategy.entry('MA2CrossSE', strategy.short, comment='MA2CrossSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)