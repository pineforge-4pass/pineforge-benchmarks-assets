"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate 05 - close x SMA(152)", shorttitle="TAI_05_SMA152", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    s = ta.sma(close, 152)
    if ta.crossover(close, s):
        strategy.entry('L', strategy.long, comment='close cross up SMA152')
    if ta.crossunder(close, s):
        strategy.entry('S', strategy.short, comment='close cross dn SMA152')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
