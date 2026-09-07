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
class Bracket:
    entry_px: float = na(float)
    entry_atr: float = na(float)
    stop_mult: float = 1.5
    limit_mult: float = 3.0


@script.strategy("PF UDT probe 15 - exit prices via method", shorttitle="UDT_p15_EXP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def stopPrice(self: Bracket):
        return self.entry_px - self.entry_atr * self.stop_mult

    @method
    def limitPrice(self: Bracket):
        return self.entry_px + self.entry_atr * self.limit_mult

    br: Persistent[Bracket] = Bracket(na, na, 1.5, 3.0)

    atrVal: float = ta.atr(14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ta.crossover(emaFast, emaSlow) and strategy.position_size == 0:
        br.entry_px = close
        br.entry_atr = atrVal
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=stopPrice(br), limit=limitPrice(br), comment='bracket from method')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
