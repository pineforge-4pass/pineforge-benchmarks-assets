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
class Bracket:
    stop_mult: float = 1.5
    limit_mult: float = 3.0
    base_qty: float = 1.0


@script.strategy("PF UDT probe 17 - tuple return", shorttitle="UDT_p17_TUP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def levels(self: Bracket, price: float, atr: float, isLong: bool):
        stopPx: float = price - self.stop_mult * atr if isLong else price + self.stop_mult * atr
        limitPx: float = price + self.limit_mult * atr if isLong else price - self.limit_mult * atr
        return (stopPx, limitPx, self.base_qty)

    br: Persistent[Bracket] = Bracket(1.5, 3.0, 1.0)

    atrVal: float = ta.atr(14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ta.crossover(emaFast, emaSlow) and strategy.position_size == 0:
        stopL, limitL, qtyL = levels(br, close, atrVal, True)
        strategy.entry('L', strategy.long, qty=qtyL, comment='entry long')
        strategy.exit('LX', 'L', stop=stopL, limit=limitL, comment='bracket long')

    if ta.crossunder(emaFast, emaSlow) and strategy.position_size == 0:
        stopS, limitS, qtyS = levels(br, close, atrVal, False)
        strategy.entry('S', strategy.short, qty=qtyS, comment='entry short')
        strategy.exit('SX', 'S', stop=stopS, limit=limitS, comment='bracket short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
