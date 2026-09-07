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
class Filter:
    rsi_min: float = 40.0
    rsi_max: float = 90.0
    atr_min: float = 0.0


@script.strategy("PF UDT probe 12 - ta param", shorttitle="UDT_p12_TAP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def confirms(self: Filter, rsi: float, ema: float, atr: float):
        rsiOk: bool = rsi >= self.rsi_min and rsi <= self.rsi_max
        emaOk: bool = close > ema
        atrOk: bool = atr > self.atr_min
        return rsiOk and emaOk and atrOk

    filt: Persistent[Filter] = Filter(40.0, 90.0, 0.0)

    rsiVal: float = ta.rsi(close, 14)
    emaVal: float = ta.ema(close, 21)
    atrVal: float = ta.atr(14)

    xUp: bool = ta.crossover(close, emaVal)
    xDown: bool = ta.crossunder(close, emaVal)

    entryCond: bool = xUp and confirms(filt, rsiVal, emaVal, atrVal)
    exitCond: bool = xDown

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
