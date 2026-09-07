"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF TA isolate 08 - RSI>50 AND MACD>sig", shorttitle="TAI_08_AND", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    macdLine, sigLine, _ = ta.macd(close, 12, 26, 9)

    longCond: bool = True
    if rsiVal <= 50:
        longCond = False
    if macdLine <= sigLine:
        longCond = False

    if longCond:
        strategy.entry('Long', strategy.long, comment='Long')
    else:
        strategy.close('Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
