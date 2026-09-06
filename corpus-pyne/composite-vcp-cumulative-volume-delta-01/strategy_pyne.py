"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, low, math, open, script, strategy, volume
from pynecore.types import Series


@script.strategy("VCP probe 05 - cumulative vol delta", shorttitle="VCP_p05", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    buyVolume: float = volume if close > open else volume * (close - low) / (high - low + 0.0001)
    sellVolume: float = volume if close < open else volume * (high - close) / (high - low + 0.0001)
    volumeDelta: float = buyVolume - sellVolume

    cumDelta: Series[float] = math.sum(volumeDelta, 10)

    crossUp: bool = cumDelta > 0 and cumDelta[1] <= 0
    crossDown: bool = cumDelta < 0 and cumDelta[1] >= 0

    if crossUp and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='cumDelta cross-up')

    if crossDown and strategy.position_size > 0:
        strategy.close('L', comment='cumDelta cross-down exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
