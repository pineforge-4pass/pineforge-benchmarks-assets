"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, minute, script, strategy


@script.strategy("PF probe 70 - exit close same pass", shorttitle="PF_P70_EXITCLOSE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 0 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='long')
    if hour == 0 and minute == 45 and (strategy.position_size > 0):
        entry = strategy.position_avg_price
        strategy.exit('X', 'L', limit=entry * 1.02, stop=entry * 0.98, comment='exit first')
        strategy.close('L', comment='close second')

    if hour == 6 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L2', strategy.long, qty=1, comment='long2')

    if hour == 6 and minute == 45 and (strategy.position_size > 0):
        entry = strategy.position_avg_price
        strategy.close('L2', comment='close first')
        strategy.exit('X2', 'L2', limit=entry * 1.02, stop=entry * 0.98, comment='exit second')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
