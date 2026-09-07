"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import array, close, script, strategy, ta


@script.strategy("PF TA isolate - pivot_point_levels R1/S1 break", shorttitle="TAI_PPL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    pivots = ta.pivot_point_levels('Traditional', True)
    P = array.get(pivots, 0)
    R1 = array.get(pivots, 1)
    S1 = array.get(pivots, 2)

    if ta.crossover(close, R1):
        strategy.entry('L', strategy.long, comment='close x> R1')
    if ta.crossunder(close, S1):
        strategy.entry('S', strategy.short, comment='close x< S1')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
