"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 58 - same id stop modify", shorttitle="PF_P58_MODSTOP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    longSetup = hour == 2 and minute <= 45 and (strategy.position_size == 0)
    shortSetup = hour == 14 and minute <= 45 and (strategy.position_size == 0)

    if longSetup:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='moving long stop')

    if shortSetup:
        strategy.entry('SE', strategy.short, stop=low - syminfo.mintick, comment='moving short stop')

    if strategy.position_size > 0 and hour == 6 and (minute == 15):
        strategy.close('LE', comment='long close')

    if strategy.position_size < 0 and hour == 18 and (minute == 15):
        strategy.close('SE', comment='short close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
