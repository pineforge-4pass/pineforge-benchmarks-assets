"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, na, script, strategy, ta


@script.strategy("PF TA isolate 09 - RSI>60 entry, RSI<45 exit", shorttitle="TAI_09_RSI60_45", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    entryCond: bool = not na(rsiVal) and rsiVal > 55.0
    exitCond: bool = not na(rsiVal) and rsiVal < 45.0

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
