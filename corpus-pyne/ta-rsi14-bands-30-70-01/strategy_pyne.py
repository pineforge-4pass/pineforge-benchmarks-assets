"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate 02 - RSI(14) bands 30/70", shorttitle="TAI_02_RSI3070", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rsi = ta.rsi(close, 14)
    if ta.crossover(rsi, 30.0):
        strategy.entry('L', strategy.long, comment='rsi cross up 30')
    if ta.crossunder(rsi, 70.0):
        strategy.entry('S', strategy.short, comment='rsi cross dn 70')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
