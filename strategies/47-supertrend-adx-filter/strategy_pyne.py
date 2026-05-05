"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, currency, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Supertrend ADX Filter", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    stFactor=input.float(3.0, "Supertrend Factor", step=0.1),
    stPeriod=input.int(10, "Supertrend ATR Period", minval=1),
    diLen=input.int(14, "DI Length", minval=1),
    adxSmooth=input.int(14, "ADX Smoothing", minval=1),
    adxThresh=input.int(20, "ADX Threshold")
):

    stValue, stDirection = ta.supertrend(stFactor, stPeriod)

    diPlus, diMinus, adxVal = ta.dmi(diLen, adxSmooth)

    stBull: Series = stDirection < 0
    stBear: Series = stDirection > 0
    adxStrong = adxVal > adxThresh

    longCond = stBull and (not stBull[1]) and adxStrong
    shortCond = stBear and (not stBear[1]) and adxStrong

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and stBear:
        strategy.close('Long')
    if strategy.position_size < 0 and stBull:
        strategy.close('Short')

    plot(stValue, 'Supertrend', color=color.green if stBull else color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
