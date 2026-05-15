"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, hour, minute, script, strategy


@script.strategy("PF probe 90 - narrow stop/limit + trail8", shorttitle="PF_P90_NARROW", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    trailTicks: int = 8
    stopDist: float = 10.0
    limitDist: float = 20.0

    if hour == 8 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        strategy.exit('LX', 'L', stop=close - stopDist, limit=close + limitDist, trail_points=trailTicks, comment='narrow stop/limit + trail8')

    if hour == 20 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='entry short')
        strategy.exit('SX', 'S', stop=close + stopDist, limit=close - limitDist, trail_points=trailTicks, comment='narrow stop/limit + trail8')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
