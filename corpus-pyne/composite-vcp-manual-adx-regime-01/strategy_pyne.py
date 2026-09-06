"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, low, math, na, script, strategy, ta
from pynecore.types import Series


@script.strategy("VCP probe 06 - adx regime", shorttitle="VCP_p06", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    atrVal: float = ta.atr(14)
    adxLen: int = 14
    upMove: float = ta.change(high)
    downMove: float = -ta.change(low)
    plusDM: float = na if na(upMove) else upMove if upMove > downMove and upMove > 0 else 0
    minusDM: float = na if na(downMove) else downMove if downMove > upMove and downMove > 0 else 0
    trueRange: float = ta.rma(ta.tr, adxLen)
    plusDI: float = 100 * ta.rma(plusDM, adxLen) / trueRange
    minusDI: float = 100 * ta.rma(minusDM, adxLen) / trueRange
    dx: float = 100 * math.abs(plusDI - minusDI) / (plusDI + minusDI)
    adxValue: float = ta.rma(dx, adxLen)

    isTrending: bool = adxValue > 25
    trend: int = 1 if plusDI > minusDI else -1
    volatility: float = atrVal / close * 100

    trendingBull: Series[bool] = isTrending and trend > 0
    regimeBullStart: bool = trendingBull and (not trendingBull[1])
    regimeBullEnd: bool = not trendingBull and trendingBull[1]

    if regimeBullStart and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='adx trending-bull start')

    if regimeBullEnd and strategy.position_size > 0:
        strategy.close('L', comment='adx trending-bull end exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
