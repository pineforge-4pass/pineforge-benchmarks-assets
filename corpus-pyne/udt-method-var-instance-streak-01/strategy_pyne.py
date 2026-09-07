"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, open, script, strategy
from pynecore.types import Persistent


@udt
class Counter:
    green_streak: int = 0
    red_streak: int = 0
    total_greens: int = 0
    total_reds: int = 0


@script.strategy("PF UDT probe 16 - var instance streak", shorttitle="UDT_p16_VAR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def observe(self: Counter, isGreen: bool):
        if isGreen:
            self.green_streak = self.green_streak + 1
            self.red_streak = 0
            self.total_greens = self.total_greens + 1
        else:
            self.red_streak = self.red_streak + 1
            self.green_streak = 0
            self.total_reds = self.total_reds + 1
        return self.green_streak

    c: Persistent[Counter] = Counter(0, 0, 0, 0)

    isGreen: bool = close > open
    gs: int = observe(c, isGreen)

    if gs >= 4 and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if c.red_streak >= 1 and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
