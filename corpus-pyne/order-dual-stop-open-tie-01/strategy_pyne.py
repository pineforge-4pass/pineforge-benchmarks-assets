"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, minute, script, strategy


@script.strategy("PF probe 83 - dual stop open tie", shorttitle="PF_P83_OPENTIE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 4 and minute == 45 and (strategy.position_size == 0):
        strategy.entry('LE', strategy.long, stop=close, comment='long stop at close')
        strategy.entry('SE', strategy.short, stop=close, comment='short stop at close')

    if strategy.position_size != 0 and hour == 8 and (minute == 15):
        strategy.close_all(comment='flat after open tie')

    if hour == 16 and minute == 45 and (strategy.position_size == 0):
        strategy.entry('SE2', strategy.short, stop=close, comment='short first at close')
        strategy.entry('LE2', strategy.long, stop=close, comment='long second at close')

    if strategy.position_size != 0 and hour == 20 and (minute == 15):
        strategy.close_all(comment='flat after reverse tie')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
