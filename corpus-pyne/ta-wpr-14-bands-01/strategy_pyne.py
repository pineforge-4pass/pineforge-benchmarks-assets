"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import script, strategy, ta


@script.strategy("PF TA isolate - WPR(14) bands", shorttitle="TAI_WPR", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    w = ta.wpr(14)
    if ta.crossover(w, -80.0):
        strategy.entry('L', strategy.long, comment='wpr cross up -80')
    if ta.crossunder(w, -20.0):
        strategy.entry('S', strategy.short, comment='wpr cross dn -20')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
