"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, minute, script, strategy


@script.strategy("PF probe 60 - pyramiding close id", shorttitle="PF_P60_PYRCLOSE", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=3, process_orders_on_close=False)
def main():
    if hour == 0 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='lot 1')
    if hour == 0 and minute == 30 and (strategy.position_size > 0):
        strategy.entry('L', strategy.long, qty=1, comment='lot 2')

    if hour == 0 and minute == 45 and (strategy.position_size > 0):
        strategy.entry('L', strategy.long, qty=1, comment='lot 3')

    if hour == 1 and minute == 15 and (strategy.position_size > 0):
        strategy.close('L', comment='close all L')

    if hour == 12 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='short lot 1')

    if hour == 12 and minute == 30 and (strategy.position_size < 0):
        strategy.entry('S', strategy.short, qty=1, comment='short lot 2')

    if hour == 12 and minute == 45 and (strategy.position_size < 0):
        strategy.entry('S', strategy.short, qty=1, comment='short lot 3')

    if hour == 13 and minute == 15 and (strategy.position_size < 0):
        strategy.close('S', comment='close all S')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
