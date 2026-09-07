"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, na, script, strategy, ta


@udt
class Sample:
    price: float = na(float)
    rsi: float = na(float)
    weight: float = 1.0


@script.strategy("PF UDT probe 20 - udt from user func", shorttitle="UDT_p20_UFR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def score(self: Sample):
        __block_result__ = na
        if na(self.price) or na(self.rsi):
            __block_result__ = 0.0
        else:
            __block_result__ = (self.rsi - 50.0) * 0.1 * self.weight
        return __block_result__

    def build_sample(price: float, rsi: float, weight: float):
        return Sample(price, rsi, weight)

    rsiVal: float = ta.rsi(close, 14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    s: Sample = build_sample(close, rsiVal, 1.0)
    sc: float = score(s)

    if ta.crossover(emaFast, emaSlow) and sc > 1.0 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
