"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, close, color, currency, high, input, low, math, na,
    plot, script, strategy
)
from pynecore.types import Persistent


@script.strategy("Parabolic SAR Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    start=input(0.02),
    increment=input(0.02),
    maximum=input(0.2)
):
    uptrend: Persistent[bool] = False
    EP: Persistent[float] = na(float)
    SAR: Persistent[float] = na(float)
    AF: Persistent[float] = start
    nextBarSAR: Persistent[float] = na(float)
    if bar_index > 0:
        firstTrendBar: bool = False
        SAR = nextBarSAR
        if bar_index == 1:
            prevSAR: float = na(float)
            prevEP: float = na(float)
            lowPrev = low[1]
            highPrev = high[1]
            closeCur = close
            closePrev = close[1]
            if closeCur > closePrev:
                uptrend = True
                EP = high
                prevSAR = lowPrev
                prevEP = high
            else:
                uptrend = False
                EP = low
                prevSAR = highPrev
                prevEP = low
            firstTrendBar = True
            SAR = prevSAR + start * (prevEP - prevSAR)
        if uptrend:
            if SAR > low:
                firstTrendBar = True
                uptrend = False
                SAR = math.max(EP, high)
                EP = low
                AF = start
        else:
            if SAR < high:
                firstTrendBar = True
                uptrend = True
                SAR = math.min(EP, low)
                EP = high
                AF = start
        if not firstTrendBar:
            if uptrend:
                if high > EP:
                    EP = high
                    AF = math.min(AF + increment, maximum)
            else:
                if low < EP:
                    EP = low
                    AF = math.min(AF + increment, maximum)
        if uptrend:
            SAR = math.min(SAR, low[1])
            if bar_index > 1:
                SAR = math.min(SAR, low[2])
        else:
            SAR = math.max(SAR, high[1])
            if bar_index > 1:
                SAR = math.max(SAR, high[2])
        nextBarSAR = SAR + AF * (EP - SAR)
        if barstate.isconfirmed:
            if uptrend:
                strategy.entry('ParSE', strategy.short, stop=nextBarSAR, comment='ParSE')
                strategy.cancel('ParLE')
            else:
                strategy.entry('ParLE', strategy.long, stop=nextBarSAR, comment='ParLE')
                strategy.cancel('ParSE')

    plot(SAR, 'SAR', style=plot.style_cross, linewidth=3, color=color.orange)
    plot(nextBarSAR, 'Next bar SAR', style=plot.style_cross, linewidth=3, color=color.aqua)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)