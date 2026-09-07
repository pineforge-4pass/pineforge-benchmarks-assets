"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate 07 - MACD > sig continuous", shorttitle="TAI_07_MACDGTSIG", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    macd, sig, _hist = ta.macd(close, 12, 26, 9)
    cond: bool = macd > sig

    if cond:
        strategy.entry('L', strategy.long, comment='macd > sig')
    else:
        strategy.close('L', comment='macd <= sig')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
