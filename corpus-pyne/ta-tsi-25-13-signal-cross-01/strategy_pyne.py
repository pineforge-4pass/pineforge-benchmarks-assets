"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate - TSI(25,13) signal cross", shorttitle="TAI_TSI", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    tsi = ta.tsi(close, 25, 13)
    sig = ta.ema(tsi, 13)

    if ta.crossover(tsi, sig):
        strategy.entry('L', strategy.long, comment='tsi cross up')
    if ta.crossunder(tsi, sig):
        strategy.entry('S', strategy.short, comment='tsi cross dn')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
