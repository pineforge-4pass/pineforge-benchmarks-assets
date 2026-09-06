"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, minute, script, strategy, ta


@script.strategy("PF probe 91 - atr trail fixed entry", shorttitle="PF_P91_ATRTRAIL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    atrLen: int = 14
    atrMult: float = 1.2
    atr = ta.atr(atrLen)

    if hour == 8 and minute == 0 and (strategy.position_size == 0):
        longStop = close - atr * atrMult
        longLimit = close + (close - longStop) * 2
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=longStop, limit=longLimit, trail_points=atr, comment='atr trail long')

    if hour == 20 and minute == 0 and (strategy.position_size == 0):
        shortStop = close + atr * atrMult
        shortLimit = close - (shortStop - close) * 2
        strategy.entry('S', strategy.short, qty=1, comment='entry short')
        strategy.exit('SX', 'S', stop=shortStop, limit=shortLimit, trail_points=atr, comment='atr trail short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
