"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, na, nz, script, strategy, ta, time, timeframe
from pynecore.types import Series


@script.strategy("PF na-chain probe 01 - deep history int na", shorttitle="NA_p01_INT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, max_bars_back=500)
def main():
    sessId: int = time(timeframe.period, '0930-1600', 'America/New_York')
    gatedSrc: Series[float] = na if na(sessId) else close

    deepRef: float = nz(gatedSrc[499], close)

    src: float = nz(gatedSrc, deepRef)
    rsiVal: float = ta.rsi(src, 14)

    sessOk: bool = not na(sessId)

    entryCond: bool = ta.crossover(rsiVal, 30.0) and sessOk
    exitCond: bool = ta.crossunder(rsiVal, 70.0)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
