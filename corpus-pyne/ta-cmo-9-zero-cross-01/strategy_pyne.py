"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate - CMO(9) zero cross", shorttitle="TAI_CMO", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    cmo = ta.cmo(close, 9)
    if ta.crossover(cmo, 0):
        strategy.entry('L', strategy.long, comment='cmo cross up 0')
    if ta.crossunder(cmo, 0):
        strategy.entry('S', strategy.short, comment='cmo cross dn 0')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
