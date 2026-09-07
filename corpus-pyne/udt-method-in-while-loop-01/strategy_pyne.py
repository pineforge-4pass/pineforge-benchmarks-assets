"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, open, script, strategy, ta
from pynecore.types import Persistent


@udt
class Ramp:
    counter: int = 0
    green_count: int = 0


@script.strategy("PF UDT probe 08 - method in while", shorttitle="UDT_p08_WHL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def tick(self: Ramp):
        idx: int = self.counter - 1
        greenBar: bool = idx >= 0 and close[idx] > open[idx]
        if greenBar:
            self.green_count = self.green_count + 1
        self.counter = self.counter - 1
        return self.counter

    ramp: Persistent[Ramp] = Ramp(0, 0)

    ramp.counter = 10
    ramp.green_count = 0
    safety: int = 0
    while ramp.counter > 0 and safety < 12:
        _c: int = tick(ramp)
        safety = safety + 1

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ramp.green_count >= 7 and ta.crossover(emaFast, emaSlow) and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
