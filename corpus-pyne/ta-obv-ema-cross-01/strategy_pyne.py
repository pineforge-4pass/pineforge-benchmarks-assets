"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import script, strategy, ta


@script.strategy("PF TA isolate - OBV EMA(21) cross", shorttitle="TAI_OBV", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    obv = ta.obv
    sig = ta.ema(obv, 21)

    if ta.crossover(obv, sig):
        strategy.entry('L', strategy.long, comment='obv cross up')
    if ta.crossunder(obv, sig):
        strategy.entry('S', strategy.short, comment='obv cross dn')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
