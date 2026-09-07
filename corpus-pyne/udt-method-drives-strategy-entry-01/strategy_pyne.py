"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import bar_index, close, script, strategy, ta
from pynecore.types import Persistent


@udt
class Signal:
    last_long_bar: int = -1000
    last_short_bar: int = -1000
    debounce: int = 5


@script.strategy("PF UDT probe 14 - method drives entry", shorttitle="UDT_p14_ENT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def shouldEnterLong(self: Signal, cross: bool):
        spaced: bool = bar_index - self.last_long_bar >= self.debounce
        ok: bool = cross and spaced
        if ok:
            self.last_long_bar = bar_index
        return ok

    @method
    def shouldEnterShort(self: Signal, cross: bool):
        spaced: bool = bar_index - self.last_short_bar >= self.debounce
        ok: bool = cross and spaced
        if ok:
            self.last_short_bar = bar_index
        return ok

    sig: Persistent[Signal] = Signal(-1000, -1000, 5)

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)
    xUp: bool = ta.crossover(emaFast, emaSlow)
    xDown: bool = ta.crossunder(emaFast, emaSlow)

    if shouldEnterLong(sig, xUp):
        if strategy.position_size < 0:
            strategy.close('S', comment='flip to long')
        strategy.entry('L', strategy.long, qty=1, comment='entry long')

    if shouldEnterShort(sig, xDown):
        if strategy.position_size > 0:
            strategy.close('L', comment='flip to short')
        strategy.entry('S', strategy.short, qty=1, comment='entry short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
