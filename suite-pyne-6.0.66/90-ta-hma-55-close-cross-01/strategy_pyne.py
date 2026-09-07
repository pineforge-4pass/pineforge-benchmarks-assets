"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, script, strategy, ta


@script.strategy("PF TA isolate 04 - close x HMA(55)", shorttitle="TAI_04_HMA55", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    h = ta.hma(close, 55)
    if ta.crossover(close, h):
        strategy.entry('L', strategy.long, comment='close cross up HMA55')
    if ta.crossunder(close, h):
        strategy.entry('S', strategy.short, comment='close cross dn HMA55')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
