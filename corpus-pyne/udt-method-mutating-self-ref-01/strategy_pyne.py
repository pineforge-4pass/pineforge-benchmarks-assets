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
class Streak:
    count: int = 0
    reset_count: int = 0


@script.strategy("PF UDT probe 02 - mutating self", shorttitle="UDT_p02_MUT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def bump(self: Streak, advance: bool):
        if advance:
            self.count = self.count + 1
        else:
            if self.count > 0:
                self.reset_count = self.reset_count + 1
            self.count = 0
        return self.count

    streak: Persistent[Streak] = Streak(0, 0)

    greenBar: bool = close > open
    updated: int = bump(streak, greenBar)

    entryCond: bool = updated >= 3 and strategy.position_size == 0
    if entryCond:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if not greenBar and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
