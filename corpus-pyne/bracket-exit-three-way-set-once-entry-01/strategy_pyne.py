"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, minute, script, strategy


@script.strategy("PF probe 88 - 3-way exit set once", shorttitle="PF_P88_EX3SET", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    trailTicks: int = 20
    if hour == 8 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=close * 0.99, limit=close * 1.02, trail_points=trailTicks, comment='3-way set once')

    if hour == 20 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='entry short')
        strategy.exit('SX', 'S', stop=close * 1.01, limit=close * 0.98, trail_points=trailTicks, comment='3-way set once')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
