"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import array, close, na, script, strategy, ta
from pynecore.types import NA, Persistent


@udt
class Sample:
    price: float = na(float)
    rsi: float = na(float)


@script.strategy("PF UDT probe 19 - array of UDT method", shorttitle="UDT_p19_AUDT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def score(self: Sample):
        __block_result__ = na
        if na(self.price) or na(self.rsi):
            __block_result__ = 0.0
        else:
            __block_result__ = (self.rsi - 50.0) * 0.1
        return __block_result__

    window: Persistent[list[Sample]] = array.new(0, NA(Sample))

    rsiVal: float = ta.rsi(close, 14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    current: Sample = Sample(close, rsiVal)
    array.push(window, current)
    if array.size(window) > 5:
        array.shift(window)

    total: float = 0.0
    len: int = array.size(window)
    for i in pine_range(0, len - 1):
        s: Sample = array.get(window, i)
        total = total + score(s)

    avgScore: float = total / cast_float(len) if len > 0 else 0.0

    latestScore: float = 0.0
    if len > 0:
        newest: Sample = array.get(window, len - 1)
        latestScore = score(newest)

    entryCond: bool = ta.crossover(emaFast, emaSlow) and latestScore > 0.0 and (avgScore > -0.5)
    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
