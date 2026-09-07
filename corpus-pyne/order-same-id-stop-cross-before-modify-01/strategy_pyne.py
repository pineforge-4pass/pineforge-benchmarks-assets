"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 62 - stop cross before modify", shorttitle="PF_P62_STOPCROSS", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    longFirst = hour == 3 and minute == 15 and (strategy.position_size == 0)
    longModify = hour == 3 and minute == 30 and (strategy.position_size == 0)
    shortFirst = hour == 15 and minute == 15 and (strategy.position_size == 0)
    shortModify = hour == 15 and minute == 30 and (strategy.position_size == 0)

    if longFirst:
        strategy.entry('LE', strategy.long, stop=close, comment='touchable long stop')

    if longModify:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='modified long stop')

    if shortFirst:
        strategy.entry('SE', strategy.short, stop=close, comment='touchable short stop')

    if shortModify:
        strategy.entry('SE', strategy.short, stop=low - syminfo.mintick, comment='modified short stop')

    if strategy.position_size > 0 and hour == 6 and (minute == 15):
        strategy.close('LE', comment='long close')

    if strategy.position_size < 0 and hour == 18 and (minute == 15):
        strategy.close('SE', comment='short close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
