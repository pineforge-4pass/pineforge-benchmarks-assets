"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, script, strategy, ta, volume


@script.strategy("Volume Breakout", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    volLen=input.int(20, "Volume MA Length", minval=5),
    volMult=input.float(1.5, "Volume Spike Multiplier", step=0.1),
    atrLen=input.int(14, "ATR Length", minval=1),
    atrMult=input.float(1.0, "ATR Breakout Multiplier", step=0.1)
):

    volMA = ta.sma(volume, volLen)
    volSpike = volume > volMA * volMult
    atrVal = ta.atr(atrLen)

    priceBreakUp = close > close[1] + atrVal * atrMult
    priceBreakDown = close < close[1] - atrVal * atrMult

    longCond = priceBreakUp and volSpike
    shortCond = priceBreakDown and volSpike

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and close < close[1] and (volume < volMA):
        strategy.close('Long')
    if strategy.position_size < 0 and close > close[1] and (volume < volMA):
        strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
