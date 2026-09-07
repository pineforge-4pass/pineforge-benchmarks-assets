"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, high, low, script, strategy, ta
from pynecore.types import Persistent


@udt
class Trend:
    lookback: int = 3


@script.strategy("PF UDT probe 11 - history in method", shorttitle="UDT_p11_HIST", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def changeRate(self: Trend):
        ref: float = close[self.lookback]
        return 0.0 if ref == 0.0 else (close - ref) / ref

    @method
    def swingRange(self: Trend):
        hi: float = high[self.lookback]
        lo: float = low[self.lookback]
        return hi - lo

    trend: Persistent[Trend] = Trend(3)

    r: float = changeRate(trend)
    swing: float = swingRange(trend)

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ta.crossover(emaFast, emaSlow) and r > 0.01 and (swing > 0) and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
