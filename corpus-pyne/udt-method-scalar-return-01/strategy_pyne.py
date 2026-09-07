"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, script, strategy, ta
from pynecore.types import Persistent


@udt
class Box__ren__:
    k: float = 1.0
    bias: float = 50.0


@script.strategy("PF UDT probe 01 - scalar return", shorttitle="UDT_p01_SCAL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def score(self: Box__ren__):
        return self.k * (self.bias - 50.0)

    b: Persistent[Box__ren__] = Box__ren__(1.0, 50.0)

    rsiVal = ta.rsi(close, 14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    b.bias = rsiVal

    entryCond: bool = ta.crossover(emaFast, emaSlow) and score(b) > 5.0
    exitCond: bool = ta.crossunder(emaFast, emaSlow)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
