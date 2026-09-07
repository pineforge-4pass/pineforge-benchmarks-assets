"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import script, strategy, ta


@script.strategy("PF TA isolate - NVI/PVI vs EMA255 cross", shorttitle="TAI_NVIPVI", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    pvi = ta.pvi
    nvi = ta.nvi
    pviEma = ta.ema(pvi, 255)
    nviEma = ta.ema(nvi, 255)

    if ta.crossover(pvi, pviEma):
        strategy.entry('L', strategy.long, comment='pvi cross up')
    if ta.crossunder(nvi, nviEma):
        strategy.entry('S', strategy.short, comment='nvi cross dn')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
