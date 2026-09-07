"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 76 - dual side no cancel", shorttitle="PF_P76_DUALNOCANCEL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    longWindow = hour == 2 and minute <= 45 and (strategy.position_size == 0)
    shortWindow = hour == 14 and minute <= 45 and (strategy.position_size == 0)

    if longWindow:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='dual long stop')

    if shortWindow:
        strategy.entry('SE', strategy.short, stop=low - syminfo.mintick, comment='dual short stop')

    if strategy.position_size > 0 and hour == 6 and (minute == 15):
        strategy.close('LE', comment='long close')

    if strategy.position_size < 0 and hour == 18 and (minute == 15):
        strategy.close('SE', comment='short close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
