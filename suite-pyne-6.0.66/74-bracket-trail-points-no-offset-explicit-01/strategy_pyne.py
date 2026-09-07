"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, hour, minute, script, strategy


@script.strategy("PF probe 89 - trail_points 8 + far stop/limit", shorttitle="PF_P89_TRAIL8", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    trailTicks: int = 8
    if hour == 8 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=close * 0.95, limit=close * 1.05, trail_points=trailTicks, comment='trail8 + far stop/limit')

    if hour == 20 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='entry short')
        strategy.exit('SX', 'S', stop=close * 1.05, limit=close * 0.95, trail_points=trailTicks, comment='trail8 + far stop/limit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
