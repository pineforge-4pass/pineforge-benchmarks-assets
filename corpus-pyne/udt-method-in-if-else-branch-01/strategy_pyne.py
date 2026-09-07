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
class Regime:
    bull: int = 0
    bear: int = 0
    flat: int = 0


@script.strategy("PF UDT probe 05 - method in if", shorttitle="UDT_p05_IF", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def tag(self: Regime, bucket: int):
        if bucket == 1:
            self.bull = self.bull + 1
            self.bear = 0
            self.flat = 0
        elif bucket == -1:
            self.bear = self.bear + 1
            self.bull = 0
            self.flat = 0
        else:
            self.flat = self.flat + 1
            self.bull = 0
            self.bear = 0
        return self.bull

    regime: Persistent[Regime] = Regime(0, 0, 0)

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    bullStreak: int = na(int)
    if emaFast > emaSlow * 1.001:
        bullStreak = tag(regime, 1)
    elif emaFast < emaSlow * 0.999:
        _ignored: int = tag(regime, -1)
        bullStreak = regime.bull
    else:
        _ignored: int = tag(regime, 0)
        bullStreak = regime.bull

    if not na(bullStreak) and bullStreak >= 3 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if regime.bear >= 3 and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
