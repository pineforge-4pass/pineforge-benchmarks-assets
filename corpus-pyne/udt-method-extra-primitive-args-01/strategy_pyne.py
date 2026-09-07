"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_float
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, script, strategy, ta
from pynecore.types import Persistent


@udt
class Cfg:
    base: float = 100.0
    bias: float = 0.0


@script.strategy("PF UDT probe 03 - extra args", shorttitle="UDT_p03_ARGS", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def offset(self: Cfg, n: int, mult: float, flip: bool):
        sign: int = -1 if flip else 1
        return self.base + mult * cast_float(n) * cast_float(sign) + self.bias

    cfg: Persistent[Cfg] = Cfg(0.0, 0.0)
    cfg.base = close

    upOff: float = offset(cfg, 5, 0.1, False)
    downOff: float = offset(cfg, n=5, mult=0.1, flip=True)

    if ta.crossover(close, ta.sma(close, 20)) and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', limit=upOff, stop=downOff, comment='bracket long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
