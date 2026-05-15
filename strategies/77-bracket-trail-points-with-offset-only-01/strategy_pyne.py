"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, input, minute, script, strategy


@script.strategy("PF probe 51 - trail points offset", shorttitle="PF_P51_TRAIL", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    trailPts=input.float(80.0, "Trail Points", minval=1.0),
    trailOff=input.float(40.0, "Trail Offset", minval=1.0)
):
    if hour == 9 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='trail long')

    if hour == 15 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='trail short')

    if strategy.position_size > 0:
        strategy.exit('LX', 'L', trail_points=trailPts, trail_offset=trailOff, comment='trail long')

    if strategy.position_size < 0:
        strategy.exit('SX', 'S', trail_points=trailPts, trail_offset=trailOff, comment='trail short')

    if strategy.position_size != 0 and hour == 23 and (minute == 45):
        strategy.close_all(comment='timeout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
