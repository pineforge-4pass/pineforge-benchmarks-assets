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
class Stat:
    last: float = na(float)
    mean: float = na(float)
    sd: float = na(float)
    n: int = 0


@script.strategy("PF UDT probe 21 - windowed method chain", shorttitle="UDT_p21_WMC", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def feed(self: Stat, v: float, m: float, s: float):
        self.last = v
        self.mean = m
        self.sd = s
        self.n = self.n + 1
        return self.n

    @method
    def zscore(self: Stat):
        return 0.0 if na(self.sd) or self.sd == 0.0 else (self.last - self.mean) / self.sd

    @method
    def refreshAndScore(self: Stat, v: float, m: float, s: float):
        _: int = feed(self, v, m, s)
        return zscore(self)

    stat: Persistent[Stat] = Stat(na, na, na, 0)

    statLen: int = 50
    smaVal: float = ta.sma(close, statLen)
    sdVal: float = ta.stdev(close, statLen)

    z: float = refreshAndScore(stat, close, smaVal, sdVal)

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ta.crossover(emaFast, emaSlow) and z > 1.0 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
