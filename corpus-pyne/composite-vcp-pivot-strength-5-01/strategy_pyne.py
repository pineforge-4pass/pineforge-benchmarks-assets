"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, input, low, na, script, strategy, ta


@script.strategy("VCP probe 01 - pivot strength 5", shorttitle="VCP_p01", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_pivot=input.int(5, "Pivot Strength", minval=2, maxval=20)
):

    pivotHigh: float = ta.pivothigh(high, i_pivot, i_pivot)
    pivotLow: float = ta.pivotlow(low, i_pivot, i_pivot)

    pivotHighConfirmed: bool = not na(pivotHigh)
    pivotLowConfirmed: bool = not na(pivotLow)

    if pivotLowConfirmed and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='pivot low entry')

    if pivotHighConfirmed and strategy.position_size > 0:
        strategy.close('L', comment='pivot high exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
