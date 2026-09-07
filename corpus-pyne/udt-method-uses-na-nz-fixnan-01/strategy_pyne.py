"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, na, nz, script, strategy, ta
from pynecore.types import Persistent


@udt
class Sample:
    prev: float = na(float)
    ratio: float = na(float)


@script.strategy("PF UDT probe 10 - na nz in method", shorttitle="UDT_p10_NA", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def safeRatio(self: Sample, curr: float):
        p: float = nz(self.prev, curr)
        r: float = 1.0 if p == 0.0 else curr / p
        self.prev = curr
        self.ratio = r
        return 1.0 if na(self.ratio) else self.ratio

    s: Persistent[Sample] = Sample(na, na)

    r: float = safeRatio(s, close)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = ta.crossover(emaFast, emaSlow) and r > 1.0 and (not na(r))
    exitCond: bool = ta.crossunder(emaFast, emaSlow)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
