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
class Cfg:
    factor: float = 1.0


@script.strategy("PF UDT probe 04 - default param", shorttitle="UDT_p04_DEF", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def threshold(self: Cfg, mult: float = 1.0, base: float = 0.0):
        return base + self.factor * mult

    cfg: Persistent[Cfg] = Cfg(1.5)

    rsiVal = ta.rsi(close, 14)
    atrVal = ta.atr(14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    t0: float = threshold(cfg)
    t1: float = threshold(cfg, atrVal)
    t2: float = threshold(cfg, mult=2.0, base=rsiVal)

    trigger: float = t0 + t1 + t2

    entryCond: bool = ta.crossover(emaFast, emaSlow) and trigger > 80.0 and (t1 > t0)
    exitCond: bool = ta.crossunder(emaFast, emaSlow)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
