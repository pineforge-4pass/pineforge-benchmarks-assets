"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, na, script, strategy, ta


@script.strategy("Volty Expan Close Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    length=input(5, "Length"),
    numATRs=input(0.75, "ATR Mult")
):
    atrs = ta.sma(ta.tr, length) * numATRs
    if not na(close[length]):
        strategy.entry('VltClsLE', strategy.long, stop=close + atrs, comment='VltClsLE')
        strategy.entry('VltClsSE', strategy.short, stop=close - atrs, comment='VltClsSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
