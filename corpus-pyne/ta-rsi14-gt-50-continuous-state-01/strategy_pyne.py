"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate 06 - RSI(14) > 50 continuous", shorttitle="TAI_06_RSIGT50", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rsi = ta.rsi(close, 14)
    cond: bool = rsi > 50.0

    if cond:
        strategy.entry('L', strategy.long, comment='rsi > 50')
    else:
        strategy.close('L', comment='rsi <= 50')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
