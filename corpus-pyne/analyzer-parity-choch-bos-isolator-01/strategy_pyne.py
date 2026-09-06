"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, high, input, low, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("Parity probe 02 - choch/bos isolator", shorttitle="par_p02", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=0, process_orders_on_close=False)
def main(
    i_pivot=input.int(5, "Pivot Strength", minval=2, maxval=20)
):

    pivotHigh: float = ta.pivothigh(high, i_pivot, i_pivot)
    pivotLow: float = ta.pivotlow(low, i_pivot, i_pivot)

    lastSwingHigh: Persistent[float] = na(float)
    lastSwingLow: Persistent[float] = na(float)
    prevSwingHigh: Persistent[float] = na(float)
    prevSwingLow: Persistent[float] = na(float)
    structureDirection: Persistent[int] = 0

    if not na(pivotHigh):
        prevSwingHigh = lastSwingHigh
        lastSwingHigh = pivotHigh

    if not na(pivotLow):
        prevSwingLow = lastSwingLow
        lastSwingLow = pivotLow

    bosUp: bool = not na(lastSwingHigh) and close > lastSwingHigh and (structureDirection <= 0)
    bosDown: bool = not na(lastSwingLow) and close < lastSwingLow and (structureDirection >= 0)
    chochUp: bool = not na(prevSwingHigh) and close > prevSwingHigh and (structureDirection < 0)
    chochDown: bool = not na(prevSwingLow) and close < prevSwingLow and (structureDirection > 0)

    if bosUp or chochUp:
        structureDirection = 1
    if bosDown or chochDown:
        structureDirection = -1

    any_bull_event: bool = bosUp or chochUp
    any_bear_event: bool = bosDown or chochDown

    if any_bull_event and strategy.position_size == 0:
        c_bu: str = 'bosUp' if bosUp else 'chochUp'
        strategy.entry('BU', strategy.long, comment=c_bu)

    if any_bear_event and strategy.position_size == 0:
        c_bd: str = 'bosDown' if bosDown else 'chochDown'
        strategy.entry('BD', strategy.short, comment=c_bd)

    if strategy.position_size != 0 and bar_index > strategy.opentrades.entry_bar_index(0):
        strategy.close_all(comment='event flatten')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
