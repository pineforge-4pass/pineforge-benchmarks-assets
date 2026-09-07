"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, minute, script, strategy, syminfo


@script.strategy("PF probe 75 - stop after flat", shorttitle="PF_P75_AFTERFLAT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    firstWindow = hour == 2 and minute <= 45 and (strategy.position_size == 0)
    secondWindow = hour == 8 and minute <= 45 and (strategy.position_size == 0)

    if firstWindow:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='first window stop')

    if hour == 6 and minute == 15 and (strategy.position_size > 0):
        strategy.close('LE', comment='first close')

    if secondWindow:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='second window stop')

    if hour == 12 and minute == 15 and (strategy.position_size > 0):
        strategy.close('LE', comment='second close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
