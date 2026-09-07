"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, na, script, strategy, ta
from pynecore.types import Persistent


@udt
class Counters:
    bull_run: int = 0
    bear_run: int = 0
    flat_run: int = 0


@script.strategy("PF UDT probe 06 - method in switch", shorttitle="UDT_p06_SW", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def bumpBull(self: Counters):
        self.bull_run = self.bull_run + 1
        self.bear_run = 0
        self.flat_run = 0
        return self.bull_run

    @method
    def bumpBear(self: Counters):
        self.bear_run = self.bear_run + 1
        self.bull_run = 0
        self.flat_run = 0
        return self.bear_run

    @method
    def bumpFlat(self: Counters):
        self.flat_run = self.flat_run + 1
        self.bull_run = 0
        self.bear_run = 0
        return self.flat_run

    c: Persistent[Counters] = Counters(0, 0, 0)

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)
    regime: str = 'bull' if emaFast > emaSlow * 1.001 else 'bear' if emaFast < emaSlow * 0.999 else 'flat'

    __block_result__ = na
    __switch__ = regime
    if __switch__ == "bull":
        __block_result__ = bumpBull(c)
    elif __switch__ == "bear":
        __block_result__ = bumpBear(c)
    else:
        __block_result__ = bumpFlat(c)
    active: int = __block_result__

    if regime == 'bull' and c.bull_run >= 3 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if regime == 'bear' and c.bear_run >= 3 and (strategy.position_size > 0):
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
