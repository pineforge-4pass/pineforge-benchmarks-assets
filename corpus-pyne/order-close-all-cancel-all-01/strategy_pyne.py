"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, minute, script, strategy


@script.strategy("PF TV golden 43 - cancel all close all", shorttitle="PF_G43_ALL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=2, process_orders_on_close=False)
def main():
    if hour == 4 and minute == 15:
        strategy.entry('PENDING_L', strategy.long, qty=1, limit=close * 0.8, comment='pending low')
        strategy.entry('PENDING_S', strategy.short, qty=1, limit=close * 1.2, comment='pending high')

    if hour == 4 and minute == 30:
        strategy.cancel_all()

    if hour == 5 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('A', strategy.long, qty=1, comment='first')

    if hour == 5 and minute == 45 and (strategy.position_size > 0):
        strategy.entry('B', strategy.long, qty=1, comment='second')

    if hour == 6 and minute == 15 and (strategy.position_size != 0):
        strategy.close_all(comment='global flat', immediately=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
