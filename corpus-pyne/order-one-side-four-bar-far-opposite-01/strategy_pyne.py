"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 79 - far opposite pending", shorttitle="PF_P79_FAROPP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    longWindow = hour == 2 and minute <= 45 and (strategy.position_size == 0)
    if hour == 2 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('SE', strategy.short, stop=low * 0.5, comment='far opposite short')

    if longWindow:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='four-bar long stop')

    if hour == 6 and minute == 15 and (strategy.position_size > 0):
        strategy.close('LE', comment='long close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
