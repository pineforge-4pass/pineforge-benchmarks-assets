"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, minute, script, strategy


@script.strategy("PF probe 59 - market close fill basis", shorttitle="PF_P59_CLOSE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 3 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='long')
    if hour == 5 and minute == 15 and (strategy.position_size > 0):
        strategy.close('L', comment='market close long')

    if hour == 15 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='short')

    if hour == 17 and minute == 15 and (strategy.position_size < 0):
        strategy.close('S', comment='market close short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
