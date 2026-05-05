"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, math, nz, plot, script, strategy
from pynecore.types import PersistentSeries, Series


@script.strategy("Adaptive MA Function", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    len=input.int(14, "Length", minval=2),
    fastLen=input.int(2, "Fast Alpha Period", minval=1),
    slowLen=input.int(30, "Slow Alpha Period", minval=5)
):

    def calcEfficiencyRatio(src: Series, length):
        direction = math.abs(src - src[length])
        volatilitySum = math.sum(math.abs(src - src[1]), length)
        er = direction / volatilitySum if volatilitySum != 0 else 0
        return er

    er = calcEfficiencyRatio(close, len)

    fastAlpha = 2.0 / (fastLen + 1)
    slowAlpha = 2.0 / (slowLen + 1)

    sc = math.pow(er * (fastAlpha - slowAlpha) + slowAlpha, 2)

    kama: PersistentSeries[float] = close
    kama = nz(kama[1]) + sc * (close - nz(kama[1]))

    kamaUp: Series = kama > kama[1]
    kamaDown: Series = kama < kama[1]

    longCond = kamaUp and (not kamaUp[1])
    shortCond = kamaDown and (not kamaDown[1])

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    plot(kama, 'KAMA', color=color.green if kamaUp else color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
