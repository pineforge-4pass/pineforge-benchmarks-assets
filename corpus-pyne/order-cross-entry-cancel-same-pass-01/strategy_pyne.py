"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 69 - entry cancel same pass", shorttitle="PF_P69_ENTCANCEL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 2 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, stop=high + syminfo.mintick, comment='entry first cancel second')
        strategy.cancel('L')

    if hour == 4 and minute == 15 and (strategy.position_size == 0):
        strategy.cancel('L2')
        strategy.entry('L2', strategy.long, stop=high + syminfo.mintick, comment='cancel first entry second')

    if hour == 6 and minute == 15 and (strategy.position_size > 0):
        strategy.close_all(comment='long cleanup')

    if hour == 14 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, stop=low - syminfo.mintick, comment='short entry first cancel second')
        strategy.cancel('S')

    if hour == 16 and minute == 15 and (strategy.position_size == 0):
        strategy.cancel('S2')
        strategy.entry('S2', strategy.short, stop=low - syminfo.mintick, comment='short cancel first entry second')

    if hour == 18 and minute == 15 and (strategy.position_size < 0):
        strategy.close_all(comment='short cleanup')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
