"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, dayofweek, hour, matrix, na, script, strategy, ta, time
from pynecore.types import Matrix, Persistent


@script.strategy("PF TA isolate 11 - mask only no transpose", shorttitle="TAI_11_MASK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    mask: Persistent[Matrix[bool]] = matrix.new(24, 7, False)
    rsiVal = ta.rsi(close, 14)
    h: int = hour(time)
    d: int = dayofweek(time) - 1

    if not na(rsiVal) and rsiVal > 60.0 and (h >= 0) and (h < 24) and (d >= 0) and (d < 7):
        matrix.set(mask, h, d, True)

    sample: bool = matrix.get(mask, h if h < 24 else 0, d if d >= 0 and d < 7 else 0)
    hotCount: int = 0
    for i in pine_range(0, 23):
        for j in pine_range(0, 6):
            if matrix.get(mask, i, j):
                hotCount += 1

    entryCond: bool = hotCount >= 6 and rsiVal > 55.0 and sample
    exitCond: bool = not na(rsiVal) and rsiVal < 45.0

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
