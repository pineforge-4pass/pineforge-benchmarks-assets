"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import array, close, open, request, script, strategy, syminfo, ta


@script.strategy("PF lower-tf probe 02 - bool array", shorttitle="LTF_p02_BOOL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    ltfBullArr = request.security_lower_tf(syminfo.tickerid, '1', close > open)
    bullCount: int = 0
    if array.size(ltfBullArr) > 0:
        for i in pine_range(0, array.size(ltfBullArr) - 1):
            if array.get(ltfBullArr, i):
                bullCount = bullCount + 1

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = bullCount >= 9 and emaFast > emaSlow
    exitCond: bool = bullCount <= 6 or emaFast < emaSlow

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='bull-majority')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='bull-broken')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
