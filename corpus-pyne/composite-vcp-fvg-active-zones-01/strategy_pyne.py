"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import array, close, high, low, na, open, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("VCP probe 02 - fvg zones", shorttitle="VCP_p02", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, max_boxes_count=300)
def main():
    atrVal: float = ta.atr(14)
    bullFVG: bool = low > high[2] and close[1] > open[1]
    bearFVG: bool = high < low[2] and close[1] < open[1]

    minFVGSize: float = atrVal * 0.3

    fvgTops: Persistent[list[float]] = array.new_float()
    fvgBottoms: Persistent[list[float]] = array.new_float()
    fvgBullish: Persistent[list[bool]] = array.new_bool()

    fvgTop: float = na(float)
    fvgBottom: float = na(float)

    if bullFVG and low - high[2] >= minFVGSize:
        fvgTop = low
        fvgBottom = high[2]
        array.push(fvgTops, fvgTop)
        array.push(fvgBottoms, fvgBottom)
        array.push(fvgBullish, True)

    if bearFVG and low[2] - high >= minFVGSize:
        fvgTop = low[2]
        fvgBottom = high
        array.push(fvgTops, fvgTop)
        array.push(fvgBottoms, fvgBottom)
        array.push(fvgBullish, False)

    while array.size(fvgTops) > 30:
        array.shift(fvgTops)
        array.shift(fvgBottoms)
        array.shift(fvgBullish)

    inBullFVG: bool = False
    inBearFVG: bool = False

    if array.size(fvgTops) > 0:
        for i in pine_range(0, array.size(fvgTops) - 1):
            fTop: float = array.get(fvgTops, i)
            fBottom: float = array.get(fvgBottoms, i)
            isBull: bool = array.get(fvgBullish, i)

            if low <= fTop and high >= fBottom:
                if isBull:
                    inBullFVG = True
                else:
                    inBearFVG = True

    if inBullFVG and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='bull-fvg touch')

    if inBearFVG and strategy.position_size > 0:
        strategy.close('L', comment='bear-fvg touch exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
