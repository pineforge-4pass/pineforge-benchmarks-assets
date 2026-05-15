"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, input, script, strategy, ta


@script.strategy("DMI ADX Trend Following", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    diLen=input.int(14, "DI Length", minval=1),
    adxSmooth=input.int(14, "ADX Smoothing", minval=1),
    adxThresh=input.int(20, "ADX Threshold", minval=10)
):

    diPlus, diMinus, adxVal = ta.dmi(diLen, adxSmooth)

    bullCross = ta.crossover(diPlus, diMinus)
    bearCross = ta.crossunder(diPlus, diMinus)

    if bullCross:
        strategy.entry('Long', strategy.long)
    if bearCross:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)