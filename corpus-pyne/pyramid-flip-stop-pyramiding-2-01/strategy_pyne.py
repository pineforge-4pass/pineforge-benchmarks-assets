"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 93 - flip stop pyramiding 2", shorttitle="PF_P93_PYR2", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=2, process_orders_on_close=False)
def main():
    if hour == 0 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='open long')
    if hour == 0 and minute == 45 and (strategy.position_size > 0):
        strategy.entry('S', strategy.short, qty=1, stop=low - syminfo.mintick, comment='opposite stop first')
        strategy.close('L', comment='close long second')

    if hour == 6 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L2', strategy.long, qty=1, comment='open long2')

    if hour == 6 and minute == 45 and (strategy.position_size > 0):
        strategy.close('L2', comment='close long first')
        strategy.entry('S2', strategy.short, qty=1, stop=low - syminfo.mintick, comment='opposite stop second')

    if hour == 12 and minute == 15 and (strategy.position_size < 0):
        strategy.close_all(comment='cleanup short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
