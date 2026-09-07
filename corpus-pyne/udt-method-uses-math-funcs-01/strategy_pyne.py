"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, math, script, strategy, ta
from pynecore.types import Persistent


@udt
class Box__ren__:
    min_offset: float = 1.0
    max_offset: float = 50.0


@script.strategy("PF UDT probe 09 - math in method", shorttitle="UDT_p09_MATH", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def clampedStop(self: Box__ren__, price: float, atr: float):
        raw: float = math.abs(atr) * 1.5
        clamped: float = math.max(self.min_offset, math.min(self.max_offset, raw))
        return math.round(price - clamped)

    @method
    def clampedLimit(self: Box__ren__, price: float, atr: float):
        raw: float = math.sqrt(math.abs(atr)) * 5.0
        clamped: float = math.max(self.min_offset, math.min(self.max_offset, raw))
        return math.round(price + clamped)

    bx: Persistent[Box__ren__] = Box__ren__(1.0, 50.0)

    atrVal: float = ta.atr(14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ta.crossover(emaFast, emaSlow) and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=clampedStop(bx, close, atrVal), limit=clampedLimit(bx, close, atrVal), comment='bracket long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
