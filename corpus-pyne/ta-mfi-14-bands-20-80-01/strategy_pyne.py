"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hlc3, script, strategy, ta


@script.strategy("PF TA isolate - MFI(14) bands 20/80", shorttitle="TAI_MFI", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    mfi = ta.mfi(hlc3, 14)
    if ta.crossover(mfi, 20):
        strategy.entry('L', strategy.long, comment='mfi x up 20')
    if ta.crossunder(mfi, 80):
        strategy.entry('S', strategy.short, comment='mfi x dn 80')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
