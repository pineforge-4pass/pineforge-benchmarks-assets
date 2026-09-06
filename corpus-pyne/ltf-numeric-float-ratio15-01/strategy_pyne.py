"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import array, close, math, request, script, strategy, syminfo, ta


@script.strategy("PF lower-tf probe 01 - float ratio15", shorttitle="LTF_p01_F15", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    ltfCloses = request.security_lower_tf(syminfo.tickerid, '1', close)
    ltfSum: float = 0.0
    if array.size(ltfCloses) > 0:
        for i in pine_range(0, array.size(ltfCloses) - 1):
            ltfSum = ltfSum + array.get(ltfCloses, i)

    drift: float = ltfSum - 15.0 * close

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = ta.crossover(emaFast, emaSlow) and math.abs(drift) > close * 0.001
    exitCond: bool = ta.crossunder(emaFast, emaSlow)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='ltf-entry')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='ltf-exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
