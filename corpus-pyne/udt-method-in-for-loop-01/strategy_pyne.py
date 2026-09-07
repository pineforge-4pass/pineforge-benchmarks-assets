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
from pynecore.lib import close, script, strategy, ta
from pynecore.types import Persistent


@udt
class Acc:
    total: float = 0.0
    n: int = 0


@script.strategy("PF UDT probe 07 - method in for", shorttitle="UDT_p07_FOR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def add(self: Acc, v: float):
        self.total = self.total + v
        self.n = self.n + 1
        return self.total

    @method
    def mean(self: Acc):
        return self.total / cast_float(self.n) if self.n > 0 else 0.0

    @method
    def reset(self: Acc):
        self.total = 0.0
        self.n = 0
        return 0

    acc: Persistent[Acc] = Acc(0.0, 0)

    _r: int = reset(acc)
    for i in pine_range(0, 4):
        add(acc, close[i])

    avg5: float = mean(acc)
    emaSlow = ta.ema(close, 21)

    if avg5 > emaSlow and ta.crossover(close, emaSlow) and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(close, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
